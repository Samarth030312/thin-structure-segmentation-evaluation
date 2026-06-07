"""Reproducibility: seed all RNGs and optionally force deterministic kernels."""
from __future__ import annotations

import os
import random

import numpy as np


def seed_everything(seed: int = 42, deterministic: bool = True) -> int:
    """Seed python, numpy and (if available) torch.

    ``deterministic=True`` trades a little throughput for bit-reproducibility,
    which is the right default for a *benchmark* where fair comparison matters
    more than raw speed.
    """
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    try:
        import torch

        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        if deterministic:
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False
            # cuBLAS workspace config required for full determinism on CUDA>=10.2
            os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
    except ImportError:
        pass
    return seed
