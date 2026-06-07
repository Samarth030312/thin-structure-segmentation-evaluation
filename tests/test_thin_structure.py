"""Tests for the thin-structure evaluation protocol (the paper's metric core)."""
import numpy as np
import pytest

from uavroadmark.metrics.thin_structure import (ThinStructureEvaluator,
                                                WidthStratifiedIoU, boundary_iou,
                                                cl_dice, local_width,
                                                tolerance_scores)


def _line(h=64, w=64, row=32, x0=4, x1=60, thickness=2):
    m = np.zeros((h, w), bool)
    t = thickness // 2
    m[row - t:row + t + (thickness % 2 or 1), x0:x1] = True
    return m


def test_cldice_perfect_is_one():
    m = _line()
    assert cl_dice(m, m.copy()) == pytest.approx(1.0, abs=1e-3)


def test_cldice_empty_both_is_one():
    z = np.zeros((32, 32), bool)
    assert cl_dice(z, z) == 1.0


def test_cldice_penalises_topology_break_more_than_iou():
    """A broken line keeps most pixels (high IoU) but loses connectivity."""
    gt = _line(thickness=3)
    broken = gt.copy()
    broken[:, 28:36] = False  # cut a gap -> topology broken
    iou = (gt & broken).sum() / (gt | broken).sum()
    cld = cl_dice(gt, broken)
    # both drop, but the gap removes a chunk of the centerline
    assert cld < 1.0
    assert iou > 0.6  # IoU stays high despite the break
    # connectivity-sensitive recall must register the gap
    ts = tolerance_scores(gt, broken, tau=1)
    assert ts["cl_recall"] < 1.0


def test_boundary_iou_perfect_is_one():
    m = _line(thickness=4)
    assert boundary_iou(m, m.copy()) == pytest.approx(1.0, abs=1e-3)


def test_boundary_iou_zero_on_disjoint():
    a = _line(row=10)
    b = _line(row=50)
    assert boundary_iou(a, b) < 0.05


def test_tolerance_recovers_shifted_line():
    """A 1px-shifted prediction is ~0 mask-IoU-friendly but fine within tau."""
    gt = _line(row=32, thickness=1)
    shifted = _line(row=34, thickness=1)  # 2 px off
    strict = tolerance_scores(gt, shifted, tau=1)
    loose = tolerance_scores(gt, shifted, tau=3)
    assert loose["cl_f1"] > strict["cl_f1"]
    assert loose["cl_f1"] > 0.8


def test_local_width_matches_thickness():
    m = _line(thickness=5)
    w = local_width(m)
    # max width on the centerline should be ~thickness
    assert 4.0 <= w.max() <= 6.0


def test_width_stratified_accumulates():
    acc = WidthStratifiedIoU()
    gt = _line(thickness=2)
    pred = gt.copy()
    acc.update(gt, pred)
    rec = acc.recall_by_width()
    assert any(v > 0.9 for v in rec.values())  # perfect recall somewhere


def test_evaluator_streaming():
    ev = ThinStructureEvaluator(tau=3)
    gt = _line(thickness=3)
    for _ in range(3):
        ev.update(gt, gt.copy())
    m = ev.compute()
    assert m.cl_dice == pytest.approx(1.0, abs=1e-2)
    assert m.tol_iou == pytest.approx(1.0, abs=1e-2)
    assert isinstance(ev.width_curve(), dict)
