#!/usr/bin/env python3
"""Ingest UAVid (HF parquet `arakesh/uavid-15-hq-mixedres`) into the folder
contract as a BINARY road segmentation task (road vs background), for the UAV
validation campaign. UAVid is genuine low-altitude UAV imagery; road has the
standard colour (128,64,128).

    python scripts/prepare_uavid.py --raw datasets/_real_raw/uavid_pq/data \
        --out datasets/uavid --size 768
"""
import argparse
import glob
import io
import os

import cv2
import numpy as np
import pyarrow.parquet as pq
from PIL import Image

ROAD_RGB = (128, 64, 128)  # UAVid road colour


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default="datasets/_real_raw/uavid_pq/data")
    ap.add_argument("--out", default="datasets/uavid")
    ap.add_argument("--size", type=int, default=768)
    args = ap.parse_args()

    counts = {"train": 0, "test": 0}
    mapped_px = total_px = 0
    for shard in sorted(glob.glob(os.path.join(args.raw, "*.parquet"))):
        split = "train" if "train" in os.path.basename(shard) else "test"
        idir = os.path.join(args.out, "images", split)
        mdir = os.path.join(args.out, "masks", split)
        os.makedirs(idir, exist_ok=True); os.makedirs(mdir, exist_ok=True)
        pf = pq.ParquetFile(shard)
        ri = 0
        for batch in pf.iter_batches(batch_size=4):
            d = batch.to_pydict()
            for i in range(len(d["image"])):
                img = np.array(Image.open(io.BytesIO(d["image"][i]["bytes"])).convert("RGB"))
                lab = np.array(Image.open(io.BytesIO(d["label"][i]["bytes"])).convert("RGB"))
                road = np.all(lab == ROAD_RGB, axis=-1).astype(np.uint8)  # binary road
                total_px += road.size; mapped_px += int(road.sum())
                img = cv2.resize(img, (args.size, args.size), interpolation=cv2.INTER_AREA)
                road = cv2.resize(road, (args.size, args.size), interpolation=cv2.INTER_NEAREST)
                stem = f"{os.path.basename(shard).split('.')[0]}_{ri:04d}"
                cv2.imwrite(os.path.join(idir, f"{stem}.png"), cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
                cv2.imwrite(os.path.join(mdir, f"{stem}.png"), road)
                counts[split] += 1; ri += 1
        print(f"{os.path.basename(shard)} -> {split}: {ri} frames")

    print(f"\nWrote {counts} -> {args.out}")
    print(f"Road pixel share: {100*mapped_px/max(1,total_px):.2f}%")
    print(f"Validate: python scripts/dataset_validator.py --root {args.out} --num-classes 2")


if __name__ == "__main__":
    main()
