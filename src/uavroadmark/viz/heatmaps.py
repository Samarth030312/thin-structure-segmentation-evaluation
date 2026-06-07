"""Spatial error heatmaps aggregated over a dataset.

Accumulating false-positive / false-negative frequency *per pixel location*
across the whole test set reveals systematic spatial bias (e.g. a model that
always misses markings near the frame edge, where UAV lens distortion is worst).
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except Exception:  # pragma: no cover
    plt = None


class accumulate_error_maps:
    """Streaming accumulator for FP/FN/support maps at a fixed resolution."""

    def __init__(self, height: int, width: int):
        self.h, self.w = height, width
        self.fp = np.zeros((height, width), np.float64)
        self.fn = np.zeros((height, width), np.float64)
        self.support = np.zeros((height, width), np.float64)
        self.n = 0

    def update(self, gt: np.ndarray, pred: np.ndarray):
        gt_fg = gt > 0
        pred_fg = pred > 0
        self.fp += (~gt_fg) & pred_fg
        self.fn += gt_fg & (~pred_fg)
        self.support += gt_fg
        self.n += 1

    def normalized(self):
        denom = max(1, self.n)
        return self.fp / denom, self.fn / denom, self.support / denom


def error_heatmaps(acc: "accumulate_error_maps", save_path: Optional[str] = None):
    fp, fn, support = acc.normalized()
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    for ax, data, title, cmap in [
        (axes[0], support, "GT marking frequency", "viridis"),
        (axes[1], fp, "False-positive frequency", "Reds"),
        (axes[2], fn, "False-negative frequency", "Blues"),
    ]:
        im = ax.imshow(data, cmap=cmap)
        ax.set_title(title)
        ax.axis("off")
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.suptitle(f"Spatial error analysis over {acc.n} samples")
    fig.tight_layout()
    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
    return fig
