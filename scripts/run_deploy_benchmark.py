#!/usr/bin/env python3
"""Deployment benchmark: PyTorch vs ONNX Runtime (vs TensorRT, documented).

Exports a model to ONNX, verifies numerical parity against PyTorch, and compares
inference latency/throughput across backends. The TensorRT leg is documented (it
needs the TensorRT runtime, absent here) with the exact `trtexec` command.

    python scripts/run_deploy_benchmark.py --model unet --size 512 --iters 50 \
        --out reports/deployment
"""
import argparse
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from uavroadmark.models import get_model  # noqa: E402


def bench(fn, x, iters, warmup=5):
    for _ in range(warmup):
        fn(x)
    t0 = time.perf_counter()
    for _ in range(iters):
        fn(x)
    dt = (time.perf_counter() - t0) / iters
    return dt * 1000.0, 1.0 / dt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="unet")
    ap.add_argument("--num-classes", type=int, default=25)
    ap.add_argument("--size", type=int, default=512)
    ap.add_argument("--iters", type=int, default=50)
    ap.add_argument("--device", default="cpu", choices=["cpu", "cuda"])
    ap.add_argument("--out", default="reports/deployment")
    args = ap.parse_args()

    import torch
    os.makedirs(args.out, exist_ok=True)
    enc = "mit_b0" if args.model == "segformer" else \
          ("resnet50" if args.model in ("deeplabv3plus", "pspnet") else "resnet34")
    model = get_model(args.model, num_classes=args.num_classes, encoder=enc,
                      pretrained=False).eval()
    x = torch.randn(1, 3, args.size, args.size)

    results = {"model": args.model, "encoder": enc, "size": args.size,
               "device": args.device, "backends": {}}

    # --- PyTorch ---
    dev = args.device
    model.to(dev); xd = x.to(dev)
    with torch.no_grad():
        pt_ms, pt_fps = bench(lambda t: model(t), xd, args.iters)
        ref = model(xd).cpu().numpy()
    results["backends"]["pytorch"] = {"latency_ms": round(pt_ms, 2), "fps": round(pt_fps, 1)}
    print(f"PyTorch  {pt_ms:.2f} ms  {pt_fps:.1f} FPS")

    # --- ONNX export + ONNX Runtime ---
    onnx_path = os.path.join(args.out, f"{args.model}.onnx")
    torch.onnx.export(model.cpu(), x, onnx_path, opset_version=17,
                      input_names=["input"], output_names=["logits"],
                      dynamic_axes={"input": {0: "b", 2: "h", 3: "w"}})
    try:
        import onnxruntime as ort
        providers = (["CUDAExecutionProvider", "CPUExecutionProvider"]
                     if args.device == "cuda" else ["CPUExecutionProvider"])
        sess = ort.InferenceSession(onnx_path, providers=providers)
        xn = x.numpy()
        run = lambda t: sess.run(None, {"input": t})[0]
        ort_out = run(xn)
        parity = float(np.abs(ref - ort_out).max())
        ort_ms, ort_fps = bench(run, xn, args.iters)
        results["backends"]["onnxruntime"] = {
            "latency_ms": round(ort_ms, 2), "fps": round(ort_fps, 1),
            "max_abs_diff_vs_pytorch": parity,
            "speedup_vs_pytorch": round(pt_ms / ort_ms, 2)}
        print(f"ONNXRT   {ort_ms:.2f} ms  {ort_fps:.1f} FPS  "
              f"(parity max|Δ|={parity:.2e}, {pt_ms/ort_ms:.2f}x)")
    except Exception as e:  # noqa: BLE001
        results["backends"]["onnxruntime"] = {"error": str(e)}
        print("ONNXRT skipped:", e)

    # --- TensorRT (documented) ---
    results["backends"]["tensorrt"] = {
        "status": "not run (TensorRT runtime not installed in this environment)",
        "command": f"trtexec --onnx={onnx_path} --saveEngine={args.model}_fp16.engine --fp16",
        "note": "FP16/INT8 TensorRT typically gives 2-4x over ONNX-RT on Jetson."}

    with open(os.path.join(args.out, f"deploy_{args.model}.json"), "w") as f:
        json.dump(results, f, indent=2)
    print(f"Wrote {args.out}/deploy_{args.model}.json")


if __name__ == "__main__":
    main()
