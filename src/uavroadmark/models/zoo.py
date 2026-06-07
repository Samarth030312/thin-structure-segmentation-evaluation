"""Model factories. smp-backed architectures + a native U-Net fallback.

All factories return a plain ``nn.Module`` whose ``forward`` yields raw logits
of shape ``(N, num_classes, H, W)`` - a single, uniform contract so the trainer
and evaluator never special-case an architecture.
"""
from __future__ import annotations

import warnings

import torch
import torch.nn as nn

from . import MODEL_REGISTRY


def _smp():
    try:
        import segmentation_models_pytorch as smp
        return smp
    except ImportError as e:  # pragma: no cover - exercised only without smp
        raise ImportError(
            "segmentation_models_pytorch is required for this architecture. "
            "Install with `pip install segmentation-models-pytorch`, or use "
            "model name 'miniunet' which has no smp dependency."
        ) from e


def _encoder_weights(pretrained: bool) -> str | None:
    return "imagenet" if pretrained else None


def _smp_factory(builder_name: str):
    def _factory(num_classes=2, in_channels=3, encoder="resnet34",
                 pretrained=True, **kwargs):
        smp = _smp()
        builder = getattr(smp, builder_name)
        return builder(
            encoder_name=encoder,
            encoder_weights=_encoder_weights(pretrained),
            in_channels=in_channels,
            classes=num_classes,
            **kwargs,
        )
    return _factory


MODEL_REGISTRY.register("unet")(_smp_factory("Unet"))
MODEL_REGISTRY.register("unetpp", "unetplusplus", "unet++")(_smp_factory("UnetPlusPlus"))
MODEL_REGISTRY.register("deeplabv3plus", "deeplabv3+")(_smp_factory("DeepLabV3Plus"))
MODEL_REGISTRY.register("pspnet")(_smp_factory("PSPNet"))


@MODEL_REGISTRY.register("segformer")
def _segformer(num_classes=2, in_channels=3, encoder="mit_b0",
               pretrained=True, **kwargs):
    """SegFormer via smp (MiT encoder). Falls back gracefully if the smp
    version is too old to expose the Segformer head."""
    smp = _smp()
    if not hasattr(smp, "Segformer"):
        raise ImportError(
            "Your segmentation_models_pytorch is too old for SegFormer "
            "(needs >=0.3.3). Upgrade smp or pick another model."
        )
    return smp.Segformer(
        encoder_name=encoder,
        encoder_weights=_encoder_weights(pretrained),
        in_channels=in_channels,
        classes=num_classes,
        **kwargs,
    )


# --------------------------------------------------------------------------- #
# Native fallback: a compact U-Net with zero third-party model deps.          #
# Keeps the whole framework runnable (CI, smoke tests) without smp/internet.  #
# --------------------------------------------------------------------------- #
class _DoubleConv(nn.Module):
    def __init__(self, cin, cout):
        super().__init__()
        self.block = nn.Sequential(
            nn.Conv2d(cin, cout, 3, padding=1, bias=False),
            nn.BatchNorm2d(cout),
            nn.ReLU(inplace=True),
            nn.Conv2d(cout, cout, 3, padding=1, bias=False),
            nn.BatchNorm2d(cout),
            nn.ReLU(inplace=True),
        )

    def forward(self, x):
        return self.block(x)


class MiniUNet(nn.Module):
    """A small but real U-Net (encoder-decoder + skip connections)."""

    def __init__(self, num_classes=2, in_channels=3, base=32, depth=4):
        super().__init__()
        self.depth = depth
        chans = [base * (2**i) for i in range(depth)]
        self.downs = nn.ModuleList()
        prev = in_channels
        for c in chans:
            self.downs.append(_DoubleConv(prev, c))
            prev = c
        self.pool = nn.MaxPool2d(2)
        self.bottleneck = _DoubleConv(chans[-1], chans[-1] * 2)
        self.ups = nn.ModuleList()
        self.up_convs = nn.ModuleList()
        prev = chans[-1] * 2
        for c in reversed(chans):
            self.ups.append(nn.ConvTranspose2d(prev, c, 2, stride=2))
            self.up_convs.append(_DoubleConv(c * 2, c))
            prev = c
        self.head = nn.Conv2d(chans[0], num_classes, 1)

    def forward(self, x):
        skips = []
        for down in self.downs:
            x = down(x)
            skips.append(x)
            x = self.pool(x)
        x = self.bottleneck(x)
        for up, conv, skip in zip(self.ups, self.up_convs, reversed(skips)):
            x = up(x)
            if x.shape[-2:] != skip.shape[-2:]:
                x = nn.functional.interpolate(
                    x, size=skip.shape[-2:], mode="bilinear", align_corners=False
                )
            x = conv(torch.cat([skip, x], dim=1))
        return self.head(x)


@MODEL_REGISTRY.register("miniunet", "mini_unet")
def _miniunet(num_classes=2, in_channels=3, pretrained=False, base=32,
              depth=4, **kwargs):
    if pretrained:
        warnings.warn("miniunet has no pretrained weights; training from scratch.")
    return MiniUNet(num_classes=num_classes, in_channels=in_channels,
                    base=base, depth=depth)
