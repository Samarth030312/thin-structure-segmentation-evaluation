"""Statistical-rigor utilities: bootstrap confidence intervals and paired
significance testing over per-image metric samples.

A single mIoU number is an anecdote; a mIoU with a 95% CI, and a paired test
saying model A beats model B with p<0.05, is evidence. These helpers operate on
*per-image* metric arrays (one value per test image) so claims like "CoRe > CE+Dice
on clDice" can be backed by a confidence interval and a p-value.
"""
from __future__ import annotations

from typing import Dict, Sequence, Tuple

import numpy as np


def bootstrap_ci(values: Sequence[float], n_boot: int = 10000,
                 alpha: float = 0.05, seed: int = 0) -> Dict[str, float]:
    """Percentile bootstrap CI for the mean of a per-image metric sample."""
    v = np.asarray(values, dtype=np.float64)
    if v.size == 0:
        return {"mean": float("nan"), "lo": float("nan"), "hi": float("nan"), "n": 0}
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, v.size, size=(n_boot, v.size))
    boot_means = v[idx].mean(axis=1)
    lo, hi = np.quantile(boot_means, [alpha / 2, 1 - alpha / 2])
    return {"mean": float(v.mean()), "lo": float(lo), "hi": float(hi),
            "std": float(v.std(ddof=1)) if v.size > 1 else 0.0, "n": int(v.size)}


def paired_bootstrap_test(a: Sequence[float], b: Sequence[float],
                          n_boot: int = 10000, seed: int = 0) -> Dict[str, float]:
    """Paired bootstrap test of H0: mean(a) == mean(b) on matched per-image
    samples (a[i], b[i] are the same image under two models). Returns the mean
    difference, its 95% CI, and a two-sided bootstrap p-value."""
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    if a.shape != b.shape or a.size == 0:
        raise ValueError("a and b must be matched, non-empty arrays")
    d = a - b
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, d.size, size=(n_boot, d.size))
    boot = d[idx].mean(axis=1)
    lo, hi = np.quantile(boot, [0.025, 0.975])
    # two-sided p: fraction of bootstrap means on the opposite side of 0
    centered = boot - boot.mean()
    p = 2.0 * min((centered >= abs(d.mean())).mean(), (centered <= -abs(d.mean())).mean())
    return {"mean_diff": float(d.mean()), "lo": float(lo), "hi": float(hi),
            "p_value": float(min(1.0, p)), "n": int(d.size),
            "significant_0.05": bool(lo > 0 or hi < 0)}


def fmt_ci(ci: Dict[str, float], pct: bool = False) -> str:
    s = 100 if pct else 1
    u = "%" if pct else ""
    return f"{ci['mean']*s:.2f}{u} [{ci['lo']*s:.2f}, {ci['hi']*s:.2f}]"
