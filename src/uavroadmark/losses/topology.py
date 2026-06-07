"""Topology / connectivity-aware losses for thin road markings.

This module contains the **training-side novelty** of the project:

1. ``SoftSkeletonize`` - a differentiable soft skeleton (Shit et al., CVPR 2021),
   built from iterative soft morphological erosion/dilation (min/max pooling).
2. ``SoftClDiceLoss`` - the soft centerline-Dice loss; optimises *topology*
   (connectivity) rather than pixel overlap, which is what makes a lane line a
   continuous curve instead of a dashed mess.
3. ``CoReLoss`` (**Connectivity-Recall loss, this work**) - a principled coupling
   of (a) a recall-weighted region term (soft Tversky, β>α) and (b) the soft
   clDice connectivity term. The thesis: thin safety-critical markings demand
   *both* high recall (don't miss a thin line) *and* topological continuity
   (don't break it). Existing losses optimise one or the other; CoRe optimises
   their combination, with the region term providing dense gradients that
   stabilise the otherwise-sparse skeleton gradients.

All losses consume **raw logits** ``(N, C, H, W)`` and int targets ``(N, H, W)``.
The connectivity terms operate on the **any-marking foreground** probability
(``1 - softmax[:, 0]``), the correct granularity for line topology.
"""
from __future__ import annotations

from typing import Optional

import torch
import torch.nn as nn
import torch.nn.functional as F

from . import LOSS_REGISTRY
from .functional import TverskyLoss

_EPS = 1e-6


class SoftSkeletonize(nn.Module):
    """Differentiable soft skeleton via iterative soft erosion/opening.

    Works on a probability map ``(N, 1, H, W)`` in [0, 1].
    """

    def __init__(self, num_iter: int = 10):
        super().__init__()
        self.num_iter = num_iter

    @staticmethod
    def _soft_erode(img):
        # min-pool = -max-pool(-x); use separable 3x1 / 1x3 for a cross SE
        p1 = -F.max_pool2d(-img, (3, 1), (1, 1), (1, 0))
        p2 = -F.max_pool2d(-img, (1, 3), (1, 1), (0, 1))
        return torch.min(p1, p2)

    @staticmethod
    def _soft_dilate(img):
        return F.max_pool2d(img, (3, 3), (1, 1), (1, 1))

    def _soft_open(self, img):
        return self._soft_dilate(self._soft_erode(img))

    def forward(self, img):
        img1 = self._soft_open(img)
        skel = F.relu(img - img1)
        for _ in range(self.num_iter):
            img = self._soft_erode(img)
            img1 = self._soft_open(img)
            delta = F.relu(img - img1)
            skel = skel + F.relu(delta - skel * delta)
        return skel


def _foreground_prob(logits: torch.Tensor) -> torch.Tensor:
    """P(any marking) = 1 - softmax[:, background] -> (N, 1, H, W)."""
    probs = torch.softmax(logits, dim=1)
    fg = 1.0 - probs[:, 0:1]
    return fg


def _foreground_target(target: torch.Tensor) -> torch.Tensor:
    return (target > 0).float().unsqueeze(1)


@LOSS_REGISTRY.register("cldice", "soft_cldice")
class SoftClDiceLoss(nn.Module):
    """Soft centerline-Dice loss on the any-marking foreground (topology term)."""

    def __init__(self, num_iter: int = 10, **_):
        super().__init__()
        self.skel = SoftSkeletonize(num_iter)

    def forward(self, logits, target):
        pred = _foreground_prob(logits)
        gt = _foreground_target(target).to(pred.dtype)
        skel_pred = self.skel(pred)
        skel_gt = self.skel(gt)
        tprec = (torch.sum(skel_pred * gt) + _EPS) / (torch.sum(skel_pred) + _EPS)
        tsens = (torch.sum(skel_gt * pred) + _EPS) / (torch.sum(skel_gt) + _EPS)
        cldice = 2.0 * tprec * tsens / (tprec + tsens + _EPS)
        return 1.0 - cldice


@LOSS_REGISTRY.register("core", "cltversky", "connectivity_recall")
class CoReLoss(nn.Module):
    """Connectivity-Recall loss (**proposed**).

    ``L = w_ce · CE + w_region · Region(α,β) + w_topo · (1 - softClDice)``

    Design rationale, informed by our own ablation (see
    ``reports/loss_function_analysis.md``):

    * A **CE term** provides background *calibration* - without it, recall-biased
      region losses over-predict foreground (we measured PixelAcc collapsing to
      ~0.51). CE supplies the dense, well-conditioned gradient that keeps false
      positives in check.
    * A **region term** (Dice by default, or recall-weighted **Tversky** when
      ``region='tversky'`` with α<β) drives overlap and, optionally, recall on
      thin markings.
    * The **soft-clDice term** enforces *connectivity/topology* of the
      any-marking foreground - the property mIoU is blind to.
    * ``warmup`` ramps the topology weight from 0 over N steps so the (initially
      meaningless) skeleton gradients do not destabilise early training.

    Thus CoRe = "the strong balanced baseline (CE+Dice) + explicit connectivity",
    a strict, principled extension rather than a replacement.
    """

    def __init__(self, w_ce: float = 0.5, w_region: float = 0.5, w_topo: float = 0.5,
                 region: str = "dice", alpha: float = 0.3, beta: float = 0.7,
                 num_iter: int = 10, ignore_index: Optional[int] = None,
                 foreground_only: bool = True, warmup: int = 0, **_):
        super().__init__()
        from .functional import CrossEntropyLoss, DiceLoss
        ce_ignore = ignore_index if (ignore_index is not None and ignore_index >= 0) else -100
        reg_ignore = ignore_index if (ignore_index is not None and ignore_index >= 0) else None
        self.ce = CrossEntropyLoss(ignore_index=ce_ignore)
        if region == "tversky":
            self.region = TverskyLoss(alpha=alpha, beta=beta, ignore_index=reg_ignore,
                                      foreground_only=foreground_only)
        else:
            self.region = DiceLoss(ignore_index=reg_ignore, foreground_only=foreground_only)
        self.topo = SoftClDiceLoss(num_iter=num_iter)
        self.w_ce, self.w_region = w_ce, w_region
        self.w_topo_target = w_topo
        self.warmup = max(0, warmup)
        self.register_buffer("_step", torch.zeros((), dtype=torch.long))

    def _topo_weight(self) -> float:
        if self.warmup == 0:
            return self.w_topo_target
        t = min(1.0, float(self._step.item()) / self.warmup)
        return self.w_topo_target * t

    def forward(self, logits, target):
        ce = self.ce(logits, target)
        region = self.region(logits, target)
        topo = self.topo(logits, target)
        w_topo = self._topo_weight()
        if self.training:
            self._step += 1
        return self.w_ce * ce + self.w_region * region + w_topo * topo
