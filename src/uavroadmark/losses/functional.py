"""Concrete loss implementations, registered into ``LOSS_REGISTRY``.

Conventions
-----------
* ``logits``: ``(N, C, H, W)`` raw network outputs.
* ``target``: ``(N, H, W)`` int64 class ids.
* Region losses (Dice/Tversky) are computed on softmax probabilities but the
  gradient flows through the softmax, so we keep logits as the public API.
* Every loss honours ``ignore_index`` so void/unlabeled pixels never produce a
  gradient.
"""
from __future__ import annotations

from typing import Optional, Sequence

import torch
import torch.nn as nn
import torch.nn.functional as F

from . import LOSS_REGISTRY

_EPS = 1e-6


def _one_hot(target: torch.Tensor, num_classes: int, ignore_index: Optional[int]):
    """(N,H,W) -> (N,C,H,W) one-hot, with ignored pixels zeroed everywhere."""
    if ignore_index is not None:
        mask = target != ignore_index
        safe = target.clone()
        safe[~mask] = 0
        oh = F.one_hot(safe, num_classes).permute(0, 3, 1, 2).float()
        oh = oh * mask.unsqueeze(1).float()
        return oh, mask.unsqueeze(1).float()
    oh = F.one_hot(target, num_classes).permute(0, 3, 1, 2).float()
    return oh, torch.ones_like(oh[:, :1])


