"""Loss-function zoo for class-imbalanced segmentation.

See ``reports/loss_function_study.md`` for the mathematics and the rationale of
each loss for thin, sparse road markings. All losses operate on **raw logits**
(no sigmoid/softmax pre-applied) for numerical stability - this is the single
most important fix relative to the original notebook, which applied
``sigmoid`` and then ``BCELoss`` (a recipe for vanishing gradients and NaNs).
"""
from __future__ import annotations

from ..utils.registry import Registry

LOSS_REGISTRY = Registry("loss")


def get_loss(name: str, **kwargs):
    """Factory: ``get_loss("dice", ...)`` -> an ``nn.Module``.

    Imported lazily so that environments without torch can still import the
    package (e.g. for metrics-only unit tests).
    """
    from . import functional  # noqa: F401  (registers CE/Dice/Focal/Tversky/Combo)
    from . import topology    # noqa: F401  (registers clDice / CoRe)

    return LOSS_REGISTRY.get(name, **kwargs)


def available_losses():
    from . import functional  # noqa: F401
    from . import topology    # noqa: F401

    return LOSS_REGISTRY.available()
