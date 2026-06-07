#!/usr/bin/env python3
"""Publication figures for the width-coupling law (Figs A-D), 300 DPI + vector."""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from run_controlled_robustness import degrade, make_structure, metrics  # type: ignore  # noqa: E402

import importlib.util
_spec = importlib.util.spec_from_file_location(
    "rcr", os.path.join(os.path.dirname(__file__), "run_controlled_robustness.py"))
_rcr = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_rcr)

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

plt.rcParams.update({"figure.dpi": 300, "savefig.dpi": 300, "font.size": 11,
                     "axes.grid": True, "grid.alpha": 0.3, "axes.spines.top": False,
                     "axes.spines.right": False, "legend.frameon": False})
OUT = "paper_figures"
os.makedirs(OUT, exist_ok=True)
VAL = "reports/visualizations/uav_validation"


def load_real_points():
    """Load real-dataset (label, MEASURED mean width px, MEASURED mean gap) from the
    width-validation JSONs — no hand-assigned values. The synthetic point uses the
    GT-controlled width (2 px) and the multi-seed measured gap."""
    pts = []
    # synthetic: controlled 2-px width, gap from the multi-seed width study
    try:
        ms = json.load(open("reports/visualizations/width_study_multiseed/width_multiseed.json"))
        a = ms["agg"]["ce_dice"]
        gap0 = a["clDice"]["mean"][0] - a["mIoU"]["mean"][0]  # first tag = 2-px GT width
        pts.append(("Synthetic (2px GT)", 2.0, round(gap0, 3)))
    except Exception:
        pass
    for label in ("MassRoads", "LoveDA", "UAVid"):
        p = os.path.join(VAL, f"{label}_width_val.json")
        if os.path.exists(p):
            j = json.load(open(p))
            pts.append((label, j["measured_mean_width_px"], j["measured_mean_gap"]))
    return pts


REAL = load_real_points()


def save(fig, name):
    for e in ("png", "pdf"):
        fig.savefig(f"{OUT}/{name}.{e}", bbox_inches="tight")
    plt.close(fig); print("wrote", name)


def fig_A():
    d = json.load(open("reports/controlled/robustness_sweeps.json"))["dilate_1"]
    w = np.array([r["width"] for r in d]); gap = np.array([r["gap"] for r in d])
    fit = json.load(open("reports/controlled/law_fit.json"))
    dd = fit["inverse_d"]
    xs = np.linspace(1, 30, 200)
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    ax.scatter(w, gap, color="#444", zorder=3, label="controlled (1-px error)")
    ax.plot(xs, 2 * dd / (xs + 2 * dd), color="#009E73", lw=2,
            label=f"law  2$\\delta$/(w+2$\\delta$), $\\delta$={dd:.2f}")
    for name, ww, g in REAL:
        ax.scatter(ww, g, marker="*", s=180, zorder=4)
        ax.annotate(name, (ww, g), xytext=(5, 4), textcoords="offset points", fontsize=8)
    ax.set_xlabel("structure width (px)"); ax.set_ylabel("Gap = clDice - mIoU")
    ax.set_title("Figure A: Width-coupling law (controlled + real datasets)")
    ax.legend(); save(fig, "figA_width_gap_law")


def fig_B():
    d = json.load(open("reports/controlled/robustness_sweeps.json"))["dilate_1"]
    w = np.array([r["width"] for r in d])
    rel = np.array([(r["clDice"] - r["IoU"]) / max(1e-6, r["clDice"]) for r in d])
    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.plot(w, 100 * rel, marker="o", color="#D55E00", lw=2)
    ax.set_xlabel("structure width (px)")
    ax.set_ylabel("relative mIoU under-report  (%) = (clDice-mIoU)/clDice")
    ax.set_title("Figure B: Relative metric error vs width")
    save(fig, "figB_relative_error")


