"""Confusion-matrix based semantic-segmentation metrics (numpy, torch-free).

Why a confusion matrix?
-----------------------
Every standard segmentation metric (IoU, Dice/F1, precision, recall, pixel
accuracy) is a function of the per-class true-positive / false-positive /
false-negative pixel counts. Accumulating a single ``C x C`` confusion matrix
over the whole dataset lets us compute *dataset-level* (micro/macro) metrics
exactly, without the bias you get from naively averaging per-image scores
(small objects on small images otherwise dominate). This matches the
mmsegmentation / Cityscapes evaluation convention.

All inputs are integer label maps of identical shape; predictions are assumed
to be argmax class ids (not logits). An optional ``ignore_index`` removes
unlabeled / void pixels from every statistic.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

import numpy as np

_EPS = 1e-7


class ConfusionMatrix:
    """Streaming ``num_classes x num_classes`` confusion matrix.

    Row = ground-truth class, Column = predicted class.
    Update once per image (or per batch flattened) and read derived metrics
    at the end.
    """

    def __init__(self, num_classes: int, ignore_index: Optional[int] = None):
        if num_classes < 2:
            raise ValueError("num_classes must be >= 2 (binary uses 2 classes)")
        self.num_classes = num_classes
        self.ignore_index = ignore_index
        self.mat = np.zeros((num_classes, num_classes), dtype=np.int64)

    def reset(self) -> None:
        self.mat[:] = 0

    def update(self, target: np.ndarray, pred: np.ndarray) -> None:
        target = np.asarray(target).reshape(-1)
        pred = np.asarray(pred).reshape(-1)
        if target.shape != pred.shape:
            raise ValueError(
                f"target/pred shape mismatch: {target.shape} vs {pred.shape}"
            )
        valid = np.ones_like(target, dtype=bool)
        if self.ignore_index is not None:
            valid &= target != self.ignore_index
        # Guard against out-of-range predicted ids (e.g. a buggy model head).
        valid &= (pred >= 0) & (pred < self.num_classes)
        valid &= (target >= 0) & (target < self.num_classes)
        t = target[valid]
        p = pred[valid]
        # bincount on the flattened (C*t + p) index is the vectorised way to
        # build a confusion matrix - far faster than np.add.at in a loop.
        idx = self.num_classes * t + p
        binc = np.bincount(idx, minlength=self.num_classes**2)
        self.mat += binc.reshape(self.num_classes, self.num_classes)

    # ---- derived statistics -------------------------------------------------
    @property
    def tp(self) -> np.ndarray:
        return np.diag(self.mat).astype(np.float64)

    @property
    def fp(self) -> np.ndarray:
        return self.mat.sum(axis=0).astype(np.float64) - self.tp

    @property
    def fn(self) -> np.ndarray:
        return self.mat.sum(axis=1).astype(np.float64) - self.tp

    @property
    def support(self) -> np.ndarray:
        """Ground-truth pixel count per class (row sums)."""
        return self.mat.sum(axis=1).astype(np.float64)

    def per_class_iou(self) -> np.ndarray:
        denom = self.tp + self.fp + self.fn
        return self.tp / (denom + _EPS)

    def per_class_dice(self) -> np.ndarray:
        return 2 * self.tp / (2 * self.tp + self.fp + self.fn + _EPS)

    def per_class_precision(self) -> np.ndarray:
        return self.tp / (self.tp + self.fp + _EPS)

    def per_class_recall(self) -> np.ndarray:
        return self.tp / (self.tp + self.fn + _EPS)

    def pixel_accuracy(self) -> float:
        total = self.mat.sum()
        return float(self.tp.sum() / (total + _EPS))

    def freq_weighted_iou(self) -> float:
        freq = self.support / (self.support.sum() + _EPS)
        return float((freq * self.per_class_iou()).sum())


@dataclass
class SegMetrics:
    """A frozen snapshot of all metrics, ready to serialise to CSV/JSON."""

    per_class_iou: List[float]
    per_class_dice: List[float]
    per_class_precision: List[float]
    per_class_recall: List[float]
    per_class_f1: List[float]
    miou: float
    mdice: float
    mf1: float
    mprecision: float
    mrecall: float
    pixel_accuracy: float
    freq_weighted_iou: float
    class_names: Optional[List[str]] = None

    def to_dict(self) -> Dict:
        return {
            "miou": self.miou,
            "mdice": self.mdice,
            "mf1": self.mf1,
            "mprecision": self.mprecision,
            "mrecall": self.mrecall,
            "pixel_accuracy": self.pixel_accuracy,
            "freq_weighted_iou": self.freq_weighted_iou,
            "per_class_iou": self.per_class_iou,
            "per_class_dice": self.per_class_dice,
            "per_class_precision": self.per_class_precision,
            "per_class_recall": self.per_class_recall,
            "per_class_f1": self.per_class_f1,
            "class_names": self.class_names,
        }

    def headline(self) -> Dict[str, float]:
        """The columns that go into the leaderboard."""
        return {
            "mIoU": round(self.miou, 4),
            "mDice": round(self.mdice, 4),
            "mF1": round(self.mf1, 4),
            "mPrecision": round(self.mprecision, 4),
            "mRecall": round(self.mrecall, 4),
            "PixelAcc": round(self.pixel_accuracy, 4),
            "FWIoU": round(self.freq_weighted_iou, 4),
        }


def metrics_from_confusion(
    cm: ConfusionMatrix,
    class_names: Optional[List[str]] = None,
    foreground_only: bool = False,
) -> SegMetrics:
    """Reduce a confusion matrix to a :class:`SegMetrics` snapshot.

    ``foreground_only`` excludes class 0 (background) from the *mean* metrics.
    For road-marking segmentation the background dominates ~95-99% of pixels, so
    the foreground-mean is the scientifically honest headline number; we report
    both.
    """
    iou = cm.per_class_iou()
    dice = cm.per_class_dice()
    prec = cm.per_class_precision()
    rec = cm.per_class_recall()
    f1 = 2 * prec * rec / (prec + rec + _EPS)

    sel = slice(1, None) if (foreground_only and cm.num_classes > 1) else slice(None)
    return SegMetrics(
        per_class_iou=iou.tolist(),
        per_class_dice=dice.tolist(),
        per_class_precision=prec.tolist(),
        per_class_recall=rec.tolist(),
        per_class_f1=f1.tolist(),
        miou=float(np.nanmean(iou[sel])),
        mdice=float(np.nanmean(dice[sel])),
        mf1=float(np.nanmean(f1[sel])),
        mprecision=float(np.nanmean(prec[sel])),
        mrecall=float(np.nanmean(rec[sel])),
        pixel_accuracy=cm.pixel_accuracy(),
        freq_weighted_iou=cm.freq_weighted_iou(),
        class_names=class_names,
    )


# ---- convenience one-shot helpers (handy in tests / notebooks) -------------
def iou_score(target: np.ndarray, pred: np.ndarray, num_classes: int,
              ignore_index: Optional[int] = None) -> float:
    cm = ConfusionMatrix(num_classes, ignore_index)
    cm.update(target, pred)
    return float(np.nanmean(cm.per_class_iou()))


def dice_score(target: np.ndarray, pred: np.ndarray, num_classes: int,
               ignore_index: Optional[int] = None) -> float:
    cm = ConfusionMatrix(num_classes, ignore_index)
    cm.update(target, pred)
    return float(np.nanmean(cm.per_class_dice()))


def compute_all(target: np.ndarray, pred: np.ndarray, num_classes: int,
                class_names: Optional[List[str]] = None,
                ignore_index: Optional[int] = None,
                foreground_only: bool = False) -> SegMetrics:
    cm = ConfusionMatrix(num_classes, ignore_index)
    cm.update(target, pred)
    return metrics_from_confusion(cm, class_names, foreground_only)
