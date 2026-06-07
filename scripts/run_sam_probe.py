#!/usr/bin/env python3
"""Foundation-model (SAM / MobileSAM) zero-shot probe for thin road markings.

Runs an automatic-mask-generator over test images and measures how well SAM's
*class-agnostic* masks align with the GT marking centerlines (clDice / tolerance
recall). The hypothesis under test: SAM segments salient *blobs* well but under-
segments thin, low-contrast markings — making it a weak direct segmenter but a
useful *pseudo-labeler* when prompted at marking locations.

Requires `ultralytics` (bundles MobileSAM/SAM) OR `segment_anything`. Not run in
the constrained build environment (see reports/foundation_model_study.md for the
technical justification); ready to run where the package + weights are available.

    python scripts/run_sam_probe.py --root datasets/rlmd --backend ultralytics \
        --weights mobile_sam.pt -n 20 --out reports/visualizations/sam_probe
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from uavroadmark.data.dataset import pair_image_mask  # noqa: E402
from uavroadmark.metrics.thin_structure import cl_dice, tolerance_scores  # noqa: E402

import cv2  # noqa: E402


def load_sam(backend, weights):
    if backend == "ultralytics":
        from ultralytics import SAM
        return ("ultralytics", SAM(weights))
    if backend == "segment_anything":
        from segment_anything import sam_model_registry, SamAutomaticMaskGenerator
        sam = sam_model_registry["vit_b"](checkpoint=weights)
        return ("sa", SamAutomaticMaskGenerator(sam))
    raise SystemExit(f"unknown backend {backend}")


def sam_foreground(kind, model, img_bgr):
    """Union of SAM masks -> a single class-agnostic foreground map."""
    if kind == "ultralytics":
        res = model(img_bgr, verbose=False)
        fg = np.zeros(img_bgr.shape[:2], bool)
        for r in res:
            if r.masks is not None:
                for m in r.masks.data.cpu().numpy():
                    fg |= cv2.resize(m, (fg.shape[1], fg.shape[0])) > 0.5
        return fg
    masks = model.generate(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))
    fg = np.zeros(img_bgr.shape[:2], bool)
    for m in masks:
        fg |= m["segmentation"]
    return fg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--split", default="test")
    ap.add_argument("--backend", default="ultralytics")
    ap.add_argument("--weights", default="mobile_sam.pt")
    ap.add_argument("-n", "--num", type=int, default=20)
    ap.add_argument("--out", default="reports/visualizations/sam_probe")
    args = ap.parse_args()

    kind, model = load_sam(args.backend, args.weights)
    pairs = pair_image_mask(f"{args.root}/images/{args.split}",
                            f"{args.root}/masks/{args.split}")[: args.num]
    os.makedirs(args.out, exist_ok=True)
    cld, tol = [], []
    for img_p, msk_p, stem in pairs:
        img = cv2.imread(str(img_p))
        gt = cv2.imread(str(msk_p), cv2.IMREAD_UNCHANGED)
        gt_fg = (gt[..., 0] if gt.ndim == 3 else gt) > 0
        pred_fg = sam_foreground(kind, model, img)
        cld.append(cl_dice(gt_fg, pred_fg))
        tol.append(tolerance_scores(gt_fg, pred_fg, tau=3)["cl_recall"])
    summary = {"n": len(pairs), "mean_clDice": float(np.mean(cld)),
               "mean_centerline_recall": float(np.mean(tol)),
               "interpretation": "low clDice/recall => SAM under-segments thin markings"}
    json.dump(summary, open(os.path.join(args.out, "sam_probe.json"), "w"), indent=2)
    print(summary)


if __name__ == "__main__":
    main()
