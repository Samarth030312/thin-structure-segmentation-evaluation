"""Automated exploratory data analysis for a segmentation dataset.

Produces the statistics an AV data engineer actually needs before training:
class imbalance (the central challenge for road markings), per-image mask
coverage, and resolution spread. Saves both a JSON summary and PNG figures.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional

import cv2
import numpy as np

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except Exception:  # pragma: no cover
    plt = None


def _iter_masks(root: Path, splits):
    for split in splits:
        mdir = root / "masks" / split
        if not mdir.is_dir():
            continue
        for p in sorted(mdir.iterdir()):
            if p.suffix.lower() in {".png", ".tif", ".tiff", ".bmp"}:
                yield split, p


def analyze(root: str | Path, num_classes: int, splits=("train", "val", "test"),
            class_names: Optional[List[str]] = None) -> Dict:
    root = Path(root)
    class_pixels: Counter = Counter()
    coverage = []          # foreground fraction per image
    resolutions: Counter = Counter()
    per_split_counts: Dict[str, Counter] = {}

    for split, mp in _iter_masks(root, splits):
        m = cv2.imread(str(mp), cv2.IMREAD_UNCHANGED)
        if m is None:
            continue
        if m.ndim == 3:
            m = m[..., 0]
        resolutions[f"{m.shape[1]}x{m.shape[0]}"] += 1
        ids, counts = np.unique(m, return_counts=True)
        sc = per_split_counts.setdefault(split, Counter())
        for i, c in zip(ids, counts):
            class_pixels[int(i)] += int(c)
            sc[int(i)] += int(c)
        coverage.append(float((m > 0).mean()))

    total = max(1, sum(class_pixels.values()))
    fg_total = max(1, sum(v for k, v in class_pixels.items() if k > 0))
    # imbalance: ratio of most-common to least-common *foreground* class
    fg = {k: v for k, v in class_pixels.items() if k > 0}
    imbalance_ratio = (max(fg.values()) / max(1, min(fg.values()))) if fg else 0.0

    summary = {
        "root": str(root),
        "num_classes": num_classes,
        "class_names": class_names,
        "n_images": len(coverage),
        "class_pixel_share": {
            str(k): class_pixels.get(k, 0) / total for k in range(num_classes)},
        "foreground_class_share": {
            str(k): (class_pixels.get(k, 0) / fg_total) for k in range(1, num_classes)},
        "background_share": class_pixels.get(0, 0) / total,
        "imbalance_ratio_fg": imbalance_ratio,
        "mask_coverage": {
            "mean": float(np.mean(coverage)) if coverage else 0.0,
            "median": float(np.median(coverage)) if coverage else 0.0,
            "min": float(np.min(coverage)) if coverage else 0.0,
            "max": float(np.max(coverage)) if coverage else 0.0,
        },
        "resolutions": dict(resolutions),
    }
    return summary, coverage, class_pixels


def make_figures(summary: Dict, coverage, class_pixels, out_dir: str | Path,
                 class_names: Optional[List[str]] = None):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    nc = summary["num_classes"]
    # be robust to a class_names list that doesn't match num_classes
    names = class_names if (class_names and len(class_names) == nc) else [f"c{i}" for i in range(nc)]

    # 1) class pixel share (log scale exposes the imbalance)
    shares = [summary["class_pixel_share"].get(str(i), 0) for i in range(nc)]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(range(nc), shares, color="#0969da")
    ax.set_yscale("log")
    ax.set_xticks(range(nc))
    ax.set_xticklabels(names, rotation=45, ha="right")
    ax.set_ylabel("pixel share (log)")
    ax.set_title("Class pixel distribution (log scale)")
    fig.tight_layout()
    fig.savefig(out_dir / "class_distribution.png", dpi=150)
    plt.close(fig)

    # 2) foreground-only share (linear)
    fg_share = [summary["foreground_class_share"].get(str(i), 0) for i in range(1, nc)]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(range(1, nc), fg_share, color="#1a7f37")
    ax.set_xticks(range(1, nc))
    ax.set_xticklabels(names[1:], rotation=45, ha="right")
    ax.set_ylabel("share of foreground pixels")
    ax.set_title("Foreground class balance")
    fig.tight_layout()
    fig.savefig(out_dir / "foreground_balance.png", dpi=150)
    plt.close(fig)

    # 3) mask coverage histogram
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(np.array(coverage) * 100, bins=30, color="#8250df")
    ax.set_xlabel("foreground coverage per image (%)")
    ax.set_ylabel("# images")
    ax.set_title("Mask coverage distribution")
    fig.tight_layout()
    fig.savefig(out_dir / "mask_coverage.png", dpi=150)
    plt.close(fig)

    return [out_dir / "class_distribution.png", out_dir / "foreground_balance.png",
            out_dir / "mask_coverage.png"]


def run_eda(root, num_classes, out_dir, splits=("train", "val", "test"),
            class_names=None) -> Dict:
    summary, coverage, class_pixels = analyze(root, num_classes, splits, class_names)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "eda_summary.json").write_text(json.dumps(summary, indent=2))
    if plt is not None:
        make_figures(summary, coverage, class_pixels, out_dir, class_names)
    return summary
