#!/usr/bin/env python3
"""Ingest Massachusetts Roads (HF `asolodin/massachusetts_roads_dataset_500`,
parquet) as BINARY road segmentation. Aerial imagery with THIN rural roads
(~3-4% pixels) -- the real aerial thin-structure test (SkyScapes substitute).

    python scripts/prepare_massroads.py --raw datasets/_real_raw/mass_roads/data \
        --out datasets/massroads --size 512 --cap-train 160 --cap-test 40
"""
import argparse
import glob
import io
import os

import cv2
import numpy as np
import pyarrow.parquet as pq
from PIL import Image


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default="datasets/_real_raw/mass_roads/data")
    ap.add_argument("--out", default="datasets/massroads")
    ap.add_argument("--size", type=int, default=512)
    ap.add_argument("--cap-train", type=int, default=160)
    ap.add_argument("--cap-test", type=int, default=40)
    args = ap.parse_args()

    counts = {"train": 0, "test": 0}
    fg = tot = 0
    for shard in sorted(glob.glob(os.path.join(args.raw, "*.parquet"))):
        split = "train" if "train" in os.path.basename(shard) else "test"
        cap = args.cap_train if split == "train" else args.cap_test
        if counts[split] >= cap:
            continue
        idir = os.path.join(args.out, "images", split)
        mdir = os.path.join(args.out, "masks", split)
        os.makedirs(idir, exist_ok=True); os.makedirs(mdir, exist_ok=True)
        pf = pq.ParquetFile(shard)
        for batch in pf.iter_batches(batch_size=8):
            d = batch.to_pydict()
            for i in range(len(d["image"])):
                if counts[split] >= cap:
                    break
                img = np.array(Image.open(io.BytesIO(d["image"][i]["bytes"])).convert("RGB"))
                lab = np.array(Image.open(io.BytesIO(d["label"][i]["bytes"])).convert("L"))
                road = (lab > 127).astype(np.uint8)
                # skip near-empty tiles (no road) so training sees the structure
                if road.mean() < 0.005:
                    continue
                fg += int(road.sum()); tot += road.size
                img = cv2.resize(img, (args.size, args.size), interpolation=cv2.INTER_AREA)
                road = cv2.resize(road, (args.size, args.size), interpolation=cv2.INTER_NEAREST)
                stem = f"{os.path.basename(shard).split('.')[0]}_{counts[split]:04d}"
                cv2.imwrite(os.path.join(idir, f"{stem}.png"), cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
                cv2.imwrite(os.path.join(mdir, f"{stem}.png"), road)
                counts[split] += 1
        print(f"{os.path.basename(shard)} -> {split}: now {counts[split]}")

    print(f"\nWrote {counts} -> {args.out}")
    print(f"Road pixel share: {100*fg/max(1,tot):.2f}% (thin if <5%)")


if __name__ == "__main__":
    main()
