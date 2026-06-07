#!/usr/bin/env python3
"""Ingest the raw SkyScapes-Lane (DLR) dataset into this framework's folder
contract: tile the huge aerial images, map labels to contiguous class ids, split
into train/val/test, and write images/<split> + masks/<split>.

Two sub-commands
----------------
  inspect  - scan raw masks and report whether they are grayscale-id or RGB, the
             unique values/colors, and per-class pixel counts. Run this FIRST to
             confirm the label format and (for RGB) build/verify the colormap.
  prepare  - tile + remap + split + write the folder contract.

Raw layout (defaults; override with flags)::

    <raw>/images/*.{tif,png,jpg}
    <raw>/labels/*.png            # grayscale id  OR  RGB colour masks
    (image and label share a filename stem, optionally with a label suffix)

Examples
--------
    python scripts/prepare_skyscapes.py inspect --raw datasets/skyscapes_raw
    python scripts/prepare_skyscapes.py prepare --raw datasets/skyscapes_raw \
        --out datasets/skyscapes --label-mode id --tile 512 --stride 512 \
        --keep-empty-frac 0.1
    # RGB masks:
    python scripts/prepare_skyscapes.py prepare --raw datasets/skyscapes_raw \
        --out datasets/skyscapes --label-mode rgb \
        --colormap configs/skyscapes_colormap.json --tile 512

See docs/skyscapes.md for the full walkthrough.
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

IMG_EXTS = (".tif", ".tiff", ".png", ".jpg", ".jpeg")
MASK_EXTS = (".png", ".tif", ".tiff", ".bmp")


# --------------------------------------------------------------------------- #
# file pairing                                                                #
# --------------------------------------------------------------------------- #
def _index(folder, exts, strip_suffix=""):
    out = {}
    folder = Path(folder)
    if not folder.is_dir():
        return out
    for p in sorted(folder.rglob("*")):
        if p.suffix.lower() in exts:
            stem = p.stem
            if strip_suffix and stem.endswith(strip_suffix):
                stem = stem[: -len(strip_suffix)]
            out[stem] = p
    return out


def pair(raw, image_dir, label_dir, label_suffix):
    images = _index(Path(raw) / image_dir, IMG_EXTS)
    labels = _index(Path(raw) / label_dir, MASK_EXTS, strip_suffix=label_suffix)
    common = sorted(set(images) & set(labels))
    if not common:
        raise SystemExit(
            f"No image/label pairs found under {raw} "
            f"(images={len(images)}, labels={len(labels)}). "
            f"Check --image-dir/--label-dir/--label-suffix.")
    return [(images[s], labels[s], s) for s in common]


# --------------------------------------------------------------------------- #
# label decoding                                                              #
# --------------------------------------------------------------------------- #
def load_colormap(path):
    cm = json.load(open(path))
    lut = {tuple(c["color"]): c["id"] for c in cm["classes"]}
    return lut, cm.get("ignore_index", 255)


def rgb_to_id(mask_rgb, lut, ignore_index):
    """Map an HxWx3 RGB mask to an HxW id mask using an exact-colour LUT."""
    h, w = mask_rgb.shape[:2]
    out = np.full((h, w), ignore_index, dtype=np.uint8)
    # vectorised: pack RGB into a single int key
    packed = (mask_rgb[..., 0].astype(np.uint32) << 16) | \
             (mask_rgb[..., 1].astype(np.uint32) << 8) | mask_rgb[..., 2].astype(np.uint32)
    for (r, g, b), cid in lut.items():
        key = (r << 16) | (g << 8) | b
        out[packed == key] = cid
    return out


def read_label(path, label_mode, lut, ignore_index):
    m = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if m is None:
        raise IOError(f"cannot read label {path}")
    if label_mode == "rgb":
        if m.ndim == 2:
            raise SystemExit(f"{path} is single-channel but --label-mode rgb was set.")
        m = cv2.cvtColor(m, cv2.COLOR_BGR2RGB)
        return rgb_to_id(m, lut, ignore_index)
    # id mode
    if m.ndim == 3:
        m = m[..., 0]
    return m.astype(np.uint8)


# --------------------------------------------------------------------------- #
# inspect                                                                     #
# --------------------------------------------------------------------------- #
def cmd_inspect(args):
    pairs = pair(args.raw, args.image_dir, args.label_dir, args.label_suffix)
    print(f"Found {len(pairs)} image/label pairs.")
    n = min(args.sample, len(pairs))
    rgb_votes = 0
    id_counter, color_counter = Counter(), Counter()
    for _, lab_p, _ in pairs[:n]:
        m = cv2.imread(str(lab_p), cv2.IMREAD_UNCHANGED)
        if m is None:
            continue
        if m.ndim == 3 and not (np.all(m[..., 0] == m[..., 1]) and np.all(m[..., 1] == m[..., 2])):
            rgb_votes += 1
            rgb = cv2.cvtColor(m, cv2.COLOR_BGR2RGB).reshape(-1, 3)
            for col, cnt in zip(*np.unique(rgb, axis=0, return_counts=True)):
                color_counter[tuple(int(x) for x in col)] += int(cnt)
        else:
            if m.ndim == 3:
                m = m[..., 0]
            for v, cnt in zip(*np.unique(m, return_counts=True)):
                id_counter[int(v)] += int(cnt)
    is_rgb = rgb_votes > n / 2
    print(f"\nDetected label format: {'RGB colour masks' if is_rgb else 'grayscale id masks'}"
          f"  (sampled {n} files)")
    if is_rgb:
        print("Unique colours (RGB -> pixel count), most common first:")
        for col, cnt in color_counter.most_common(20):
            print(f"  {col}  {cnt:,}")
        print("\n=> put these colours into a colormap JSON (see "
              "configs/skyscapes_colormap.json) and use --label-mode rgb")
    else:
        print("Unique ids (id -> pixel count):")
        for v, cnt in sorted(id_counter.items()):
            print(f"  {v:3d}  {cnt:,}")
        print(f"\n=> max id = {max(id_counter)}; expected 0..12 for SkyScapes-Lane. "
              "Use --label-mode id. If ordering differs from configs/dataset/skyscapes.yaml, "
              "set dataset.class_map there.")


# --------------------------------------------------------------------------- #
# prepare (tiling + split)                                                    #
# --------------------------------------------------------------------------- #
def split_of(stem, ratios=(0.8, 0.1, 0.1)):
    h = int(hashlib.md5(stem.encode()).hexdigest(), 16) % 1000 / 1000.0
    if h < ratios[0]:
        return "train"
    if h < ratios[0] + ratios[1]:
        return "val"
    return "test"


def cmd_prepare(args):
    lut, cm_ignore = (None, args.ignore_index)
    if args.label_mode == "rgb":
        if not args.colormap:
            raise SystemExit("--label-mode rgb requires --colormap")
        lut, cm_ignore = load_colormap(args.colormap)

    split_file = None
    if args.split_file and os.path.exists(args.split_file):
        split_file = json.load(open(args.split_file))
        stem2split = {s: sp for sp, stems in split_file.items() for s in stems}

    pairs = pair(args.raw, args.image_dir, args.label_dir, args.label_suffix)
    out = Path(args.out)
    rng = np.random.default_rng(args.seed)
    counts = Counter()
    tile, stride = args.tile, args.stride or args.tile

    for img_p, lab_p, stem in pairs:
        img = cv2.imread(str(img_p), cv2.IMREAD_COLOR)
        if img is None:
            print(f"  skip unreadable image {img_p}")
            continue
        lab = read_label(lab_p, args.label_mode, lut, cm_ignore)
        if img.shape[:2] != lab.shape[:2]:
            lab = cv2.resize(lab, (img.shape[1], img.shape[0]),
                             interpolation=cv2.INTER_NEAREST)
        split = (stem2split.get(stem) if split_file else split_of(stem, tuple(args.ratios)))
        if split is None:
            continue
        H, W = img.shape[:2]
        ti = 0
        for y in range(0, max(1, H - tile + 1), stride):
            for x in range(0, max(1, W - tile + 1), stride):
                img_t = img[y:y + tile, x:x + tile]
                lab_t = lab[y:y + tile, x:x + tile]
                if img_t.shape[0] != tile or img_t.shape[1] != tile:
                    continue
                fg = np.isin(lab_t, range(1, args.num_classes)).mean()
                if fg == 0 and rng.random() > args.keep_empty_frac:
                    continue  # drop most all-background tiles (sparse markings)
                idir = out / "images" / split
                mdir = out / "masks" / split
                idir.mkdir(parents=True, exist_ok=True)
                mdir.mkdir(parents=True, exist_ok=True)
                name = f"{stem}_{y:05d}_{x:05d}.png"
                cv2.imwrite(str(idir / name), img_t)
                cv2.imwrite(str(mdir / name), lab_t)
                counts[split] += 1
                ti += 1
                if args.max_tiles_per_image and ti >= args.max_tiles_per_image:
                    break
            if args.max_tiles_per_image and ti >= args.max_tiles_per_image:
                break
        print(f"  {stem}: {ti} tiles -> {split}")

    print(f"\nDone. Tiles written: {dict(counts)} -> {out}")
    print("Next: validate, then train:")
    print(f"  python scripts/dataset_validator.py --root {out} --num-classes "
          f"{args.num_classes} --ignore-index {args.ignore_index}")
    print("  uavrm-train --config configs/experiment/skyscapes_unetpp_core.yaml")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--raw", required=True, help="raw SkyScapes root")
    common.add_argument("--image-dir", default="images")
    common.add_argument("--label-dir", default="labels")
    common.add_argument("--label-suffix", default="",
                        help="suffix on label stems to strip, e.g. '_label'")

    pi = sub.add_parser("inspect", parents=[common])
    pi.add_argument("--sample", type=int, default=8)
    pi.set_defaults(func=cmd_inspect)

    pp = sub.add_parser("prepare", parents=[common])
    pp.add_argument("--out", default="datasets/skyscapes")
    pp.add_argument("--label-mode", choices=["id", "rgb"], default="id")
    pp.add_argument("--colormap", default=None)
    pp.add_argument("--num-classes", type=int, default=13)
    pp.add_argument("--ignore-index", type=int, default=255)
    pp.add_argument("--tile", type=int, default=512)
    pp.add_argument("--stride", type=int, default=0, help="0 -> = tile (no overlap)")
    pp.add_argument("--keep-empty-frac", type=float, default=0.1,
                    help="fraction of all-background tiles to keep (markings are sparse)")
    pp.add_argument("--max-tiles-per-image", type=int, default=0)
    pp.add_argument("--ratios", type=float, nargs=3, default=[0.8, 0.1, 0.1])
    pp.add_argument("--split-file", default=None,
                    help="optional JSON {train:[stems],val:[...],test:[...]}")
    pp.add_argument("--seed", type=int, default=42)
    pp.set_defaults(func=cmd_prepare)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
