#!/usr/bin/env python3
"""Generate publication-quality qualitative figures from a checkpoint.

Produces, for N test samples:
  * comparison panels (image | GT | pred | TP/FP/FN)
  * a dataset-level spatial error heatmap (FP/FN frequency)

    python scripts/visualize.py --config configs/experiment/smoke_miniunet.yaml \
        --checkpoint outputs/smoke_miniunet/best.pth --out reports/qualitative -n 6
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
from uavroadmark.viz import (accumulate_error_maps, comparison_panel,  # noqa: E402
                             error_heatmaps)


def _denormalize(tensor):
    """Undo ImageNet normalisation -> uint8 RGB for display."""
    img = tensor.permute(1, 2, 0).cpu().numpy()
    img = img * np.array(IMAGENET_STD) + np.array(IMAGENET_MEAN)
    return np.clip(img * 255, 0, 255).astype(np.uint8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--split", default="test")
    ap.add_argument("--out", default="reports/qualitative")
    ap.add_argument("-n", "--num", type=int, default=6)
    args = ap.parse_args()

    import torch

    cfg = load_config(args.config)
    seed_everything(cfg.get("seed", 42))
    d = cfg["dataset"]
    size = tuple(d.get("image_size", [256, 256]))
    ds = RoadMarkDataset(root=d["root"], split=args.split, num_classes=d["num_classes"],
                         transform=build_transforms("val", size),
                         class_map=d.get("class_map"), strict=d.get("strict", True))

    model = build_model_from_cfg(cfg)
    ckpt = torch.load(args.checkpoint, map_location="cpu")
    model.load_state_dict(ckpt["model"] if "model" in ckpt else ckpt)
    model.eval()

    os.makedirs(args.out, exist_ok=True)
    acc = accumulate_error_maps(*size)
    with torch.no_grad():
        for i in range(len(ds)):
            sample = ds[i]
            img_t, gt = sample["image"], sample["mask"].numpy()
            logits = model(img_t.unsqueeze(0))
            pred = torch.argmax(logits, dim=1)[0].numpy()
            acc.update(gt, pred)
            if i < args.num:
                rgb = _denormalize(img_t)
                comparison_panel(rgb, gt, pred,
                                 save_path=os.path.join(args.out, f"panel_{i:02d}.png"))

    error_heatmaps(acc, save_path=os.path.join(args.out, "error_heatmaps.png"))
    print(f"Wrote {min(args.num, len(ds))} panels + error_heatmaps.png to {args.out}")


if __name__ == "__main__":
    main()
