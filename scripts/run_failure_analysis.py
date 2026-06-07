#!/usr/bin/env python3
"""Failure analysis: rank test predictions, surface the worst, and categorise
their failure modes with interpretable, image-derived heuristics.

Failure-mode taxonomy (computed from each image/GT):
  * thin_marking      - mean GT marking width below threshold
  * shadow_lowcontrast- low local contrast / dark cast-shadow region present
  * high_density      - many connected marking components (intersection/zebra)
  * sparse_marking    - very low foreground coverage (little signal)
  * other

    python scripts/run_failure_analysis.py \
        --config configs/experiment/abl_unet_core.yaml \
        --checkpoint outputs/abl_unet_core/best.pth \
        --out reports/visualizations/failure_analysis --worst 100
"""
import argparse
import json
import os
import sys
from collections import Counter

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from uavroadmark.build import build_model_from_cfg  # noqa: E402
from uavroadmark.data import RoadMarkDataset, build_transforms  # noqa: E402
from uavroadmark.data.transforms import IMAGENET_MEAN, IMAGENET_STD  # noqa: E402
from uavroadmark.metrics.segmentation import iou_score  # noqa: E402
from uavroadmark.metrics.thin_structure import cl_dice, local_width  # noqa: E402
from uavroadmark.viz.overlays import comparison_panel  # noqa: E402
from uavroadmark.utils import load_config, seed_everything  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")


def _denorm(t):
    img = t.permute(1, 2, 0).cpu().numpy() * np.array(IMAGENET_STD) + np.array(IMAGENET_MEAN)
    return np.clip(img * 255, 0, 255).astype(np.uint8)


def categorise(rgb, gt) -> str:
    import cv2
    fg = gt > 0
    cov = fg.mean()
    if cov < 1e-4:
        return "sparse_marking"
    widths = local_width(fg)
    mean_w = widths[fg].mean() if fg.any() else 0
    n_comp = cv2.connectedComponents(fg.astype(np.uint8))[0] - 1
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    contrast = gray.std()
    blur_var = cv2.Laplacian(gray, cv2.CV_64F).var()  # low => blurry
    # priority order of explanations
    if blur_var < 60:
        return "blur"
    if mean_w < 3.0:
        return "thin_marking"
    if contrast < 28 or gray.min() < 25:
        return "shadow_lowcontrast"
    if n_comp >= 6:
        return "high_density"
    if cov < 0.02:
        return "sparse_marking"
    return "other"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--split", default="test")
    ap.add_argument("--out", default="reports/visualizations/failure_analysis")
    ap.add_argument("--worst", type=int, default=100)
    ap.add_argument("--save-panels", type=int, default=12)
    args = ap.parse_args()

    import torch
    from torch.utils.data import DataLoader

    cfg = load_config(args.config)
    seed_everything(cfg.get("seed", 42))
    device = "cuda" if torch.cuda.is_available() else "cpu"
    d = cfg["dataset"]
    size = tuple(d.get("image_size", [256, 256]))
    ds = RoadMarkDataset(d["root"], args.split, build_transforms("val", size),
                         num_classes=d["num_classes"], strict=d.get("strict", True))
    loader = DataLoader(ds, batch_size=8)

    model = build_model_from_cfg(cfg).to(device)
    ck = torch.load(args.checkpoint, map_location=device)
    model.load_state_dict(ck["model"] if "model" in ck else ck)
    model.eval()

    os.makedirs(args.out, exist_ok=True)
    records = []
    idx = 0
    with torch.no_grad():
        for batch in loader:
            logits = model(batch["image"].to(device))
            preds = torch.argmax(logits, 1).cpu().numpy()
            for b in range(preds.shape[0]):
                gt = batch["mask"][b].numpy()
                pr = preds[b]
                rgb = _denorm(batch["image"][b])
                iou = iou_score(gt, pr, d["num_classes"])
                cld = cl_dice(gt > 0, pr > 0)
                score = 0.5 * iou + 0.5 * cld  # combined quality
                cat = categorise(rgb, gt)
                records.append({"idx": idx, "stem": batch["stem"][b],
                                "iou": float(iou), "clDice": float(cld),
                                "score": float(score), "category": cat,
                                "_rgb": rgb, "_gt": gt, "_pr": pr})
                idx += 1

    records.sort(key=lambda r: r["score"])
    worst = records[:min(args.worst, len(records))]

    # save panels for the very worst
    for i, r in enumerate(worst[:args.save_panels]):
        comparison_panel(r["_rgb"], r["_gt"], r["_pr"],
                         save_path=os.path.join(args.out, f"worst_{i:02d}_{r['category']}.png"))

    cat_counts = Counter(r["category"] for r in worst)
    summary = {
        "n_eval": len(records),
        "n_worst": len(worst),
        "mean_score_all": float(np.mean([r["score"] for r in records])),
        "mean_score_worst": float(np.mean([r["score"] for r in worst])),
        "failure_mode_counts": dict(cat_counts),
        "worst": [{k: r[k] for k in ("stem", "iou", "clDice", "score", "category")}
                  for r in worst],
    }
    with open(os.path.join(args.out, "failure_analysis.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print("Failure-mode counts (worst %d):" % len(worst))
    for c, n in cat_counts.most_common():
        print(f"  {c:20s} {n}")
    print(f"Wrote panels + failure_analysis.json to {args.out}")


if __name__ == "__main__":
    main()
