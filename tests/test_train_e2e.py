"""A genuine (tiny) end-to-end training test: loss must decrease and the
trainer must produce checkpoints. Proves the engine actually learns."""
import pytest

torch = pytest.importorskip("torch")

from torch.utils.data import DataLoader

from uavroadmark.data import RoadMarkDataset, build_transforms
from uavroadmark.data.synthetic import build_dataset
from uavroadmark.engine import Trainer, build_optimizer
from uavroadmark.losses import get_loss
from uavroadmark.models import get_model


def test_training_reduces_loss_and_checkpoints(tmp_path):
    root = tmp_path / "data"
    build_dataset(root, n_train=6, n_val=4, n_test=2, h=64, w=64)

    tf_train = build_transforms("train", (64, 64))
    tf_val = build_transforms("val", (64, 64))
    train_ds = RoadMarkDataset(root, "train", tf_train, num_classes=7)
    val_ds = RoadMarkDataset(root, "val", tf_val, num_classes=7)
    train_loader = DataLoader(train_ds, batch_size=3, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=2)

    model = get_model("miniunet", num_classes=7, base=8, depth=3)
    loss_fn = get_loss("ce_dice")
    opt = build_optimizer(model, {"name": "adamw", "lr": 1e-3})
    trainer = Trainer(model, loss_fn, opt, num_classes=7, device="cpu",
                      amp=False, out_dir=str(tmp_path / "run"), patience=10)

    history = trainer.fit(train_loader, val_loader, epochs=3)
    assert len(history) == 3
    # training loss should trend down over the run
    assert history[-1]["train_loss"] < history[0]["train_loss"]
    assert (tmp_path / "run" / "last.pth").exists()
    assert (tmp_path / "run" / "best.pth").exists()