def fig_C():
    # heatmap: width x boundary-error magnitude -> gap
    widths = np.arange(1, 31, 2)
    deltas = [1, 2, 3, 4]
    H = np.zeros((len(deltas), len(widths)))
    for i, dl in enumerate(deltas):
        for j, w in enumerate(widths):
            gs = []
            for s in range(3):
                gt = _rcr.make_structure(int(w), seed=s)
                pr = _rcr.degrade(gt, "dilate", dl, seed=s)
                m = _rcr.metrics(gt, pr); gs.append(m["clDice"] - m["IoU"])
            H[i, j] = np.mean(gs)
    fig, ax = plt.subplots(figsize=(7, 3.6))
    im = ax.imshow(H, aspect="auto", cmap="magma", origin="lower",
                   extent=[widths[0], widths[-1], deltas[0] - 0.5, deltas[-1] + 0.5])
    ax.set_xlabel("structure width (px)"); ax.set_ylabel("boundary error $\\delta$ (px)")
    ax.set_yticks(deltas)
    ax.set_title("Figure C: Metric-disagreement heatmap (Gap)")
    fig.colorbar(im, label="Gap = clDice - mIoU")
    save(fig, "figC_disagreement_heatmap")


def fig_D():
    fit = json.load(open("reports/controlled/law_fit.json")); dd = fit["inverse_d"]
    xs = np.linspace(1, 30, 300); gap = 2 * dd / (xs + 2 * dd)
    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.fill_between(xs, 0, gap, where=gap > 0.2, color="#cf222e", alpha=0.18)
    ax.fill_between(xs, 0, gap, where=(gap <= 0.2) & (gap > 0.05), color="#e69f00", alpha=0.18)
    ax.fill_between(xs, 0, gap, where=gap <= 0.05, color="#1a7f37", alpha=0.18)
    ax.plot(xs, gap, color="#222", lw=2)
    ax.axhline(0.2, ls=":", color="#cf222e"); ax.axhline(0.05, ls=":", color="#1a7f37")
    ax.text(2, 0.5, "FAILURE\n(<~5 px)", color="#cf222e", fontsize=9, weight="bold")
    ax.text(8, 0.13, "WARNING\n(5-25 px)", color="#9a6700", fontsize=9, weight="bold")
    ax.text(24, 0.02, "SAFE (>~25 px)", color="#1a7f37", fontsize=9, weight="bold")
    ax.set_xlabel("structure width (px)"); ax.set_ylabel("Gap = clDice - mIoU")
    ax.set_title("Figure D: mIoU reliability zones for thin structures")
    save(fig, "figD_failure_zones")


def fig_thinness():
    """fig7: cross-dataset thinness threshold, real datasets at MEASURED widths."""
    fit = json.load(open("reports/controlled/law_fit.json")); dd = fit["inverse_d"]
    xs = np.linspace(1, 30, 200)
    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.plot(xs, 2 * dd / (xs + 2 * dd), "--", color="#999", zorder=1,
            label=f"law 2$\\delta$/(w+2$\\delta$), $\\delta$={dd:.2f}")
    colors = {"Synthetic (2px GT)": "#CC79A7", "MassRoads": "#009E73",
              "LoveDA": "#0072B2", "UAVid": "#D55E00"}
    for name, ww, g in REAL:
        ax.scatter(ww, g, s=130, color=colors.get(name, "#444"), zorder=3)
        ax.annotate(name, (ww, g), xytext=(6, 4), textcoords="offset points", fontsize=8)
    ax.axhline(0, color="k", lw=0.8)
    ax.set_xlabel("measured structure width (px)")
    ax.set_ylabel("Gap = clDice - mIoU")
    ax.set_title("mIoU under-reporting is thinness-bounded (real + synthetic)")
    ax.legend(); save(fig, "fig7_thinness_threshold")


if __name__ == "__main__":
    print("real-data points (MEASURED):", REAL)
    fig_A(); fig_B(); fig_C(); fig_D(); fig_thinness()
    print("Done ->", OUT)
