#!/usr/bin/env python3
"""Performance / engineering benchmark for the model zoo.

Measures the metrics deployment actually cares about — params, FLOPs (GMACs),
GPU & CPU latency, throughput (FPS), and peak VRAM — and writes
`reports/leaderboard_performance.csv`. Accuracy is only half the story; this is
the other half (the accuracy/latency Pareto front AV teams deploy against).

FLOPs are counted with a dependency-free forward-hook counter over conv/linear
layers (MACs), so no thop/fvcore needed.

    python scripts/run_perf_benchmark.py --size 512 --iters 50 \
        --models unet unetpp deeplabv3plus pspnet segformer
"""
import argparse
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from uavroadmark.models import get_model  # noqa: E402
from uavroadmark.report.leaderboard import count_params_millions  # noqa: E402


def count_flops(model, x):
    """Count multiply-accumulates via forward hooks (Conv2d/ConvTranspose2d/Linear)."""
    import torch.nn as nn
    total = [0]
    hooks = []

    def conv_hook(m, inp, out):
        oc, oh, ow = out.shape[1], out.shape[2], out.shape[3]
        kh, kw = m.kernel_size if isinstance(m.kernel_size, tuple) else (m.kernel_size,) * 2
        ic = m.in_channels // m.groups
        total[0] += oc * oh * ow * ic * kh * kw

    def lin_hook(m, inp, out):
        total[0] += m.in_features * m.out_features

    import torch
    for mod in model.modules():
        if isinstance(mod, (nn.Conv2d, nn.ConvTranspose2d)):
            hooks.append(mod.register_forward_hook(conv_hook))
        elif isinstance(mod, nn.Linear):
            hooks.append(mod.register_forward_hook(lin_hook))
    model.eval()  # eval mode: avoids BatchNorm batch-1 error (DeepLab ASPP pooling)
    with torch.no_grad():
        model(x)
    for h in hooks:
        h.remove()
    return total[0] / 1e9  # GMACs


def bench_latency(model, x, device, iters, warmup=10):
    import torch
    model.eval().to(device)
    x = x.to(device)
    with torch.no_grad():
        for _ in range(warmup):
            model(x)
        if device == "cuda":
            torch.cuda.synchronize()
            torch.cuda.reset_peak_memory_stats()
        t0 = time.perf_counter()
        for _ in range(iters):
            model(x)
        if device == "cuda":
            torch.cuda.synchronize()
        dt = (time.perf_counter() - t0) / iters
    vram = torch.cuda.max_memory_allocated() / 1e9 if device == "cuda" else 0.0
    return dt * 1000.0, 1.0 / dt, vram  # ms, fps, GB


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+",
                    default=["unet", "unetpp", "deeplabv3plus", "pspnet", "segformer"])
    ap.add_argument("--num-classes", type=int, default=25)
    ap.add_argument("--size", type=int, default=512)
    ap.add_argument("--iters", type=int, default=50)
    ap.add_argument("--out", default="reports/leaderboard_performance.csv")
    args = ap.parse_args()

    import pandas as pd
    import torch
    has_cuda = torch.cuda.is_available()
    x = torch.randn(1, 3, args.size, args.size)

    rows = []
    for name in args.models:
        enc = "mit_b0" if name == "segformer" else ("resnet50" if name in
              ("deeplabv3plus", "pspnet") else "resnet34")
        model = get_model(name, num_classes=args.num_classes, encoder=enc, pretrained=False)
        params = count_params_millions(model)
        gmacs = count_flops(model, x)
        row = {"model": name, "encoder": enc, "params_M": round(params, 2),
               "GFLOPs": round(gmacs * 2, 1), "GMACs": round(gmacs, 1),
               "input": f"{args.size}x{args.size}"}
        cpu_ms, cpu_fps, _ = bench_latency(model, x, "cpu", max(5, args.iters // 5))
        row.update({"cpu_latency_ms": round(cpu_ms, 1), "cpu_fps": round(cpu_fps, 1)})
        if has_cuda:
            g_ms, g_fps, vram = bench_latency(model, x, "cuda", args.iters)
            row.update({"gpu_latency_ms": round(g_ms, 2), "gpu_fps": round(g_fps, 1),
                        "gpu_vram_GB": round(vram, 2)})
            del model
            torch.cuda.empty_cache()
        rows.append(row)
        print(f"{name:14s} {row.get('params_M')}M  {row.get('GFLOPs')} GFLOPs  "
              f"GPU {row.get('gpu_latency_ms','-')}ms / {row.get('gpu_fps','-')}fps  "
              f"VRAM {row.get('gpu_vram_GB','-')}GB")

    df = pd.DataFrame(rows).sort_values("gpu_fps" if has_cuda else "cpu_fps",
                                        ascending=False)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    df.to_csv(args.out, index=False)
    print(f"\nWrote {args.out}")


if __name__ == "__main__":
    main()
