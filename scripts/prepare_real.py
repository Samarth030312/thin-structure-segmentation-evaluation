#!/usr/bin/env python3
"""Generic real-dataset ingestion -> this framework's folder contract.

Handles datasets shipped as `images/<split>/*.jpg` + `labels/<split>/*.png`
(RLMD layout) or flat folders, with RGB-colour or grayscale-id masks. Supports
**whole-image resize** (driving scenes) or **tiling** (huge aerial frames), and
preserves existing splits or carves a test split from train.

Examples
--------
    # RLMD (RGB masks, official train/val splits, downscale whole image):
    python scripts/prepare_real.py --raw datasets/_real_raw/RLMD/RLMD_1080p \
        --out datasets/rlmd --label-mode rgb --colormap configs/rlmd_colormap.json \
        --resize 512 512 --num-classes 25 --carve-test 0.15

    # aerial tiles:
    python scripts/prepare_real.py --raw <raw> --out datasets/foo \
        --label-mode id --tile 512 --stride 512
"""
import argparse
import hashlib
import json
import os
import sys
from collections import Counter
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from uavroadmark.data.dataset import IMG_EXTS, MASK_EXTS  # noqa: E402

# reuse the colour->id mapper from the skyscapes script
_spec_path = os.path.join(os.path.dirname(__file__), "prepare_skyscapes.py")
import importlib.util  # noqa: E402
_spec = importlib.util.spec_from_file_location("prepare_skyscapes", _spec_path)
_ps = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_ps)
load_colormap, read_label = _ps.load_colormap, _ps.read_label


def find_splits(img_root: Path):
    subs = [d.name for d in sorted(img_root.iterdir()) if d.is_dir()]
    return subs or [None]  # None = flat (no split subdirs)


def list_pairs(img_dir: Path, lab_dir: Path):
    imgs = {p.stem: p for p in sorted(img_dir.iterdir()) if p.suffix.lower() in IMG_EXTS}
    labs = {p.stem: p for p in sorted(lab_dir.iterdir()) if p.suffix.lower() in MASK_EXTS}
    return [(imgs[s], labs[s], s) for s in sorted(set(imgs) & set(labs))]


def carve(stem, frac):
    h = int(hashlib.md5(stem.encode()).hexdigest(), 16) % 1000 / 1000.0
    return "test" if h < frac else "train"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--image-subdir", default="images")
    ap.add_argument("--label-subdir", default="labels")
    ap.add_argument("--label-mode", choices=["id", "rgb"], default="rgb")
    ap.add_argument("--colormap", default=None)
    ap.add_argument("--num-classes", type=int, required=True)
    ap.add_argument("--ignore-index", type=int, default=255)
    ap.add_argument("--resize", type=int, nargs=2, default=None, help="H W (whole-image)")
    ap.add_argument("--tile", type=int, default=0)
    ap.add_argument("--stride", type=int, default=0)
    ap.add_argument("--carve-test", type=float, default=0.0,
                    help="if no test split, move this frac of train -> test")
    ap.add_argument("--max-images", type=int, default=0, help="cap (debug)")
    args = ap.parse_args()

    lut, ig = (None, args.ignore_index)
    if args.label_mode == "rgb":
        if not args.colormap:
            raise SystemExit("--label-mode rgb requires --colormap")
        lut, ig = load_colormap(args.colormap)

    raw = Path(args.raw)
    img_root, lab_root = raw / args.image_subdir, raw / args.label_subdir
    splits = find_splits(img_root)
    out = Path(args.out)
    counts, mapped_px, total_px = Counter(), 0, 0
    n_done = 0

    for split in splits:
        img_dir = img_root / split if split else img_root
        lab_dir = lab_root / split if split else lab_root
        if not lab_dir.is_dir():
            continue
        for img_p, lab_p, stem in list_pairs(img_dir, lab_dir):
            img = cv2.imread(str(img_p), cv2.IMREAD_COLOR)
            lab = read_label(lab_p, args.label_mode, lut, ig)
            if img is None or lab is None:
                continue
            if img.shape[:2] != lab.shape[:2]:
                lab = cv2.resize(lab, (img.shape[1], img.shape[0]),
                                 interpolation=cv2.INTER_NEAREST)
            total_px += lab.size
            mapped_px += int((lab != ig).sum())

            dst_split = split or "train"
            if dst_split == "train" and args.carve_test > 0:
                dst_split = carve(stem, args.carve_test)

            def _emit(im, lb, name, sp):
                idir, mdir = out / "images" / sp, out / "masks" / sp
                idir.mkdir(parents=True, exist_ok=True); mdir.mkdir(parents=True, exist_ok=True)
                cv2.imwrite(str(idir / name), im); cv2.imwrite(str(mdir / name), lb)

            if args.tile:
                stride = args.stride or args.tile
                H, W = img.shape[:2]; ti = 0
                for y in range(0, max(1, H - args.tile + 1), stride):
                    for x in range(0, max(1, W - args.tile + 1), stride):
                        it, lt = img[y:y+args.tile, x:x+args.tile], lab[y:y+args.tile, x:x+args.tile]
                        if it.shape[:2] != (args.tile, args.tile):
                            continue
                        _emit(it, lt, f"{stem}_{y}_{x}.png", dst_split); ti += 1
                counts[dst_split] += ti
            else:
                if args.resize:
                    h, w = args.resize
                    img = cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA)
                    lab = cv2.resize(lab, (w, h), interpolation=cv2.INTER_NEAREST)
                _emit(img, lab, f"{stem}.png", dst_split)
                counts[dst_split] += 1
            n_done += 1
            if args.max_images and n_done >= args.max_images:
                break
        if args.max_images and n_done >= args.max_images:
            break

    cov = 100 * mapped_px / max(1, total_px)
    print(f"\nWrote {dict(counts)} -> {out}")
    print(f"Label coverage (non-ignore pixels): {cov:.1f}% "
          f"({'OK' if cov > 60 else 'LOW - check colormap!'})")
    print(f"Validate: python scripts/dataset_validator.py --root {out} "
          f"--num-classes {args.num_classes} --ignore-index {args.ignore_index}")


if __name__ == "__main__":
    main()