@LOSS_REGISTRY.register("ce", "crossentropy", "cross_entropy")
class CrossEntropyLoss(nn.Module):
    """Standard per-pixel softmax cross-entropy, optionally class-weighted."""

    def __init__(self, weight: Optional[Sequence[float]] = None,
                 ignore_index: int = -100, **_):
        super().__init__()
        w = torch.tensor(weight, dtype=torch.float32) if weight is not None else None
        self.register_buffer("weight", w)
        self.ignore_index = -100 if ignore_index is None else ignore_index

    def forward(self, logits: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        return F.cross_entropy(
            logits, target, weight=self.weight, ignore_index=self.ignore_index
        )


@LOSS_REGISTRY.register("dice")
class DiceLoss(nn.Module):
    """Soft multiclass Dice loss = 1 - mean_c Dice_c.

    Region-based, so it is *scale invariant*: a thin lane marking contributes as
    much as a large background blob, which directly attacks class imbalance.
    """

    def __init__(self, ignore_index: Optional[int] = None,
                 foreground_only: bool = True, **_):
        super().__init__()
        self.ignore_index = ignore_index
        self.foreground_only = foreground_only

    def forward(self, logits: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        num_classes = logits.shape[1]
        probs = torch.softmax(logits, dim=1)
        oh, mask = _one_hot(target, num_classes, self.ignore_index)
        probs = probs * mask
        dims = (0, 2, 3)
        inter = (probs * oh).sum(dims)
        card = probs.sum(dims) + oh.sum(dims)
        dice = (2 * inter + _EPS) / (card + _EPS)
        if self.foreground_only and num_classes > 1:
            dice = dice[1:]
        return 1.0 - dice.mean()


@LOSS_REGISTRY.register("focal")
class FocalLoss(nn.Module):
    r"""Multiclass focal loss: ``-(1-p_t)^gamma * log(p_t)``.

    Down-weights easy (well-classified) pixels so the abundant, easy background
    stops swamping the gradient. ``gamma=2`` is the canonical Lin et al. value.
    """

    def __init__(self, gamma: float = 2.0, alpha: Optional[Sequence[float]] = None,
                 ignore_index: int = -100, **_):
        super().__init__()
        self.gamma = gamma
        a = torch.tensor(alpha, dtype=torch.float32) if alpha is not None else None
        self.register_buffer("alpha", a)
        self.ignore_index = -100 if ignore_index is None else ignore_index

    def forward(self, logits: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        logp = F.log_softmax(logits, dim=1)
        ce = F.nll_loss(
            logp, target, weight=self.alpha,
            ignore_index=self.ignore_index, reduction="none",
        )
        pt = torch.exp(-ce)
        loss = (1 - pt) ** self.gamma * ce
        return loss.mean()


@LOSS_REGISTRY.register("tversky")
class TverskyLoss(nn.Module):
    r"""Tversky loss - a Dice generalisation that weights FP vs FN separately.

    ``alpha`` penalises false positives, ``beta`` false negatives. For road
    markings we under-detect (markings are thin), so ``beta > alpha`` (e.g.
    0.3 / 0.7) pushes recall up. ``alpha=beta=0.5`` recovers Dice.
    """

    def __init__(self, alpha: float = 0.3, beta: float = 0.7,
                 ignore_index: Optional[int] = None,
                 foreground_only: bool = True, **_):
        super().__init__()
        self.alpha, self.beta = alpha, beta
        self.ignore_index = ignore_index
        self.foreground_only = foreground_only

    def forward(self, logits: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        num_classes = logits.shape[1]
        probs = torch.softmax(logits, dim=1)
        oh, mask = _one_hot(target, num_classes, self.ignore_index)
        probs = probs * mask
        dims = (0, 2, 3)
        tp = (probs * oh).sum(dims)
        fp = (probs * (1 - oh)).sum(dims)
        fn = ((1 - probs) * oh).sum(dims)
        tversky = (tp + _EPS) / (tp + self.alpha * fp + self.beta * fn + _EPS)
        if self.foreground_only and num_classes > 1:
            tversky = tversky[1:]
        return 1.0 - tversky.mean()


@LOSS_REGISTRY.register("focal_tversky", "focaltversky")
class FocalTverskyLoss(TverskyLoss):
    r"""Focal-Tversky loss: ``(1 - Tversky)^gamma`` (Abraham & Khan, 2019).

    The ``gamma>1`` exponent focuses learning on hard, low-overlap classes -
    helpful for the rarest markings (e.g. arrows at ~6% of foreground).
    """

    def __init__(self, alpha: float = 0.3, beta: float = 0.7, gamma: float = 1.33,
                 ignore_index: Optional[int] = None, foreground_only: bool = True, **_):
        super().__init__(alpha=alpha, beta=beta, ignore_index=ignore_index,
                         foreground_only=foreground_only)
        self.gamma = gamma

    def forward(self, logits, target):
        tversky_loss = super().forward(logits, target)   # = 1 - mean tversky
        return tversky_loss.clamp(min=_EPS) ** self.gamma


@LOSS_REGISTRY.register("lovasz", "lovasz_softmax")
class LovaszSoftmaxLoss(nn.Module):
    """Lovász-Softmax loss (Berman et al., CVPR 2018): a convex surrogate that
    directly optimises the (multiclass) IoU via the Lovász extension of the
    Jaccard loss. Strong for segmentation, especially mid-frequency classes."""

    def __init__(self, ignore_index: Optional[int] = None,
                 foreground_only: bool = False, **_):
        super().__init__()
        self.ignore_index = ignore_index
        self.foreground_only = foreground_only

    @staticmethod
    def _grad(gt_sorted):
        p = len(gt_sorted)
        gts = gt_sorted.sum()
        intersection = gts - gt_sorted.float().cumsum(0)
        union = gts + (1 - gt_sorted).float().cumsum(0)
        jaccard = 1.0 - intersection / union
        if p > 1:
            jaccard[1:p] = jaccard[1:p] - jaccard[0:-1]
        return jaccard

    def forward(self, logits, target):
        probs = torch.softmax(logits, dim=1)
        n, c, h, w = probs.shape
        probs = probs.permute(0, 2, 3, 1).reshape(-1, c)
        labels = target.reshape(-1)
        if self.ignore_index is not None:
            valid = labels != self.ignore_index
            probs, labels = probs[valid], labels[valid]
        losses = []
        class_range = range(1, c) if self.foreground_only else range(c)
        for cl in class_range:
            fg = (labels == cl).float()
            if fg.sum() == 0:
                continue
            errors = (fg - probs[:, cl]).abs()
            errors_sorted, perm = torch.sort(errors, dim=0, descending=True)
            fg_sorted = fg[perm]
            losses.append(torch.dot(errors_sorted, self._grad(fg_sorted)))
        if not losses:
            return probs.sum() * 0.0
        return torch.stack(losses).mean()


@LOSS_REGISTRY.register("ce_dice", "bce_dice", "combo")
class ComboLoss(nn.Module):
    """Weighted sum of cross-entropy and Dice.

    The pragmatic default for imbalanced segmentation: CE gives smooth,
    well-conditioned pixel-wise gradients (good optimisation), Dice supplies the
    region-level, imbalance-robust signal. ``w_ce*CE + w_dice*Dice``.
    """

    def __init__(self, w_ce: float = 0.5, w_dice: float = 0.5,
                 weight: Optional[Sequence[float]] = None,
                 ignore_index: int = -100, **_):
        super().__init__()
        self.w_ce, self.w_dice = w_ce, w_dice
        self.ce = CrossEntropyLoss(weight=weight, ignore_index=ignore_index)
        dice_ignore = ignore_index if ignore_index is not None and ignore_index >= 0 else None
        self.dice = DiceLoss(ignore_index=dice_ignore)

    def forward(self, logits: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        return self.w_ce * self.ce(logits, target) + self.w_dice * self.dice(logits, target)
