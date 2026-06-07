"""Dataset pairing, synthetic generation, and validator tests."""
import cv2
import numpy as np
import pytest

from uavroadmark.data.dataset import pair_image_mask
from uavroadmark.data.synthetic import build_dataset, generate_sample
from uavroadmark.report.validator import validate_dataset


def test_synthetic_is_deterministic():
    a_img, a_msk = generate_sample(3, 64, 64, seed=42)
    b_img, b_msk = generate_sample(3, 64, 64, seed=42)
    assert np.array_equal(a_img, b_img)
    assert np.array_equal(a_msk, b_msk)


def test_synthetic_has_foreground_and_valid_ids():
    _, msk = generate_sample(0, 128, 128, seed=1)
    assert msk.max() <= 6 and msk.min() >= 0
    # across several samples at least some foreground appears
    any_fg = any(generate_sample(i, 128, 128, seed=1)[1].max() > 0 for i in range(8))
    assert any_fg


def test_build_and_validate_clean_dataset(tmp_path):
    build_dataset(tmp_path, n_train=4, n_val=2, n_test=2, h=64, w=64)
    report = validate_dataset(tmp_path, num_classes=7)
    assert report["passed"] is True
    assert report["total_errors"] == 0


def test_pairing_matches_on_stem(tmp_path):
    img_dir = tmp_path / "images" / "train"
    msk_dir = tmp_path / "masks" / "train"
    img_dir.mkdir(parents=True)
    msk_dir.mkdir(parents=True)
    for name in ["a", "b"]:
        cv2.imwrite(str(img_dir / f"{name}.png"), np.zeros((8, 8, 3), np.uint8))
        cv2.imwrite(str(msk_dir / f"{name}.png"), np.zeros((8, 8), np.uint8))
    pairs = pair_image_mask(img_dir, msk_dir)
    assert [p[0].stem for p in pairs] == ["a", "b"]


def test_pairing_strict_raises_on_unpaired(tmp_path):
    img_dir = tmp_path / "images" / "train"
    msk_dir = tmp_path / "masks" / "train"
    img_dir.mkdir(parents=True)
    msk_dir.mkdir(parents=True)
    cv2.imwrite(str(img_dir / "a.png"), np.zeros((8, 8, 3), np.uint8))
    cv2.imwrite(str(img_dir / "b.png"), np.zeros((8, 8, 3), np.uint8))
    cv2.imwrite(str(msk_dir / "a.png"), np.zeros((8, 8), np.uint8))  # b missing
    with pytest.raises(ValueError):
        pair_image_mask(img_dir, msk_dir, strict=True)


def test_validator_flags_invalid_class_id(tmp_path):
    build_dataset(tmp_path, n_train=2, n_val=1, n_test=1, h=32, w=32)
    # corrupt one mask with an out-of-range class id
    bad = tmp_path / "masks" / "train" / "train_0000.png"
    m = cv2.imread(str(bad), cv2.IMREAD_UNCHANGED)
    m[0, 0] = 99
    cv2.imwrite(str(bad), m)
    report = validate_dataset(tmp_path, num_classes=7)
    checks = {i["check"] for s in report["splits"] for i in s["issues"]}
    assert "invalid_class_id" in checks
    assert report["passed"] is False


def test_validator_flags_missing_mask(tmp_path):
    build_dataset(tmp_path, n_train=2, n_val=1, n_test=1, h=32, w=32)
    (tmp_path / "masks" / "train" / "train_0000.png").unlink()
    report = validate_dataset(tmp_path, num_classes=7)
    checks = {i["check"] for s in report["splits"] for i in s["issues"]}
    assert "missing_mask" in checks
