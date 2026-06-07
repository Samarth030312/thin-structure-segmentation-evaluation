"""Deterministic synthetic thin road-marking dataset generator.

Purpose
-------
Real road-marking / aerial datasets (RLMD, LoveDA, Massachusetts Roads, UAVid)
are ingested by the scripts in ``scripts/`` for the actual experiments. To make
the *entire* framework runnable and CI-testable without a download - and to
provide a width-*controlled* benchmark where structure width is an independent
variable - we synthesise a small, deterministic dataset that reproduces the
defining statistical properties of thin road-marking imagery:

* nadir / oblique gray asphalt background that dominates the frame,
* thin, sparse foreground markings (severe class imbalance, ~1-4% pixels),
* the marking taxonomy actually used on roads (lane lines solid/dashed,
  zebra crossings, arrows, stop lines, yellow median lines),
* photometric nuisance: shadows, texture noise, brightness variation.

It is *not* a substitute for real data for headline science, but it is a
faithful, reproducible stand-in that exercises every code path. Swap in the
real dataset via the same folder contract (see ``RoadMarkDataset``) and every
command produces the real numbers unchanged.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

import cv2
import numpy as np

# Canonical taxonomy (id -> name, RGB for visualisation).
CLASSES: List[Tuple[int, str, Tuple[int, int, int]]] = [
    (0, "background", (0, 0, 0)),
    (1, "solid_lane_line", (220, 220, 220)),
    (2, "dashed_lane_line", (0, 255, 255)),
    (3, "zebra_crossing", (255, 0, 255)),
    (4, "road_arrow", (255, 128, 0)),
    (5, "stop_line", (0, 0, 255)),
    (6, "yellow_line", (255, 255, 0)),
]
NUM_CLASSES = len(CLASSES)
CLASS_NAMES = [c[1] for c in CLASSES]
PALETTE = np.array([c[2] for c in CLASSES], dtype=np.uint8)


def _asphalt(h: int, w: int, rng: np.random.Generator) -> np.ndarray:
    base = rng.integers(70, 105)
    img = np.full((h, w, 3), base, dtype=np.int16)
    img += rng.integers(-12, 12, size=(h, w, 1))  # per-pixel grain
    # low-frequency illumination gradient (sun angle)
    gy = np.linspace(rng.uniform(-20, 20), rng.uniform(-20, 20), h)[:, None]
    gx = np.linspace(rng.uniform(-15, 15), rng.uniform(-15, 15), w)[None, :]
    img += (gy + gx).astype(np.int16)[..., None]
    return np.clip(img, 0, 255).astype(np.uint8)


def _paint(mask, img, pts, cls, color, thickness, rng):
    """Stamp a marking onto both the mask (class id) and the RGB image."""
    cv2.polylines(mask, [pts], False, int(cls), thickness)
    # markings are bright but weathered: jitter the painted intensity
    jitter = rng.integers(-25, 10)
    c = tuple(int(np.clip(v + jitter, 0, 255)) for v in color)
    cv2.polylines(img, [pts], False, c, thickness)


def generate_sample(idx: int, h: int = 256, w: int = 256, seed: int = 0,
                    width_scale: float = 1.0
                    ) -> Tuple[np.ndarray, np.ndarray]:
    """Return ``(image_rgb_uint8, mask_uint8)`` for sample ``idx``.

    ``width_scale`` multiplies every marking thickness. This is the *controlled
    variable* for the thin-structure study: rendering the same scene geometry at
    width_scale in {0.5, 1, 1.5, 2} produces markings of known, varying width so
    we can measure IoU(width) and prove the thin-structure gap with ground-truth
    width control.
    """
    rng = np.random.default_rng(seed + idx * 7919)
    img = _asphalt(h, w, rng)
    mask = np.zeros((h, w), dtype=np.uint8)

    def _w(base):  # scaled, clamped odd-ish thickness >= 1
        return max(1, int(round(base * width_scale)))

    # 1-3 longitudinal lane lines (solid white / yellow / dashed)
    n_lanes = rng.integers(1, 4)
    for _ in range(n_lanes):
        x = rng.integers(int(0.15 * w), int(0.85 * w))
        drift = rng.integers(-30, 30)
        pts = np.array([[x, 0], [x + drift, h]], np.int32)
        roll = rng.random()
        if roll < 0.4:
            _paint(mask, img, pts, 1, (235, 235, 235), _w(4), rng)        # solid white
        elif roll < 0.7:
            _paint(mask, img, pts, 6, (245, 215, 40), _w(4), rng)         # yellow median
        else:                                                          # dashed white
            for y0 in range(0, h, 40):
                seg = np.array([[x + drift * y0 // h, y0],
                                [x + drift * (y0 + 22) // h, y0 + 22]], np.int32)
                _paint(mask, img, seg, 2, (235, 235, 235), _w(4), rng)

    # zebra crossing (band of thick stripes) on ~35% of frames
    if rng.random() < 0.35:
        y0 = rng.integers(int(0.5 * h), int(0.8 * h))
        for sx in range(int(0.2 * w), int(0.8 * w), 18):
            pts = np.array([[sx, y0], [sx, y0 + 30]], np.int32)
            _paint(mask, img, pts, 3, (240, 240, 240), _w(8), rng)

    # stop line on ~30% of frames
    if rng.random() < 0.30:
        y0 = rng.integers(int(0.45 * h), int(0.65 * h))
        pts = np.array([[int(0.2 * w), y0], [int(0.8 * w), y0]], np.int32)
        _paint(mask, img, pts, 5, (235, 235, 235), _w(6), rng)

    # directional arrow on ~30% of frames (a simple chevron + shaft)
    if rng.random() < 0.30:
        cx = rng.integers(int(0.3 * w), int(0.7 * w))
        cy = rng.integers(int(0.3 * h), int(0.6 * h))
        shaft = np.array([[cx, cy + 25], [cx, cy - 20]], np.int32)
        head = np.array([[cx - 12, cy - 5], [cx, cy - 22], [cx + 12, cy - 5]], np.int32)
        _paint(mask, img, shaft, 4, (235, 235, 235), _w(5), rng)
        _paint(mask, img, head, 4, (235, 235, 235), _w(5), rng)

    # soft cast shadow (photometric nuisance, no label change)
    if rng.random() < 0.4:
        ov = img.copy()
        x0 = rng.integers(0, w)
        cv2.rectangle(ov, (x0, 0), (min(w, x0 + rng.integers(30, 90)), h),
                      (0, 0, 0), -1)
        img = cv2.addWeighted(img, 0.75, ov, 0.25, 0)

    return img, mask


def colorize_mask(mask: np.ndarray) -> np.ndarray:
    """Map a class-id mask to an RGB visualisation using the palette."""
    return PALETTE[np.clip(mask, 0, NUM_CLASSES - 1)]


def build_dataset(root: str | Path, n_train=24, n_val=8, n_test=8,
                  h=256, w=256, seed=42, width_scale: float = 1.0) -> Dict[str, int]:
    """Write an image/mask dataset to ``root`` following the folder contract::

        root/images/{train,val,test}/*.png
        root/masks/{train,val,test}/*.png   (single-channel class ids)

    Returns a dict of split -> count. Deterministic given ``seed``.
    """
    root = Path(root)
    counts = {}
    offset = 0
    for split, n in [("train", n_train), ("val", n_val), ("test", n_test)]:
        img_dir = root / "images" / split
        msk_dir = root / "masks" / split
        img_dir.mkdir(parents=True, exist_ok=True)
        msk_dir.mkdir(parents=True, exist_ok=True)
        for i in range(n):
            img, mask = generate_sample(offset + i, h, w, seed, width_scale)
            stem = f"{split}_{i:04d}"
            cv2.imwrite(str(img_dir / f"{stem}.png"),
                        cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
            cv2.imwrite(str(msk_dir / f"{stem}.png"), mask)
        counts[split] = n
        offset += n
    return counts


def build_width_series(root: str | Path, widths=(0.5, 1.0, 1.5, 2.0),
                       n_per_width=12, h=256, w=256, seed=123) -> Dict[str, int]:
    """Build controlled test sets at fixed marking widths for the thin-structure
    study. Writes ``root/width_<scale>/{images,masks}/test/*.png``. The *same
    scene seeds* are used across widths, so width is the only varying factor -
    a clean controlled experiment for measuring IoU(width).
    """
    root = Path(root)
    counts = {}
    for ws in widths:
        tag = f"width_{ws:g}".replace(".", "p")
        img_dir = root / tag / "images" / "test"
        msk_dir = root / tag / "masks" / "test"
        img_dir.mkdir(parents=True, exist_ok=True)
        msk_dir.mkdir(parents=True, exist_ok=True)
        for i in range(n_per_width):
            img, mask = generate_sample(i, h, w, seed, width_scale=ws)
            stem = f"test_{i:04d}"
            cv2.imwrite(str(img_dir / f"{stem}.png"),
                        cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
            cv2.imwrite(str(msk_dir / f"{stem}.png"), mask)
        counts[tag] = n_per_width
    return counts


if __name__ == "__main__":  # pragma: no cover
    import argparse

    ap = argparse.ArgumentParser(description="Generate synthetic UAV road-mark data")
    ap.add_argument("--root", default="datasets/synthetic")
    ap.add_argument("--train", type=int, default=24)
    ap.add_argument("--val", type=int, default=8)
    ap.add_argument("--test", type=int, default=8)
    ap.add_argument("--size", type=int, default=256)
    args = ap.parse_args()
    c = build_dataset(args.root, args.train, args.val, args.test,
                      args.size, args.size)
    print(f"Wrote synthetic dataset to {args.root}: {c}")
