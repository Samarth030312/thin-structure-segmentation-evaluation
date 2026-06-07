#!/usr/bin/env python3
"""Regenerate all paper figures at publication quality.

Consistent styling, 300 DPI raster + vector PDF, paper-ready. Reads the committed
result files and renders into `paper_figures/`. Re-runnable; skips a figure (with
a note) if its source data is absent.
"""
import json
import os
import sys

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = "paper_figures"
PALETTE = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9"]

# ---- consistent publication style ----
plt.rcParams.update({
    "figure.dpi": 300, "savefig.dpi": 300,
    "font.size": 11, "font.family": "DejaVu Sans",
    "axes.grid": True, "grid.alpha": 0.3, "axes.axisbelow": True,
    "axes.spines.top": False, "axes.spines.right": False,
    "legend.frameon": False, "figure.autolayout": True,
})


def save(fig, name):
    os.makedirs(OUT, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(OUT, f"{name}.{ext}"), bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {OUT}/{name}.png + .pdf")


def fig_width_study():
    p = "reports/visualizations/width_study/width_study.json"
    if not os.path.exists(p):
        print("  skip width_study (no data)"); return
    d = json.load(open(p)); px = [4 * s for s in d["scales"]]
    metrics = ["mIoU", "clDice", "TolIoU"]
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.4))
    for ax, m in zip(axes, metrics):
        for i, (lab, r) in enumerate(d["results"].items()):
            ax.plot(px, r[m], marker="o", color=PALETTE[i % len(PALETTE)], label=lab, lw=2)
        ax.set_xlabel("marking width (px)"); ax.set_ylabel(m); ax.set_title(m)
    axes[0].legend()
    fig.suptitle("Metric degradation vs marking width (synthetic, controlled)", y=1.03)
    save(fig, "fig1_width_study")


def fig_loss_ablation():
    if not os.path.exists("reports/leaderboard.csv"):
        print("  skip loss ablation"); return
    df = pd.read_csv("reports/leaderboard.csv")
    rows = df[df.run_name.isin([f"rlmd_unetpp_{l}" for l in
              ["ce", "dice", "ce_dice", "tversky", "focal", "core"]])].copy()
    if rows.empty:
        print("  skip loss ablation (no unetpp rows)"); return
    rows["loss"] = rows.run_name.str.replace("rlmd_unetpp_", "")
    order = ["ce", "dice", "ce_dice", "focal", "tversky", "core"]
    rows = rows.set_index("loss").reindex([o for o in order if o in rows.loss.values
                                           or o in rows.index]).dropna(how="all").reset_index()
    fig, ax = plt.subplots(figsize=(7.5, 4))
    x = np.arange(len(rows)); w = 0.27
    ax.bar(x - w, rows["mIoU"], w, label="mIoU", color=PALETTE[0])
    ax.bar(x, rows["clDice"], w, label="clDice", color=PALETTE[2])
    ax.bar(x + w, rows["PixelAcc"], w, label="PixelAcc", color=PALETTE[1])
    ax.set_xticks(x); ax.set_xticklabels(rows["loss"], rotation=20)
    ax.set_ylabel("score"); ax.set_title("RLMD loss ablation (U-Net++): mIoU vs clDice vs PixelAcc")
    ax.legend()
    fig.text(0.5, -0.04, "Note: Dice/Tversky get top mIoU but PixelAcc≈0 (frame-flooding) — mIoU mis-ranks.",
             ha="center", fontsize=8, style="italic")
    save(fig, "fig2_rlmd_loss_ablation")


def fig_perf_pareto():
    p = "reports/leaderboard_performance.csv"
    if not os.path.exists(p):
        print("  skip perf pareto"); return
    df = pd.read_csv(p)
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    for i, r in df.iterrows():
        ax.scatter(r["gpu_fps"], r["GFLOPs"], s=60 + r["params_M"] * 6,
                   color=PALETTE[i % len(PALETTE)])
        ax.annotate(r["model"], (r["gpu_fps"], r["GFLOPs"]),
                    xytext=(4, 4), textcoords="offset points", fontsize=9)
    ax.set_xlabel("GPU throughput (FPS)"); ax.set_ylabel("GFLOPs")
    ax.set_title("Compute Pareto (marker size ∝ params)")
    save(fig, "fig3_perf_pareto")


def fig_stats_ci():
    """Multi-seed mean ± 95% CI for CE+Dice vs CoRe (authoritative over single-seed)."""
    p = "reports/multiseed_results.json"
    if not os.path.exists(p):
        print("  skip stats CI (no multiseed)"); return
    d = json.load(open(p))
    losses = [k for k in ["ce_dice", "core"] if k in d]
    metrics = ["clDice", "TolIoU", "mIoU"]
    fig, ax = plt.subplots(figsize=(7, 4))
    x = np.arange(len(metrics)); w = 0.35
    for j, loss in enumerate(losses):
        means = [d[loss][m]["mean"] for m in metrics]
        errs = [d[loss][m]["ci95_halfwidth"] for m in metrics]
        ax.bar(x + (j - 0.5) * w, means, w, yerr=errs, capsize=4,
               color=PALETTE[j], label=loss)
    ax.set_xticks(x); ax.set_xticklabels(metrics)
    ax.set_ylabel("score (mean ± 95% CI, 3 seeds)")
    ax.set_title("Multi-seed loss comparison on RLMD — CE+Dice vs CoRe (tied)")
    ax.legend()
    fig.text(0.5, -0.04, "Single-seed CE+Dice>CoRe does not survive multi-seed (Δ=-0.001, n.s.).",
             ha="center", fontsize=8, style="italic")
    save(fig, "fig4_stats_ci")


def fig_xdomain():
    p = "reports/leaderboard_xdomain.csv"
    if not os.path.exists(p):
        print("  skip cross-dataset (no data yet)"); return
    df = pd.read_csv(p)
    order = ["xd_rlmd_to_rlmd", "xd_rlmd_to_loveda", "xd_loveda_to_loveda", "xd_loveda_to_rlmd"]
    df = df[df.run_name.isin(order)]
    mat = np.full((2, 2), np.nan)
    idx = {"xd_rlmd_to_rlmd": (0, 0), "xd_rlmd_to_loveda": (0, 1),
           "xd_loveda_to_rlmd": (1, 0), "xd_loveda_to_loveda": (1, 1)}
    for _, r in df.iterrows():
        if r["run_name"] in idx:
            mat[idx[r["run_name"]]] = r["clDice"]
    fig, ax = plt.subplots(figsize=(4.6, 4))
    im = ax.imshow(mat, cmap="viridis", vmin=0)
    ax.set_xticks([0, 1]); ax.set_xticklabels(["→RLMD", "→LoveDA"])
    ax.set_yticks([0, 1]); ax.set_yticklabels(["train RLMD", "train LoveDA"])
    for i in range(2):
        for j in range(2):
            if not np.isnan(mat[i, j]):
                ax.text(j, i, f"{mat[i, j]:.3f}", ha="center", va="center",
                        color="w" if mat[i, j] < mat[np.isfinite(mat)].max() * 0.6 else "k")
    fig.colorbar(im, label="clDice"); ax.set_title("Cross-dataset transfer (clDice)")
    save(fig, "fig5_cross_dataset")


if __name__ == "__main__":
    print("Regenerating paper figures (300 DPI + PDF)...")
    fig_width_study(); fig_loss_ablation(); fig_perf_pareto(); fig_stats_ci(); fig_xdomain()
    print("Done ->", OUT)
