#!/usr/bin/env python3
"""Aggregate multi-seed runs: per-loss mean/std/95% CI across seeds, and a
paired (per-seed) comparison of ce_dice vs core. Reads leaderboard_multiseed.csv,
writes reports/multiseed_results.json + a markdown summary."""
import json
import os
import sys

import numpy as np
import pandas as pd

LB = "reports/leaderboard_multiseed.csv"
OUT_JSON = "reports/multiseed_results.json"


def ci95(x):
    x = np.asarray(x, float)
    if len(x) < 2:
        return (float(x.mean()) if len(x) else float("nan"), float("nan"), float("nan"))
    m, s = x.mean(), x.std(ddof=1)
    half = 1.96 * s / np.sqrt(len(x))
    return float(m), float(s), float(half)


def main():
    if not os.path.exists(LB):
        print("no multiseed leaderboard yet"); return
    df = pd.read_csv(LB)
    df["loss"] = df.run_name.str.extract(r"ms_(.+)_s\d+")
    df["seed"] = df.run_name.str.extract(r"_s(\d+)").astype(int)
    metrics = ["mIoU", "PixelAcc", "clDice", "clRecall", "TolIoU"]
    result = {}
    for loss, g in df.groupby("loss"):
        result[loss] = {"n_seeds": int(g.seed.nunique()), "seeds": sorted(g.seed.tolist())}
        for m in metrics:
            mean, std, half = ci95(g[m].values)
            result[loss][m] = {"mean": round(mean, 4), "std": round(std, 4),
                               "ci95_halfwidth": round(half, 4)}
    # paired ce_dice vs core across matched seeds (clDice)
    piv = df.pivot_table(index="seed", columns="loss", values="clDice")
    if {"ce_dice", "core"}.issubset(piv.columns):
        d = (piv["ce_dice"] - piv["core"]).dropna().values
        m, s, half = ci95(d)
        result["_paired_ce_dice_minus_core_clDice"] = {
            "mean_diff": round(m, 4), "ci95": [round(m - half, 4), round(m + half, 4)],
            "n_pairs": int(len(d)),
            "ce_dice_better_all_seeds": bool((d > 0).all())}
    json.dump(result, open(OUT_JSON, "w"), indent=2)

    print(f"=== Multi-seed summary ({df.seed.nunique()} seeds) ===")
    for loss in sorted([k for k in result if not k.startswith("_")]):
        r = result[loss]
        print(f"{loss:8s} clDice {r['clDice']['mean']:.3f} ± {r['clDice']['ci95_halfwidth']:.3f} "
              f"| mIoU {r['mIoU']['mean']:.3f} | PixelAcc {r['PixelAcc']['mean']:.3f} "
              f"(n={r['n_seeds']})")
    if "_paired_ce_dice_minus_core_clDice" in result:
        p = result["_paired_ce_dice_minus_core_clDice"]
        print(f"\nPaired clDice (CE+Dice - CoRe): {p['mean_diff']:+.3f} "
              f"CI95 {p['ci95']} | CE+Dice better in all seeds: {p['ce_dice_better_all_seeds']}")
    print(f"Wrote {OUT_JSON}")


if __name__ == "__main__":
    main()
