#!/usr/bin/env python3
"""Statistical comparison of two checkpoints with per-image metrics, bootstrap
confidence intervals, and a paired significance test (real-data rigor).

    python scripts/run_stats_compare.py \
        --config-a configs/experiment/rlmd_unetpp_core.yaml --ckpt-a outputs/rlmd_unetpp_core/best.pth \
        --config-b configs/experiment/rlmd_unet_ce_dice.yaml --ckpt-b outputs/rlmd_unet_ce_dice/best.pth \
        --labels CoRe CEDice --metric clDice --out reports/stats
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from uavroadmark.build import build_model_from_cfg  # noqa: E402
from uavroadmark.data import RoadMarkDataset, build_transforms  # noqa: E402
from uavroadmark.metrics.segmentation import iou_score  # noqa: E402
from uavroadmark.metrics.stats import bootstrap_ci, fmt_ci, paired_bootstrap_test  # noqa: E402
from uavroadmark.metrics.thin_structure import cl_dice, tolerance_scores  # noqa: E402
from uavroadmark.utils import load_config, seed_everything  # noqa: E402


def per_image_metrics(cfg, ckpt, device):
    import torch
    from torch.utils.data import DataLoader
    d = cfg["dataset"]; size = tuple(d.get("image_size", [384, 384]))
    ds = RoadMarkDataset(d["root"], "test", build_transforms("val", size),
                         num_classes=d["num_classes"], strict=d.get("strict", True))
    loader = DataLoader(ds, batch_size=8)
    model = build_model_from_cfg(cfg).to(device)
    ck = torch.load(ckpt, map_location=device)
    model.load_state_dict(ck["model"] if "model" in ck else ck); model.eval()
    rows = {"clDice": [], "TolIoU": [], "clRecall": [], "mIoU": []}
    with torch.no_grad():
        for b in loader:
            pr = torch.argmax(model(b["image"].to(device)), 1).cpu().numpy()
            gt = b["mask"].numpy()
            for i in range(pr.shape[0]):
                g, p = gt[i], pr[i]
                rows["clDice"].append(cl_dice(g > 0, p > 0))
                ts = tolerance_scores(g > 0, p > 0, tau=3)
                rows["TolIoU"].append(ts["tol_iou"]); rows["clRecall"].append(ts["cl_recall"])
                rows["mIoU"].append(iou_score(g, p, d["num_classes"]))
    return {k: np.array(v) for k, v in rows.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config-a", required=True); ap.add_argument("--ckpt-a", required=True)
    ap.add_argument("--config-b", required=True); ap.add_argument("--ckpt-b", required=True)
    ap.add_argument("--labels", nargs=2, default=["A", "B"])
    ap.add_argument("--out", default="reports/stats")
    args = ap.parse_args()

    import torch
    device = "cuda" if torch.cuda.is_available() else "cpu"
    seed_everything(42); os.makedirs(args.out, exist_ok=True)
    la, lb = args.labels
    A = per_image_metrics(load_config(args.config_a), args.ckpt_a, device)
    B = per_image_metrics(load_config(args.config_b), args.ckpt_b, device)

    report = {"labels": args.labels, "n_test_images": len(A["clDice"]), "metrics": {}}
    print(f"n_test_images = {len(A['clDice'])}\n")
    for m in ["clDice", "TolIoU", "clRecall", "mIoU"]:
        ci_a, ci_b = bootstrap_ci(A[m]), bootstrap_ci(B[m])
        test = paired_bootstrap_test(A[m], B[m])
        report["metrics"][m] = {la: ci_a, lb: ci_b, "paired_test": test}
        sig = "SIGNIFICANT" if test["significant_0.05"] else "n.s."
        print(f"{m:9s} | {la}: {fmt_ci(ci_a)} | {lb}: {fmt_ci(ci_b)} | "
              f"Δ={test['mean_diff']:+.3f} [{test['lo']:+.3f},{test['hi']:+.3f}] "
              f"p={test['p_value']:.3f} {sig}")
    json.dump(report, open(os.path.join(args.out, "stats_compare.json"), "w"), indent=2)
    print(f"\nWrote {args.out}/stats_compare.json")


if __name__ == "__main__":
    main()
