#!/usr/bin/env python3
"""Width-stratified study: evaluate trained models across controlled marking
widths to demonstrate the thin-structure gap and how the loss changes it.

For each checkpoint and each width_scale test set, we compute standard mIoU and
the thin-structure metrics, then plot metric-vs-width curves. This is the figure
that supports the paper's central claim.

    python scripts/run_width_study.py \
        --configs configs/experiment/abl_unet_ce_dice.yaml configs/experiment/abl_unet_core.yaml \
        --checkpoints outputs/abl_unet_ce_dice/best.pth outputs/abl_unet_core/best.pth \
        --labels CE+Dice CoRe \
        --series datasets/width_series --out reports/visualizations/width_study
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from uavroadmark.build import build_model_from_cfg  # noqa: E402
from uavroadmark.data import RoadMarkDataset, build_transforms  # noqa: E402
from uavroadmark.engine import evaluate_model  # noqa: E402
from uavroadmark.utils import load_config, seed_everything  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def width_tags(series_dir):
    tags = sorted([d for d in os.listdir(series_dir)
                   if d.startswith("width_")],
                  key=lambda t: float(t.replace("width_", "").replace("p", ".")))
    scales = [float(t.replace("width_", "").replace("p", ".")) for t in tags]
    return tags, scales


def eval_one(cfg, ckpt_path, root, device):
    import torch
    d = cfg["dataset"]
    size = tuple(d.get("image_size", [256, 256]))
    ds = RoadMarkDataset(root=root, split="test", num_classes=d["num_classes"],
                         transform=build_transforms("val", size),
                         strict=d.get("strict", True))
    from torch.utils.data import DataLoader
    loader = DataLoader(ds, batch_size=8)
    model = build_model_from_cfg(cfg).to(device)
    ck = torch.load(ckpt_path, map_location=device)
    model.load_state_dict(ck["model"] if "model" in ck else ck)
    seg, cm, thin, _ = evaluate_model(model, loader, d["num_classes"], device=device,
                                      class_names=d.get("class_names"),
                                      foreground_only=True, thin_structure=True)
    return {"mIoU": seg.miou, "clDice": thin.cl_dice, "clRecall": thin.cl_recall,
            "TolIoU": thin.tol_iou, "BoundaryIoU": thin.boundary_iou}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--configs", nargs="+", required=True)
    ap.add_argument("--checkpoints", nargs="+", required=True)
    ap.add_argument("--labels", nargs="+", required=True)
    ap.add_argument("--series", default="datasets/width_series")
    ap.add_argument("--out", default="reports/visualizations/width_study")
    args = ap.parse_args()
    assert len(args.configs) == len(args.checkpoints) == len(args.labels)

    import torch
    device = "cuda" if torch.cuda.is_available() else "cpu"
    seed_everything(42)
    os.makedirs(args.out, exist_ok=True)
    tags, scales = width_tags(args.series)

    results = {}  # label -> metric -> [per width]
    for cfg_path, ckpt, label in zip(args.configs, args.checkpoints, args.labels):
        cfg = load_config(cfg_path)
        per_width = {m: [] for m in ["mIoU", "clDice", "clRecall", "TolIoU", "BoundaryIoU"]}
        for tag in tags:
            root = os.path.join(args.series, tag)
            r = eval_one(cfg, ckpt, root, device)
            for m in per_width:
                per_width[m].append(r[m])
            print(f"{label:10s} {tag:10s} mIoU={r['mIoU']:.3f} clDice={r['clDice']:.3f} "
                  f"TolIoU={r['TolIoU']:.3f}")
        results[label] = per_width

    with open(os.path.join(args.out, "width_study.json"), "w") as f:
        json.dump({"scales": scales, "results": results}, f, indent=2)

    # approximate physical width in px ~ 4*scale (the dominant lane thickness)
    px = [4 * s for s in scales]
    metrics_to_plot = ["mIoU", "clDice", "TolIoU"]
    fig, axes = plt.subplots(1, len(metrics_to_plot), figsize=(5 * len(metrics_to_plot), 4))
    for ax, m in zip(axes, metrics_to_plot):
        for label in results:
            ax.plot(px, results[label][m], marker="o", label=label)
        ax.set_xlabel("approx. marking width (px)")
        ax.set_ylabel(m)
        ax.set_title(f"{m} vs marking width")
        ax.grid(alpha=0.3)
        ax.legend()
    fig.suptitle("Thin-structure gap: metric degradation as markings get thinner")
    fig.tight_layout()
    out_png = os.path.join(args.out, "width_study.png")
    fig.savefig(out_png, dpi=150)
    print(f"Wrote {out_png} and width_study.json")


if __name__ == "__main__":
    main()
