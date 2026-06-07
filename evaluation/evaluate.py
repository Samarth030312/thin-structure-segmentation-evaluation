#!/usr/bin/env python3
"""Checkpoint evaluation entry point (``evaluation/evaluate.py``).

Wrapper around ``uavroadmark.cli.evaluate``. Evaluates a checkpoint on a split
and appends a ranked row to the leaderboard::

    python evaluation/evaluate.py \
        --config configs/experiment/uav_uavid.yaml \
        --checkpoint outputs/uav_uavid_s42/best.pth --split test
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from uavroadmark.cli.evaluate import main  # noqa: E402

if __name__ == "__main__":
    main()
