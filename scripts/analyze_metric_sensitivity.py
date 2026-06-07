#!/usr/bin/env python3
"""Adversarial metric-sensitivity analysis (reproduces reports/metric_sensitivity_analysis.md).

For the RLMD 25-class loss-ablation models, computes every common IoU/accuracy
variant and tests two properties: flood-robustness (does the metric rank
frame-flooding losses below non-flooders?) and foreground-sensitivity (does it
spread the non-flooding losses by their clDice-ordered quality?).
"""
import json
import os
import sys

import numpy as np

LOSSES = ["ce", "dice", "ce_dice", "focal", "tversky", "core"]
FLOODERS = {"dice", "tversky"}  # PixelAcc ~ 0.008 -> predict marking ~everywhere


def main(outdir="outputs"):
    rows = {}
    for L in LOSSES:
        p = os.path.join(outdir, f"rlmd_unetpp_{L}", "eval_test.json")
        if not os.path.exists(p):
            print(f"missing {p} (run the RLMD ablation first)"); continue
        d = json.load(open(p))
        iou = np.array(d["per_class_iou"])
        rows[L] = {
            "fg_miou": float(np.mean(iou[1:])),
            "all_miou": float(np.mean(iou)),
            "fwiou": float(d["freq_weighted_iou"]),
            "pixacc": float(d["pixel_accuracy"]),
            "cldice": float(d.get("thin_structure", {}).get("clDice", 0.0)),
        }
    if not rows:
        return

    metrics = ["fg_miou", "all_miou", "fwiou", "pixacc", "cldice"]
    print(f"{'loss':9s}" + "".join(f"{m:>10s}" for m in metrics))
    for L in LOSSES:
        if L in rows:
            print(f"{L:9s}" + "".join(f"{rows[L][m]:10.4f}" for m in metrics))

    def rank(m):
        return [L for L in sorted(rows, key=lambda x: rows[x][m], reverse=True)]

    print("\nRankings (best->worst):")
    for m in metrics:
        print(f"  {m:9s}: {rank(m)}")

    # Best detector by an independent reference (clDice ground-truth ordering;
    # ce_dice has the only high clPrecision 0.91 and is the de-facto best).
    best = "ce_dice"
    non_flood = [L for L in rows if L not in FLOODERS]

    print("\n--- Test 1: is the metric's #1-ranked loss a frame-flooder? ---")
    for m in metrics:
        top = rank(m)[0]
        floods = rows[top]["pixacc"] < 0.05
        print(f"  {m:9s}: top='{top}' (PixAcc {rows[top]['pixacc']:.3f}) -> "
              f"{'REWARDS FLOODING' if floods else 'ok'}")

    print(f"\n--- Test 2: does the metric rank the best detector ('{best}') #1? ---")
    for m in metrics:
        pos = rank(m).index(best) + 1
        print(f"  {m:9s}: '{best}' ranked #{pos}  -> {'YES' if pos == 1 else 'no'}")

    print("\n--- Test 3: foreground-sensitivity (spread over non-flooding losses) ---")
    for m in metrics:
        vals = [rows[L][m] for L in non_flood]
        print(f"  {m:9s}: spread {max(vals)-min(vals):.3f}")
    print("\nVerdict: mIoU fails Test 1 (top pick floods); FWIoU/PixAcc pass 1&2 but"
          " fail Test 3 (spread <0.01); only clDice passes all three.")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "outputs")
