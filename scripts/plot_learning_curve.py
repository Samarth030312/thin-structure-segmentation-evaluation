#!/usr/bin/env python3
"""Plot a training run's learning curves (loss + metrics per epoch) to document
convergence. Reads outputs/<run>/history.json.

    python scripts/plot_learning_curve.py --run rlmdbin_converge
"""
import argparse
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", default="reports/visualizations/convergence")
    args = ap.parse_args()
    hist = json.load(open(f"outputs/{args.run}/history.json"))
    ep = [h["epoch"] for h in hist]
    os.makedirs(args.out, exist_ok=True)

    fig, ax1 = plt.subplots(figsize=(6.5, 4))
    ax1.plot(ep, [h["train_loss"] for h in hist], "--", color="#999", label="train loss")
    ax1.plot(ep, [h["val_loss"] for h in hist], "-", color="#333", label="val loss")
    ax1.set_xlabel("epoch"); ax1.set_ylabel("loss"); ax1.grid(alpha=0.3)
    ax2 = ax1.twinx()
    ax2.plot(ep, [h.get("mIoU", 0) for h in hist], color="#0072B2", marker="o",
             ms=3, label="val mIoU")
    if "clDice" in hist[0]:
        ax2.plot(ep, [h.get("clDice", 0) for h in hist], color="#009E73", marker="s",
                 ms=3, label="val clDice")
    ax2.set_ylabel("metric")
    l1, la1 = ax1.get_legend_handles_labels(); l2, la2 = ax2.get_legend_handles_labels()
    ax1.legend(l1 + l2, la1 + la2, loc="center right", fontsize=8)
    final = hist[-1]
    ax1.set_title(f"Convergence: {args.run}  (final val mIoU={final.get('mIoU',0):.3f})")
    fig.tight_layout()
    fig.savefig(f"{args.out}/{args.run}_curve.png", dpi=300)
    fig.savefig(f"{args.out}/{args.run}_curve.pdf")
    # simple plateau check: last-5 vs prior-5 mIoU
    mious = [h.get("mIoU", 0) for h in hist]
    if len(mious) >= 10:
        import numpy as np
        last5, prev5 = np.mean(mious[-5:]), np.mean(mious[-10:-5])
        print(f"{args.run}: mIoU last-5 {last5:.3f} vs prev-5 {prev5:.3f} "
              f"(Δ={last5-prev5:+.3f} -> {'converged' if abs(last5-prev5)<0.02 else 'still improving'})")
    print(f"Wrote {args.out}/{args.run}_curve.png/.pdf")


if __name__ == "__main__":
    main()
