#!/usr/bin/env python3
"""Grad-CAM class-activation maps for segmentation models.

For a chosen marking class, we backprop the (spatially-summed) class logit to the
deepest convolutional feature map and weight channels by their mean gradient
(Grad-CAM; Selvaraju et al., ICCV 2017). The resulting heatmap shows *where* the
network looks to predict that marking class - a interpretability check that the
model attends to the actual markings, not spurious asphalt texture.

    python scripts/run_gradcam.py --config configs/experiment/abl_unet_core.yaml \
        --checkpoint outputs/abl_unet_core/best.pth --class-id 1 -n 4 \
        --out reports/visualizations/gradcam
"""
import argparse
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from uavroadmark.build import build_model_from_cfg  # noqa: E402
from uavroadmark.data import RoadMarkDataset, build_transforms  # noqa: E402
from uavroadmark.data.transforms import IMAGENET_MEAN, IMAGENET_STD  # noqa: E402
from uavroadmark.utils import load_config, seed_everything  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def last_conv(model):
    """Return the last nn.Conv2d module in execution order (heuristic)."""
    import torch.nn as nn
    target = None
    for m in model.modules():
        if isinstance(m, nn.Conv2d):
            target = m
    return target


def _denorm(t):
    img = t.permute(1, 2, 0).cpu().numpy() * np.array(IMAGENET_STD) + np.array(IMAGENET_MEAN)
    return np.clip(img * 255, 0, 255).astype(np.uint8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--class-id", type=int, default=1)
    ap.add_argument("-n", "--num", type=int, default=4)
    ap.add_argument("--out", default="reports/visualizations/gradcam")
    args = ap.parse_args()

    import torch
    import torch.nn.functional as F

    cfg = load_config(args.config)
    seed_everything(cfg.get("seed", 42))
    device = "cuda" if torch.cuda.is_available() else "cpu"
    d = cfg["dataset"]
    size = tuple(d.get("image_size", [256, 256]))
    ds = RoadMarkDataset(d["root"], "test", build_transforms("val", size),
                         num_classes=d["num_classes"], strict=d.get("strict", True))
    model = build_model_from_cfg(cfg).to(device)
    ck = torch.load(args.checkpoint, map_location=device)
    model.load_state_dict(ck["model"] if "model" in ck else ck)
    model.eval()

    # hook the last conv feature map (Grad-CAM target layer)
    target_layer = last_conv(model)
    feats, grads = {}, {}

    def fwd_hook(_, __, output):
        feats["v"] = output

    def bwd_hook(_, grad_in, grad_out):
        grads["v"] = grad_out[0]

    h1 = target_layer.register_forward_hook(fwd_hook)
    h2 = target_layer.register_full_backward_hook(bwd_hook)

    os.makedirs(args.out, exist_ok=True)
    cls = args.class_id
    for i in range(min(args.num, len(ds))):
        sample = ds[i]
        x = sample["image"].unsqueeze(0).to(device).requires_grad_(False)
        model.zero_grad()
        logits = model(x)                              # 1xCxHxW
        score = logits[:, cls].sum()                   # spatially-summed class logit
        score.backward()

        A = feats["v"].detach()[0]                     # (K, h, w)
        dA = grads["v"].detach()[0]                    # (K, h, w)
        weights = dA.mean(dim=(1, 2))                  # (K,)
        cam = F.relu((weights[:, None, None] * A).sum(0))
        cam = cam / (cam.max() + 1e-7)
        cam = F.interpolate(cam[None, None], size=size, mode="bilinear",
                            align_corners=False)[0, 0].cpu().numpy()

        rgb = _denorm(sample["image"])
        fig, axes = plt.subplots(1, 2, figsize=(8, 4))
        axes[0].imshow(rgb); axes[0].set_title("input"); axes[0].axis("off")
        axes[1].imshow(rgb); axes[1].imshow(cam, cmap="jet", alpha=0.5)
        cname = (d.get("class_names") or [str(cls)])[cls] if d.get("class_names") else str(cls)
        axes[1].set_title(f"Grad-CAM: {cname}"); axes[1].axis("off")
        fig.tight_layout()
        fig.savefig(os.path.join(args.out, f"gradcam_{i:02d}_cls{cls}.png"), dpi=150)
        plt.close(fig)

    h1.remove(); h2.remove()
    print(f"Wrote {min(args.num, len(ds))} Grad-CAM maps (class {cls}) to {args.out}")


if __name__ == "__main__":
    main()
