"""Evaluation engine: run a model over a loader and accumulate a confusion matrix.

Returns a :class:`~uavroadmark.metrics.SegMetrics` snapshot. Kept separate from
training so it can be called standalone (``uavrm-eval``) on a checkpoint.
"""
from __future__ import annotations

from typing import Optional

import numpy as np

from ..metrics.segmentation import ConfusionMatrix, metrics_from_confusion
from ..metrics.thin_structure import ThinStructureEvaluator


class Evaluator:
    def __init__(self, num_classes: int, ignore_index: Optional[int] = None,
                 class_names=None, foreground_only: bool = True,
                 thin_structure: bool = True, tau: int = 3):
        self.num_classes = num_classes
        self.ignore_index = ignore_index
        self.class_names = class_names
        self.foreground_only = foreground_only
        self.thin_structure = thin_structure
        self.tau = tau

    @staticmethod
    def _to_numpy(t):
        return t.detach().cpu().numpy()

    def run(self, model, loader, device="cpu"):
        import torch

        model.eval()
        cm = ConfusionMatrix(self.num_classes, self.ignore_index)
        tse = ThinStructureEvaluator(tau=self.tau) if self.thin_structure else None
        with torch.no_grad():
            for batch in loader:
                images = batch["image"].to(device)
                masks = batch["mask"]
                logits = model(images)
                preds = torch.argmax(logits, dim=1)
                m_np = self._to_numpy(masks)
                p_np = self._to_numpy(preds)
                cm.update(m_np, p_np)
                if tse is not None:
                    for gt_i, pr_i in zip(m_np, p_np):   # per-image for topology
                        tse.update(gt_i, pr_i)
        seg = metrics_from_confusion(cm, self.class_names, self.foreground_only)
        thin = tse.compute() if tse is not None else None
        width = tse.width_curve() if tse is not None else None
        return seg, cm, thin, width


def evaluate_model(model, loader, num_classes, device="cpu",
                   ignore_index=None, class_names=None, foreground_only=True,
                   thin_structure=True, tau=3):
    ev = Evaluator(num_classes, ignore_index, class_names, foreground_only,
                   thin_structure, tau)
    seg, cm, thin, width = ev.run(model, loader, device)
    return seg, cm, thin, width
