#!/usr/bin/env python3
"""Dataset validation entry point (``scripts/dataset_validator.py``).

Runnable wrapper around :mod:`uavroadmark.report.validator`. Example::

    python scripts/dataset_validator.py \
        --root datasets/synthetic --num-classes 7 \
        --class-names background solid_lane_line dashed_lane_line \
                      zebra_crossing road_arrow stop_line yellow_line
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from uavroadmark.cli.validate import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
