"""Metric correctness tests - the numeric foundation of the whole benchmark."""
import numpy as np
import pytest

from uavroadmark.metrics.segmentation import (ConfusionMatrix, compute_all,
                                              metrics_from_confusion)


def test_perfect_prediction_scores_one():
    gt = np.array([[0, 1, 2], [2, 1, 0]])
    m = compute_all(gt, gt.copy(), num_classes=3, foreground_only=False)
    assert m.miou == pytest.approx(1.0, abs=1e-4)
    assert m.mdice == pytest.approx(1.0, abs=1e-4)
    assert m.pixel_accuracy == pytest.approx(1.0, abs=1e-4)


def test_totally_wrong_prediction_scores_zero_iou():
    gt = np.zeros((4, 4), dtype=int)
    pred = np.ones((4, 4), dtype=int)
    cm = ConfusionMatrix(2)
    cm.update(gt, pred)
    iou = cm.per_class_iou()
    assert iou[0] == pytest.approx(0.0, abs=1e-4)  # class 0 never predicted right
    assert iou[1] == pytest.approx(0.0, abs=1e-4)  # class 1 never in GT


def test_confusion_matrix_counts():
    # 2 pixels of class0, predicted [0,1]; 2 of class1, predicted [1,1]
    gt = np.array([0, 0, 1, 1])
    pred = np.array([0, 1, 1, 1])
    cm = ConfusionMatrix(2)
    cm.update(gt, pred)
    # row=gt, col=pred -> [[1,1],[0,2]]
    assert cm.mat.tolist() == [[1, 1], [0, 2]]
    assert cm.tp.tolist() == [1.0, 2.0]
    assert cm.fp.tolist() == [0.0, 1.0]
    assert cm.fn.tolist() == [1.0, 0.0]


def test_known_iou_value():
    # gt=[0,0,1,1] pred=[0,1,1,1]
    # class1: TP=2 (idx 2,3), FP=1 (idx 1), FN=0 -> IoU = 2/(2+1+0) = 2/3
    gt = np.array([0, 0, 1, 1])
    pred = np.array([0, 1, 1, 1])
    cm = ConfusionMatrix(2)
    cm.update(gt, pred)
    assert cm.per_class_iou()[1] == pytest.approx(2 / 3, abs=1e-4)
    # class0: TP=1, FP=0, FN=1 -> IoU = 1/2
    assert cm.per_class_iou()[0] == pytest.approx(0.5, abs=1e-4)


def test_ignore_index_excludes_pixels():
    gt = np.array([255, 1, 1, 0])
    pred = np.array([0, 1, 1, 0])
    cm = ConfusionMatrix(2, ignore_index=255)
    cm.update(gt, pred)
    # the 255 pixel must be ignored -> 3 valid pixels, all correct
    assert cm.mat.sum() == 3
    assert cm.pixel_accuracy() == pytest.approx(1.0, abs=1e-4)


def test_foreground_only_excludes_background():
    gt = np.array([[0, 0, 1], [0, 2, 2]])
    pred = gt.copy()
    pred[0, 2] = 0  # miss one class-1 pixel
    full = compute_all(gt, pred, num_classes=3, foreground_only=False)
    fg = compute_all(gt, pred, num_classes=3, foreground_only=True)
    # foreground-only mean must differ from the all-class mean here
    assert fg.miou != pytest.approx(full.miou)


def test_streaming_equals_single_shot():
    rng = np.random.default_rng(0)
    gt = rng.integers(0, 3, size=(10, 8, 8))
    pred = rng.integers(0, 3, size=(10, 8, 8))
    cm_stream = ConfusionMatrix(3)
    for i in range(10):
        cm_stream.update(gt[i], pred[i])
    cm_once = ConfusionMatrix(3)
    cm_once.update(gt, pred)
    assert np.array_equal(cm_stream.mat, cm_once.mat)


def test_shape_mismatch_raises():
    cm = ConfusionMatrix(2)
    with pytest.raises(ValueError):
        cm.update(np.zeros((2, 2)), np.zeros((3, 3)))
