"""Segmentation metrics entry point (``evaluation/metrics.py``).

This is a thin, stable re-export of the package's segmentation metrics so that
external scripts and graders can do ``from evaluation.metrics import compute_all``
without depending on the ``src/`` layout. The implementation lives in
``uavroadmark.metrics.segmentation`` (confusion-matrix based; see its docstring
for the methodology).
"""
from __future__ import annotations

import os
import sys

# Make the src/ package importable when this file is used standalone.
_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from uavroadmark.metrics.segmentation import (  # noqa: E402
    ConfusionMatrix,
    SegMetrics,
    compute_all,
    dice_score,
    iou_score,
    metrics_from_confusion,
)

__all__ = [
    "ConfusionMatrix",
    "SegMetrics",
    "compute_all",
    "dice_score",
    "iou_score",
    "metrics_from_confusion",
]
