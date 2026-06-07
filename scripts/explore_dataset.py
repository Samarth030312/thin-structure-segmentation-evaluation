#!/usr/bin/env python3
"""Run automated EDA and write reports to ``reports/exploratory_analysis/``."""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from uavroadmark.data.synthetic import CLASS_NAMES  # noqa: E402
from uavroadmark.report.explore import run_eda  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="datasets/synthetic")
    ap.add_argument("--num-classes", type=int, default=7)
    ap.add_argument("--out", default="reports/exploratory_analysis")
    ap.add_argument("--class-names", nargs="*", default=CLASS_NAMES)
    args = ap.parse_args()
    summary = run_eda(args.root, args.num_classes, args.out,
                      class_names=args.class_names)
    print(f"EDA complete. background share = {summary['background_share']:.4f}, "
          f"fg imbalance ratio = {summary['imbalance_ratio_fg']:.1f}")
    print(f"Figures + summary in {args.out}")


if __name__ == "__main__":
    main()
