"""Config -> objects: the single place that turns a YAML ``Config`` into a
dataset, dataloaders, model and loss. Keeping this centralised means the train
and eval CLIs share identical construction logic (no drift).
"""
from __future__ import annotations

from typing import Tuple

from .data import RoadMarkDataset, build_transforms
from .losses import get_loss
from .models import get_model
from .utils.config import Config


def build_datasets(cfg: Config):
    d = cfg["dataset"]
    size = tuple(d.get("image_size", [256, 256]))
    nc = d["num_classes"]
    common = dict(root=d["root"], num_classes=nc,
                  class_map=d.get("class_map"), strict=d.get("strict", True))
    train = RoadMarkDataset(split=d.get("train_split", "train"),
                            transform=build_transforms("train", size),
                            subsample=d.get("subsample"), **common)
    val = RoadMarkDataset(split=d.get("val_split", "val"),
                          transform=build_transforms("val", size), **common)
    return train, val


def build_loaders(cfg: Config) -> Tuple:
    from torch.utils.data import DataLoader

    train_ds, val_ds = build_datasets(cfg)
    t = cfg["train"]
    train_loader = DataLoader(
        train_ds, batch_size=t.get("batch_size", 4), shuffle=True,
        num_workers=t.get("num_workers", 0), pin_memory=t.get("pin_memory", False),
        drop_last=False)
    val_loader = DataLoader(
        val_ds, batch_size=t.get("val_batch_size", t.get("batch_size", 4)),
        shuffle=False, num_workers=t.get("num_workers", 0),
        pin_memory=t.get("pin_memory", False))
    return train_loader, val_loader


def build_model_from_cfg(cfg: Config):
    m = dict(cfg["model"])
    name = m.pop("name")
    m.setdefault("num_classes", cfg["dataset"]["num_classes"])
    return get_model(name, **m)


def build_loss_from_cfg(cfg: Config):
    loss_cfg = dict(cfg.get("loss", {"name": "ce_dice"}))
    name = loss_cfg.pop("name")
    loss_cfg.setdefault("ignore_index", cfg["dataset"].get("ignore_index", -100))
    return get_loss(name, **loss_cfg)
