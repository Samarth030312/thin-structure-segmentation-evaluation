"""Model zoo with a single unified entry point: :func:`get_model`.

Supported (via segmentation_models_pytorch): ``unet``, ``unetpp``,
``deeplabv3plus``, ``pspnet``, ``segformer``.
Always available (pure-torch fallback, no smp needed): ``miniunet``.
"""
from __future__ import annotations

from ..utils.registry import Registry

MODEL_REGISTRY = Registry("model")


def get_model(name: str, num_classes: int = 2, in_channels: int = 3, **kwargs):
    """Construct a segmentation model by name.

    Parameters mirror the smp convention so configs stay backend-agnostic::

        get_model("deeplabv3plus", num_classes=8, encoder="resnet50",
                  pretrained=True)
    """
    from . import zoo  # noqa: F401  (registers factories on import)

    return MODEL_REGISTRY.get(
        name, num_classes=num_classes, in_channels=in_channels, **kwargs
    )


def available_models():
    from . import zoo  # noqa: F401

    return MODEL_REGISTRY.available()
