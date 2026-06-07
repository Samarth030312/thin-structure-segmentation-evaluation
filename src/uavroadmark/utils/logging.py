"""Consistent, timestamped console logging across all entry points."""
from __future__ import annotations

import logging
import sys

_CONFIGURED = False


def get_logger(name: str = "uavroadmark", level: int = logging.INFO) -> logging.Logger:
    global _CONFIGURED
    if not _CONFIGURED:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
                datefmt="%H:%M:%S",
            )
        )
        root = logging.getLogger("uavroadmark")
        root.addHandler(handler)
        root.setLevel(level)
        root.propagate = False
        _CONFIGURED = True
    return logging.getLogger(name if name.startswith("uavroadmark") else f"uavroadmark.{name}")
