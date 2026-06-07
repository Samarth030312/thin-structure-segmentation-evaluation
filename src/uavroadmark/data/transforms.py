"""Albumentations pipelines shared by training and evaluation.

Augmentations are chosen for the UAV domain specifically:
* geometric flips/rotations are *safe* because nadir aerial imagery has no
  canonical up direction (unlike dashcam imagery);
* mild scale/shift simulates altitude and GSD variation;
* photometric jitter simulates time-of-day and sensor differences.
We deliberately avoid heavy elastic/grid distortions that would break the
geometry of thin straight markings.
"""
from __future__ import annotations

from typing import Tuple

import albumentations as A
from albumentations.pytorch import ToTensorV2

IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)


def train_transforms(size: Tuple[int, int] = (256, 256)) -> A.Compose:
    h, w = size
    return A.Compose([
        A.Resize(h, w),
        A.HorizontalFlip(p=0.5),
        A.VerticalFlip(p=0.5),
        A.RandomRotate90(p=0.5),
        A.ShiftScaleRotate(shift_limit=0.06, scale_limit=0.1, rotate_limit=15,
                           border_mode=0, p=0.5),
        A.RandomBrightnessContrast(brightness_limit=0.2, contrast_limit=0.2, p=0.5),
        A.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
        ToTensorV2(),
    ])


def eval_transforms(size: Tuple[int, int] = (256, 256)) -> A.Compose:
    h, w = size
    return A.Compose([
        A.Resize(h, w),
        A.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
        ToTensorV2(),
    ])


def build_transforms(phase: str, size: Tuple[int, int] = (256, 256)) -> A.Compose:
    return train_transforms(size) if phase == "train" else eval_transforms(size)
