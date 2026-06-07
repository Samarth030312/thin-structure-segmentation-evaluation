"""``RoadMarkDataset`` - a robust image/mask segmentation dataset.

Folder contract::

    root/images/<split>/<stem>.<ext>
    root/masks/<split>/<stem>.<ext>      # single-channel class-id PNG

Key robustness fixes vs. the original notebook
----------------------------------------------
* **Stem-based pairing** instead of ``sorted(glob(...))`` zipping. The original
  paired the i-th image with the i-th mask; a single missing/extra file silently
  shifts every pair thereafter, corrupting training. Here we match on filename
  stem and *fail loudly* on any unmatched file.
* **Extension-agnostic** images (.jpg/.png/.jpeg/.tif) but masks are read as
  raw class ids with no interpolation.
* Optional ``class_map`` remaps arbitrary mask values to contiguous ids.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np
from torch.utils.data import Dataset

IMG_EXTS = (".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp")
MASK_EXTS = (".png", ".tif", ".tiff", ".bmp")


def _index_by_stem(folder: Path, exts) -> Dict[str, Path]:
    out: Dict[str, Path] = {}
    if not folder.is_dir():
        raise FileNotFoundError(f"Expected directory does not exist: {folder}")
    for p in sorted(folder.iterdir()):
        if p.suffix.lower() in exts:
            if p.stem in out:
                raise ValueError(f"Duplicate stem '{p.stem}' in {folder}")
            out[p.stem] = p
    return out


def pair_image_mask(image_dir: Path, mask_dir: Path,
                    strict: bool = True) -> List[Tuple[Path, Path]]:
    """Return matched ``(image, mask)`` paths, matched on filename stem."""
    images = _index_by_stem(Path(image_dir), IMG_EXTS)
    masks = _index_by_stem(Path(mask_dir), MASK_EXTS)
    common = sorted(set(images) & set(masks))
    missing_masks = sorted(set(images) - set(masks))
    missing_images = sorted(set(masks) - set(images))
    if strict and (missing_masks or missing_images):
        raise ValueError(
            f"Unpaired files. images-without-masks={missing_masks[:5]} "
            f"masks-without-images={missing_images[:5]} "
            f"(total unpaired={len(missing_masks) + len(missing_images)})"
        )
    return [(images[s], masks[s]) for s in common]


class RoadMarkDataset(Dataset):
    def __init__(self, root: str | Path, split: str = "train",
                 transform=None, num_classes: int = 7,
                 class_map: Optional[Dict[int, int]] = None,
                 strict: bool = True, subsample: Optional[int] = None):
        self.root = Path(root)
        self.split = split
        self.transform = transform
        self.num_classes = num_classes
        self.class_map = class_map
        self.pairs = pair_image_mask(
            self.root / "images" / split,
            self.root / "masks" / split,
            strict=strict,
        )
        if len(self.pairs) == 0:
            raise RuntimeError(f"No samples found for split '{split}' under {root}")
        # Deterministic, evenly-spaced subsample (for compute-bounded real runs).
        if subsample and subsample < len(self.pairs):
            step = len(self.pairs) / subsample
            idx = [int(i * step) for i in range(subsample)]
            self.pairs = [self.pairs[i] for i in idx]

    def __len__(self) -> int:
        return len(self.pairs)

    def _read_mask(self, path: Path) -> np.ndarray:
        mask = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
        if mask is None:
            raise IOError(f"Could not read mask: {path}")
        if mask.ndim == 3:  # tolerate accidentally-RGB masks
            mask = mask[..., 0]
        if self.class_map:
            remapped = np.zeros_like(mask)
            for src, dst in self.class_map.items():
                remapped[mask == src] = dst
            mask = remapped
        return mask.astype(np.int64)

    def __getitem__(self, idx: int):
        img_path, mask_path = self.pairs[idx]
        image = cv2.imread(str(img_path), cv2.IMREAD_COLOR)
        if image is None:
            raise IOError(f"Could not read image: {img_path}")
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mask = self._read_mask(mask_path)

        if self.transform is not None:
            out = self.transform(image=image, mask=mask)
            image, mask = out["image"], out["mask"]
            mask = mask.long()
        return {"image": image, "mask": mask, "stem": img_path.stem}
