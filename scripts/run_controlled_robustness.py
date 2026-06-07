#!/usr/bin/env python3
"""Controlled, geometry-only robustness study for the width-coupling effect.

The goal is to decouple the metric-disagreement effect from any dataset or model:
we generate synthetic thin structures of *controlled* width, apply *controlled*
degradations that mimic a prediction error, and measure how IoU/Dice/clDice/
Boundary-IoU/Tolerance-IoU respond. If Gap = clDice - mIoU depends only on
*geometry* (width, error magnitude) and not on the dataset, the effect is a law,
not an artifact.

Outputs JSON sweeps to reports/controlled/ for fitting (Phase 1) and figures.
"""
import argparse
import json
import os
import sys

import cv2
import numpy as np
from scipy.ndimage import binary_dilation, binary_erosion, distance_transform_edt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from uavroadmark.metrics.thin_structure import (boundary_iou, cl_dice,  # noqa: E402
                                                tolerance_scores)

CANVAS = 256


def make_structure(width, kind="wave", seed=0, canvas=CANVAS):
    """A binary thin structure of given pixel width (a wavy line with a real
    skeleton, so clDice is meaningful)."""
    rng = np.random.default_rng(seed)
    m = np.zeros((canvas, canvas), np.uint8)
    th = max(1, int(round(width)))
    xs = np.arange(10, canvas - 10)
    amp = rng.uniform(20, 50); period = rng.uniform(60, 120); phase = rng.uniform(0, 6)
    ys = (canvas // 2 + amp * np.sin(2 * np.pi * xs / period + phase)).astype(int)
    pts = np.stack([xs, ys], 1).astype(np.int32)
    cv2.polylines(m, [pts], False, 1, th)
    return m.astype(bool)


def iou(gt, pr):
    return (gt & pr).sum() / max(1, (gt | pr).sum())


def dice(gt, pr):
    return 2 * (gt & pr).sum() / max(1, gt.sum() + pr.sum())


def degrade(gt, mode, mag, seed=0):
    """Produce a 'prediction' from GT via a controlled degradation."""
    rng = np.random.default_rng(seed + 1)
    if mode == "dilate":
        return binary_dilation(gt, iterations=int(mag))
    if mode == "erode":
        e = binary_erosion(gt, iterations=int(mag))
        return e if e.sum() > 0 else gt
    if mode == "shift":
        return np.roll(gt, int(mag), axis=0)
    if mode == "boundary_noise":
        # randomly flip boundary-band pixels with prob ~mag
        band = binary_dilation(gt, iterations=2) & ~binary_erosion(gt, iterations=2)
        flip = (rng.random(gt.shape) < mag) & band
        return gt ^ flip
    if mode == "gaps":
        # delete random vertical slabs (recall < 1, topology breaks)
        pr = gt.copy()
        for _ in range(int(mag * 6)):
            x0 = rng.integers(0, gt.shape[1] - 8)
            pr[:, x0:x0 + 6] = False
        return pr
    raise ValueError(mode)


def metrics(gt, pr):
    return {
        "IoU": float(iou(gt, pr)),
        "Dice": float(dice(gt, pr)),
        "clDice": float(cl_dice(gt, pr)),
        "BoundaryIoU": float(boundary_iou(gt, pr)),
        "TolIoU": float(tolerance_scores(gt, pr, tau=3)["tol_iou"]),
    }


def sweep_width(mode="dilate", mag=1, widths=None, n_seeds=5):
    widths = widths or [1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30]
    out = []
    for w in widths:
        vals = {k: [] for k in ["IoU", "Dice", "clDice", "BoundaryIoU", "TolIoU"]}
        for s in range(n_seeds):
            gt = make_structure(w, seed=s)
            pr = degrade(gt, mode, mag, seed=s)
            mt = metrics(gt, pr)
            for k in vals:
                vals[k].append(mt[k])
        row = {"width": w}
        for k, v in vals.items():
            row[k] = float(np.mean(v)); row[k + "_sd"] = float(np.std(v))
        row["gap"] = row["clDice"] - row["IoU"]
        out.append(row)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="reports/controlled")
    ap.add_argument("--seeds", type=int, default=5)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    results = {}
    # 1) primary law: 1-px boundary error (dilation), width sweep
    results["dilate_1"] = sweep_width("dilate", 1, n_seeds=args.seeds)
    # 2) robustness: error magnitude
    for mag in [2, 3]:
        results[f"dilate_{mag}"] = sweep_width("dilate", mag, n_seeds=args.seeds)
    results["erode_1"] = sweep_width("erode", 1, n_seeds=args.seeds)
    results["shift_2"] = sweep_width("shift", 2, n_seeds=args.seeds)
    results["boundary_noise_0.3"] = sweep_width("boundary_noise", 0.3, n_seeds=args.seeds)
    results["gaps_0.5"] = sweep_width("gaps", 0.5, n_seeds=args.seeds)

    json.dump(results, open(os.path.join(args.out, "robustness_sweeps.json"), "w"), indent=2)
    print("primary law (dilate_1): width -> gap(clDice-IoU)")
    for r in results["dilate_1"]:
        print(f"  w={r['width']:5.1f}  IoU={r['IoU']:.3f}  clDice={r['clDice']:.3f}  "
              f"gap={r['gap']:+.3f}")
    print(f"\nWrote {args.out}/robustness_sweeps.json  ({len(results)} conditions)")


if __name__ == "__main__":
    main()
