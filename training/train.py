#!/usr/bin/env python3
"""Config-driven training entry point (``training/train.py``).

Thin wrapper around the config-driven trainer in
``uavroadmark.cli.train`` so the canonical path works without an editable
install::

    python training/train.py --config configs/experiment/uav_uavid.yaml
    python training/train.py --config configs/experiment/smoke_miniunet.yaml \
        --opt train.epochs=5 train.lr=3e-4
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from uavroadmark.cli.train import main  # noqa: E402

if __name__ == "__main__":
    main()
