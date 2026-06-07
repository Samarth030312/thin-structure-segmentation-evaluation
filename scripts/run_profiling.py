#!/usr/bin/env python3
"""Performance profiling: torch.profiler op breakdown + dataloader-throughput /
bottleneck analysis. Produces the evidence for reports/performance_profiling.md.

    python scripts/run_profiling.py --config configs/experiment/rlmd_unet_ce_dice.yaml \
        --out reports/profiling
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from uavroadmark.build import (build_loss_from_cfg, build_model_from_cfg,  # noqa: E402
                               build_datasets)
from uavroadmark.utils import load_config  # noqa: E402


def dataloader_throughput(cfg, workers_list=(0, 2, 6)):
    """Measure imgs/s for different num_workers to expose the data bottleneck."""
    from torch.utils.data import DataLoader
    train_ds, _ = build_datasets(cfg)
    out = {}
    for nw in workers_list:
        dl = DataLoader(train_ds, batch_size=cfg["train"].get("batch_size", 8),
                        shuffle=True, num_workers=nw, pin_memory=True)
        n, t0, seen = 0, time.perf_counter(), 0
        for batch in dl:
            seen += batch["image"].shape[0]; n += 1
            if n >= 20:
                break
        dt = time.perf_counter() - t0
        out[f"workers_{nw}"] = round(seen / dt, 1)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--out", default="reports/profiling")
    ap.add_argument("--steps", type=int, default=12)
    args = ap.parse_args()

    import torch
    from torch.profiler import ProfilerActivity, profile

    cfg = load_config(args.config)
    os.makedirs(args.out, exist_ok=True)
    device = "cuda" if torch.cuda.is_available() else "cpu"

    # 1) dataloader throughput vs workers (CPU pipeline bottleneck)
    dl_tp = dataloader_throughput(cfg)
    print("dataloader imgs/s:", dl_tp)

    # 2) op-level profile of a few train steps
    model = build_model_from_cfg(cfg).to(device)
    loss_fn = build_loss_from_cfg(cfg)
    opt = torch.optim.AdamW(model.parameters(), lr=1e-4)
    size = tuple(cfg["dataset"].get("image_size", [384, 384]))
    bs = cfg["train"].get("batch_size", 4)
    x = torch.randn(bs, 3, *size, device=device)
    y = torch.randint(0, cfg["dataset"]["num_classes"], (bs, *size), device=device)

    acts = [ProfilerActivity.CPU] + ([ProfilerActivity.CUDA] if device == "cuda" else [])
    model.train()
    with profile(activities=acts, record_shapes=True) as prof:
        for _ in range(args.steps):
            opt.zero_grad()
            loss = loss_fn(model(x), y)
            loss.backward()
            opt.step()
    sort_key = "cuda_time_total" if device == "cuda" else "cpu_time_total"
    table = prof.key_averages().table(sort_by=sort_key, row_limit=15)
    print(table)

    (open(os.path.join(args.out, "profiler_top_ops.txt"), "w")).write(table)
    json.dump({"device": device, "image_size": list(size), "batch_size": bs,
               "dataloader_imgs_per_s": dl_tp},
              open(os.path.join(args.out, "profiling_summary.json"), "w"), indent=2)
    print(f"Wrote {args.out}/profiler_top_ops.txt + profiling_summary.json")


if __name__ == "__main__":
    main()
