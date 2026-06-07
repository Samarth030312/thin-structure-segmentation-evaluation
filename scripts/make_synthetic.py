#!/usr/bin/env python3
"""Generate the deterministic synthetic UAV road-marking dataset.

This makes the whole framework runnable without the (non-redistributable) real
dataset. See ``uavroadmark.data.synthetic`` for the design rationale.

    python scripts/make_synthetic.py --root datasets/synthetic
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from uavroadmark.data.synthetic import build_dataset  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="datasets/synthetic")
    ap.add_argument("--train", type=int, default=24)
    ap.add_argument("--val", type=int, default=8)
    ap.add_argument("--test", type=int, default=8)
    ap.add_argument("--size", type=int, default=256)
    args = ap.parse_args()
    counts = build_dataset(args.root, args.train, args.val, args.test,
                           args.size, args.size)
    print(f"Synthetic dataset written to {args.root}: {counts}")


if __name__ == "__main__":
    main()
