"""Tests for statistical utilities, dataset subsampling, and the FLOPs counter."""
import numpy as np
import pytest

from uavroadmark.metrics.stats import (bootstrap_ci, fmt_ci,
                                       paired_bootstrap_test)


def test_bootstrap_ci_brackets_mean():
    rng = np.random.default_rng(0)
    x = rng.normal(0.8, 0.05, size=200)
    ci = bootstrap_ci(x, n_boot=2000, seed=1)
    assert ci["lo"] < ci["mean"] < ci["hi"]
    assert abs(ci["mean"] - 0.8) < 0.02
    assert ci["n"] == 200


def test_bootstrap_ci_empty():
    ci = bootstrap_ci([], n_boot=100)
    assert ci["n"] == 0


def test_paired_test_detects_real_difference():
    rng = np.random.default_rng(0)
    a = rng.normal(0.85, 0.03, 150)
    b = a - 0.05            # a is consistently better by 0.05
    res = paired_bootstrap_test(a, b, n_boot=2000)
    assert res["mean_diff"] == pytest.approx(0.05, abs=0.005)
    assert res["significant_0.05"] is True
    assert res["lo"] > 0


def test_paired_test_no_difference_not_significant():
    rng = np.random.default_rng(1)
    a = rng.normal(0.8, 0.05, 150)
    b = rng.normal(0.8, 0.05, 150)
    res = paired_bootstrap_test(a, b, n_boot=2000)
    assert res["significant_0.05"] is False


def test_fmt_ci_string():
    s = fmt_ci({"mean": 0.5, "lo": 0.4, "hi": 0.6}, pct=True)
    assert "%" in s and "50.00" in s


def test_dataset_subsample(tmp_path):
    from uavroadmark.data.synthetic import build_dataset
    from uavroadmark.data import RoadMarkDataset, build_transforms
    build_dataset(tmp_path, n_train=20, n_val=4, n_test=4, h=64, w=64)
    full = RoadMarkDataset(tmp_path, "train", build_transforms("val", (64, 64)), num_classes=7)
    sub = RoadMarkDataset(tmp_path, "train", build_transforms("val", (64, 64)),
                          num_classes=7, subsample=5)
    assert len(full) == 20
    assert len(sub) == 5
    # deterministic: same subsample twice
    sub2 = RoadMarkDataset(tmp_path, "train", build_transforms("val", (64, 64)),
                           num_classes=7, subsample=5)
    assert [p[0].name for p in sub.pairs] == [p[0].name for p in sub2.pairs]


def test_flops_counter_runs():
    torch = pytest.importorskip("torch")
    import importlib.util, os
    path = os.path.join(os.path.dirname(__file__), "..", "scripts", "run_perf_benchmark.py")
    spec = importlib.util.spec_from_file_location("perf", path)
    perf = importlib.util.module_from_spec(spec); spec.loader.exec_module(perf)
    from uavroadmark.models import get_model
    m = get_model("miniunet", num_classes=7)
    gmacs = perf.count_flops(m, torch.randn(1, 3, 64, 64))
    assert gmacs > 0
