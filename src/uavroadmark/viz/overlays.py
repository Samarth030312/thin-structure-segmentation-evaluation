"""Publication-quality overlays for qualitative analysis.

All functions are numpy-in / numpy-(or file)-out and never require torch, so
they can be reused from notebooks, the evaluator, or report generation.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional, Sequence, Tuple

import numpy as np

try:
    import matplotlib
    matplotlib.use("Agg")  # headless-safe
    import matplotlib.pyplot as plt
except Exception:  # pragma: no cover
    plt = None

from ..data.synthetic import PALETTE as _DEFAULT_PALETTE


def overlay_mask(image: np.ndarray, mask: np.ndarray, palette: np.ndarray = None,
                 alpha: float = 0.5) -> np.ndarray:
    """Alpha-blend a class-id mask onto an RGB image (background stays clear)."""
    palette = _DEFAULT_PALETTE if palette is None else palette
    color = palette[np.clip(mask, 0, len(palette) - 1)]
    out = image.astype(np.float32).copy()
    fg = mask > 0
    out[fg] = (1 - alpha) * out[fg] + alpha * color[fg]
    return np.clip(out, 0, 255).astype(np.uint8)


def _save(fig, save_path: Optional[str]):
    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
    return fig


def ground_truth_overlay(image, mask, save_path=None, title="Ground Truth"):
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.imshow(overlay_mask(image, mask))
    ax.set_title(title)
    ax.axis("off")
    return _save(fig, save_path)


def prediction_overlay(image, pred, save_path=None, title="Prediction"):
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.imshow(overlay_mask(image, pred))
    ax.set_title(title)
    ax.axis("off")
    return _save(fig, save_path)


def failure_overlay(image, gt, pred, save_path=None):
    """Colour-code TP (green), false-positive (red), false-negative (blue).

    This is the single most useful qualitative diagnostic: it instantly shows
    *where* and *how* a model fails on thin structures.
    """
    h, w = gt.shape
    canvas = image.astype(np.float32).copy()
    gt_fg, pred_fg = gt > 0, pred > 0
    tp = gt_fg & pred_fg
    fp = (~gt_fg) & pred_fg
    fn = gt_fg & (~pred_fg)
    overlay = np.zeros((h, w, 3), np.float32)
    overlay[tp] = (0, 255, 0)
    overlay[fp] = (255, 0, 0)
    overlay[fn] = (0, 0, 255)
    m = tp | fp | fn
    canvas[m] = 0.4 * canvas[m] + 0.6 * overlay[m]
    canvas = np.clip(canvas, 0, 255).astype(np.uint8)

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.imshow(canvas)
    ax.set_title("Failure analysis  (green=TP  red=FP  blue=FN)")
    ax.axis("off")
    return _save(fig, save_path)


def comparison_panel(image, gt, pred, save_path=None,
                     extra: Optional[Sequence[Tuple[str, np.ndarray]]] = None):
    """Side-by-side: image | GT overlay | pred overlay | failure map."""
    panels = [("Image", image),
              ("Ground Truth", overlay_mask(image, gt)),
              ("Prediction", overlay_mask(image, pred))]
    n = len(panels) + 1 + (len(extra) if extra else 0)
    fig, axes = plt.subplots(1, n, figsize=(4 * n, 4))
    for ax, (title, im) in zip(axes, panels):
        ax.imshow(im)
        ax.set_title(title)
        ax.axis("off")
    # failure map
    h, w = gt.shape
    fmap = np.zeros((h, w, 3), np.uint8)
    fmap[(gt > 0) & (pred > 0)] = (0, 255, 0)
    fmap[(gt == 0) & (pred > 0)] = (255, 0, 0)
    fmap[(gt > 0) & (pred == 0)] = (0, 0, 255)
    axes[3].imshow(fmap)
    axes[3].set_title("TP/FP/FN")
    axes[3].axis("off")
    if extra:
        for ax, (title, im) in zip(axes[4:], extra):
            ax.imshow(im)
            ax.set_title(title)
            ax.axis("off")
    fig.tight_layout()
    return _save(fig, save_path)
