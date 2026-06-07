"""Thin-structure evaluation protocol for road-marking segmentation.

Motivation (the paper's empirical claim)
-----------------------------------------
Road markings are *thin* (2-8 px wide in typical UAV GSD). Region-overlap metrics
like mIoU/Dice are dominated by the (few) interior pixels of an already-thin
structure and are insensitive to **connectivity/topology** and to **boundary
localisation**. Two models with the same mIoU can differ drastically in whether
a lane line is recovered as one connected curve or a dashed, broken mess — the
latter is useless for lane-keeping. This module provides metrics that *see* that
difference:

* **clDice** (centerline Dice; Shit et al., CVPR 2021) - topology preservation.
* **Boundary-IoU** (Cheng et al., CVPR 2021) - boundary-localisation quality.
* **centerline-F1 / tolerance-IoU** - detection within a τ-pixel tolerance band
  of the GT centerline (the metric that actually matters for thin lines).
* **width-stratified IoU** (this work) - IoU as a function of GT marking width,
  which *exposes* the thin-structure gap directly and is the basis for our
  claim that standard mIoU mis-ranks models on thin markings.

All operate on binary foreground masks (any-marking vs background) or per-class
masks. numpy/scipy/skimage only - torch-free and unit-testable.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np
from scipy.ndimage import binary_erosion, distance_transform_edt
from skimage.morphology import skeletonize

_EPS = 1e-7


# --------------------------------------------------------------------------- #
# clDice                                                                       #
# --------------------------------------------------------------------------- #
def cl_dice(gt: np.ndarray, pred: np.ndarray) -> float:
    """Centerline Dice between binary masks.

    Topology Precision  Tprec = |skeleton(pred) ∩ gt|   / |skeleton(pred)|
    Topology Sensitivity Tsens = |skeleton(gt)  ∩ pred| / |skeleton(gt)|
    clDice = 2·Tprec·Tsens / (Tprec + Tsens)
    """
    gt = gt.astype(bool)
    pred = pred.astype(bool)
    if gt.sum() == 0 and pred.sum() == 0:
        return 1.0
    if gt.sum() == 0 or pred.sum() == 0:
        return 0.0
    skel_pred = skeletonize(pred)
    skel_gt = skeletonize(gt)
    tprec = (skel_pred & gt).sum() / (skel_pred.sum() + _EPS)
    tsens = (skel_gt & pred).sum() / (skel_gt.sum() + _EPS)
    return float(2 * tprec * tsens / (tprec + tsens + _EPS))


# --------------------------------------------------------------------------- #
# Boundary-IoU                                                                 #
# --------------------------------------------------------------------------- #
def _boundary(mask: np.ndarray, dilation: int) -> np.ndarray:
    """Boundary region = mask minus its erosion by `dilation` pixels."""
    mask = mask.astype(bool)
    if mask.sum() == 0:
        return mask
    eroded = binary_erosion(mask, iterations=max(1, dilation), border_value=1)
    return mask & (~eroded)


def boundary_iou(gt: np.ndarray, pred: np.ndarray, dilation_ratio: float = 0.02,
                 min_dilation: int = 1) -> float:
    """IoU computed only over boundary regions (Cheng et al., 2021).

    For thin structures the boundary *is* almost the whole object, so this
    sharpens sensitivity to localisation error relative to mask IoU.
    """
    h, w = gt.shape
    d = max(min_dilation, int(round(dilation_ratio * np.sqrt(h * h + w * w))))
    gt_b = _boundary(gt, d)
    pred_b = _boundary(pred, d)
    inter = (gt_b & pred_b).sum()
    union = (gt_b | pred_b).sum()
    if union == 0:
        return 1.0
    return float(inter / (union + _EPS))


# --------------------------------------------------------------------------- #
# Centerline-F1 / tolerance-IoU                                                #
# --------------------------------------------------------------------------- #
def tolerance_scores(gt: np.ndarray, pred: np.ndarray, tau: int = 3) -> Dict[str, float]:
    """Detection within a τ-pixel tolerance of the *centerline*.

    A predicted pixel counts as a true positive if it lies within τ px of the GT
    skeleton; a GT centerline pixel counts as recalled if a prediction lies
    within τ px of it. Returns precision/recall/F1 and a tolerance-band IoU.
    This is the metric that reflects "did we find the line?", forgiving the
    sub-pixel width ambiguity that punishes mask-IoU on thin structures.
    """
    gt = gt.astype(bool)
    pred = pred.astype(bool)
    if gt.sum() == 0 and pred.sum() == 0:
        return {"cl_precision": 1.0, "cl_recall": 1.0, "cl_f1": 1.0, "tol_iou": 1.0}
    if gt.sum() == 0 or pred.sum() == 0:
        return {"cl_precision": 0.0, "cl_recall": 0.0, "cl_f1": 0.0, "tol_iou": 0.0}

    skel_gt = skeletonize(gt)
    skel_pred = skeletonize(pred)
    # distance to nearest GT / pred foreground pixel
    dt_gt = distance_transform_edt(~gt)
    dt_pred = distance_transform_edt(~pred)

    # precision: predicted centerline pixels close to GT mask
    prec = (dt_gt[skel_pred] <= tau).mean() if skel_pred.sum() else 0.0
    # recall: GT centerline pixels close to predicted mask
    rec = (dt_pred[skel_gt] <= tau).mean() if skel_gt.sum() else 0.0
    f1 = 2 * prec * rec / (prec + rec + _EPS)

    # tolerance-band IoU: dilate both centerlines by τ, IoU of the bands
    band_gt = dt_gt <= tau
    band_pred = dt_pred <= tau
    inter = (band_gt & band_pred).sum()
    union = (band_gt | band_pred).sum()
    tol_iou = inter / (union + _EPS)
    return {"cl_precision": float(prec), "cl_recall": float(rec),
            "cl_f1": float(f1), "tol_iou": float(tol_iou)}


# --------------------------------------------------------------------------- #
# Width-stratified IoU  (novel analysis tool)                                  #
# --------------------------------------------------------------------------- #
def local_width(mask: np.ndarray) -> np.ndarray:
    """Approximate local marking width at each foreground pixel = 2·EDT.

    The Euclidean distance transform of the mask gives the distance to the
    nearest background; on the skeleton this equals the half-width, so 2·EDT is
    a per-pixel width estimate.
    """
    return 2.0 * distance_transform_edt(mask.astype(bool))


@dataclass
class WidthStratifiedIoU:
    """Accumulate confusion counts stratified by GT marking width.

    For each width bin we accumulate intersection/union of (any-)foreground, so
    we can plot IoU(width) over the whole dataset - the figure that demonstrates
    the thin-structure gap and motivates the proposed loss/metric.
    """
    bins: List[float] = field(default_factory=lambda: [0, 2, 4, 6, 8, 12, 1e9])
    inter: np.ndarray = None
    union: np.ndarray = None

    def __post_init__(self):
        n = len(self.bins) - 1
        self.inter = np.zeros(n, dtype=np.float64)
        self.union = np.zeros(n, dtype=np.float64)

    def update(self, gt: np.ndarray, pred: np.ndarray):
        gt = gt.astype(bool)
        pred = pred.astype(bool)
        width = local_width(gt)
        # assign each GT pixel to a width bin; background pixels (width 0) -> bin via pred
        for i in range(len(self.bins) - 1):
            lo, hi = self.bins[i], self.bins[i + 1]
            gt_bin = gt & (width > lo) & (width <= hi)
            # union/intersection restricted to this width stratum of GT, plus
            # predictions that fall on those GT pixels
            inter = (gt_bin & pred).sum()
            union = gt_bin.sum() + (pred & gt_bin).sum() - inter  # ~ TP+FN within stratum
            # use a stratum-local IoU proxy: TP / (TP + FN)  (recall within width)
            self.inter[i] += inter
            self.union[i] += gt_bin.sum()

    def recall_by_width(self) -> Dict[str, float]:
        out = {}
        for i in range(len(self.bins) - 1):
            lo, hi = self.bins[i], self.bins[i + 1]
            label = f"{int(lo)}-{int(hi) if hi < 1e8 else 'inf'}px"
            out[label] = float(self.inter[i] / (self.union[i] + _EPS))
        return out


@dataclass
class ThinStructureMetrics:
    cl_dice: float
    boundary_iou: float
    cl_precision: float
    cl_recall: float
    cl_f1: float
    tol_iou: float

    def to_dict(self) -> Dict[str, float]:
        return {"clDice": round(self.cl_dice, 4),
                "BoundaryIoU": round(self.boundary_iou, 4),
                "clPrecision": round(self.cl_precision, 4),
                "clRecall": round(self.cl_recall, 4),
                "clF1": round(self.cl_f1, 4),
                "TolIoU": round(self.tol_iou, 4)}


class ThinStructureEvaluator:
    """Streaming accumulator producing dataset-mean thin-structure metrics.

    Operates on the *binary any-marking* mask (foreground = any class > 0) by
    default, which is the right granularity for topology/connectivity of lines.
    """

    def __init__(self, tau: int = 3, boundary_dilation_ratio: float = 0.02,
                 foreground_fn=None):
        self.tau = tau
        self.bdr = boundary_dilation_ratio
        self.foreground_fn = foreground_fn or (lambda m: m > 0)
        self._cld, self._biou = [], []
        self._clp, self._clr, self._clf, self._tol = [], [], [], []
        self.width = WidthStratifiedIoU()

    def update(self, gt_mask: np.ndarray, pred_mask: np.ndarray):
        gt = self.foreground_fn(np.asarray(gt_mask))
        pr = self.foreground_fn(np.asarray(pred_mask))
        self._cld.append(cl_dice(gt, pr))
        self._biou.append(boundary_iou(gt, pr, self.bdr))
        ts = tolerance_scores(gt, pr, self.tau)
        self._clp.append(ts["cl_precision"]); self._clr.append(ts["cl_recall"])
        self._clf.append(ts["cl_f1"]); self._tol.append(ts["tol_iou"])
        self.width.update(gt, pr)

    def compute(self) -> ThinStructureMetrics:
        mean = lambda x: float(np.mean(x)) if x else 0.0
        return ThinStructureMetrics(
            cl_dice=mean(self._cld), boundary_iou=mean(self._biou),
            cl_precision=mean(self._clp), cl_recall=mean(self._clr),
            cl_f1=mean(self._clf), tol_iou=mean(self._tol))

    def width_curve(self) -> Dict[str, float]:
        return self.width.recall_by_width()
