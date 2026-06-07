"""Tests for SkyScapes ingestion (color->id mapping, splitting) and the CLI
boolean-override coercion bug fix."""
import importlib.util
import os

import cv2
import numpy as np
import pytest

from uavroadmark.utils.config import _coerce

# import the script module by path (scripts/ is not a package)
_SCRIPT = os.path.join(os.path.dirname(__file__), "..", "scripts", "prepare_skyscapes.py")
_spec = importlib.util.spec_from_file_location("prepare_skyscapes", _SCRIPT)
prep = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(prep)


def test_coerce_yaml_booleans():
    assert _coerce("false") is False
    assert _coerce("true") is True
    assert _coerce("False") is False
    assert _coerce("none") is None
    assert _coerce("null") is None
    assert _coerce("3e-4") == pytest.approx(3e-4)
    assert _coerce("8") == 8
    assert _coerce("cosine") == "cosine"


def test_rgb_to_id_exact_mapping():
    lut = {(0, 0, 0): 0, (255, 0, 0): 1, (0, 255, 0): 2}
    rgb = np.zeros((4, 4, 3), np.uint8)
    rgb[0, 0] = (255, 0, 0)
    rgb[1, 1] = (0, 255, 0)
    rgb[2, 2] = (7, 7, 7)        # unknown colour -> ignore_index
    ids = prep.rgb_to_id(rgb, lut, ignore_index=255)
    assert ids[0, 0] == 1
    assert ids[1, 1] == 2
    assert ids[3, 3] == 0
    assert ids[2, 2] == 255


def test_split_of_is_deterministic_and_covers_splits():
    splits = {prep.split_of(f"scene_{i}") for i in range(200)}
    assert splits == {"train", "val", "test"}
    assert prep.split_of("scene_5") == prep.split_of("scene_5")  # stable


def test_prepare_id_mode_end_to_end(tmp_path):
    raw = tmp_path / "raw"
    (raw / "images").mkdir(parents=True)
    (raw / "labels").mkdir(parents=True)
    for i in range(8):
        img = (np.random.rand(300, 300, 3) * 255).astype(np.uint8)
        msk = np.zeros((300, 300), np.uint8)
        msk[10:14, 5:280] = (i % 12) + 1     # a thin marking, class 1..12
        cv2.imwrite(str(raw / "images" / f"s{i}.png"), img)
        cv2.imwrite(str(raw / "labels" / f"s{i}.png"), msk)

    args = type("A", (), {})()
    args.raw, args.image_dir, args.label_dir, args.label_suffix = str(raw), "images", "labels", ""
    args.out = str(tmp_path / "prepared")
    args.label_mode, args.colormap = "id", None
    args.num_classes, args.ignore_index = 13, 255
    args.tile, args.stride = 128, 128
    args.keep_empty_frac, args.max_tiles_per_image = 1.0, 0
    args.ratios, args.split_file, args.seed = [0.6, 0.2, 0.2], None, 0
    prep.cmd_prepare(args)

    # the prepared dataset must satisfy the framework's folder contract
    from uavroadmark.report.validator import validate_dataset
    report = validate_dataset(args.out, num_classes=13, ignore_index=255)
    assert report["passed"]
    assert report["total_errors"] == 0
    # at least train split must exist with tiles
    train_imgs = list((tmp_path / "prepared" / "images" / "train").glob("*.png"))
    assert len(train_imgs) > 0
