"""``uavrm-train`` / ``python -m uavroadmark.cli.train`` - config-driven training."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from ..build import (build_loaders, build_loss_from_cfg, build_model_from_cfg)
from ..engine import Trainer, build_optimizer, build_scheduler
from ..tracking import ExperimentTracker
from ..utils import get_logger, load_config, seed_everything

log = get_logger("cli.train")


def _resolve_device(requested: str) -> str:
    if requested != "auto":
        return requested
    try:
        import torch
        return "cuda" if torch.cuda.is_available() else "cpu"
    except ImportError:
        return "cpu"


def main(argv=None):
    ap = argparse.ArgumentParser(description="Train a segmentation model")
    ap.add_argument("--config", required=True)
    ap.add_argument("--opt", nargs="*", default=[],
                    help="dotted overrides, e.g. train.lr=3e-4 train.epochs=5")
    args = ap.parse_args(argv)

    cfg = load_config(args.config, overrides=args.opt)
    seed_everything(cfg.get("seed", 42))
    device = _resolve_device(cfg["train"].get("device", "auto"))

    run_name = cfg.get("run_name", Path(args.config).stem)
    out_dir = Path(cfg["train"].get("out_dir", "outputs")) / run_name
    out_dir.mkdir(parents=True, exist_ok=True)

    train_loader, val_loader = build_loaders(cfg)
    model = build_model_from_cfg(cfg)
    loss_fn = build_loss_from_cfg(cfg)
    optimizer = build_optimizer(model, cfg["train"].get("optimizer", {}))
    epochs = cfg["train"].get("epochs", 10)
    scheduler = build_scheduler(optimizer, cfg["train"].get("scheduler"), epochs)

    tracker = ExperimentTracker(
        out_dir=out_dir, run_name=run_name,
        use_tensorboard=cfg["train"].get("tensorboard", True),
        use_wandb=cfg["train"].get("wandb", False),
        config=dict(cfg))

    nc = cfg["dataset"]["num_classes"]
    class_names = cfg["dataset"].get("class_names")
    trainer = Trainer(
        model, loss_fn, optimizer, num_classes=nc, device=device,
        scheduler=scheduler, amp=cfg["train"].get("amp", True),
        grad_accum=cfg["train"].get("grad_accum", 1),
        grad_clip=cfg["train"].get("grad_clip", 0.0),
        ignore_index=cfg["dataset"].get("ignore_index"),
        class_names=class_names,
        foreground_only=cfg["dataset"].get("foreground_only", True),
        monitor=cfg["train"].get("monitor", "miou"),
        patience=cfg["train"].get("patience", 10),
        out_dir=str(out_dir), tracker=tracker)

    history = trainer.fit(train_loader, val_loader, epochs)
    tracker.close()

    (out_dir / "history.json").write_text(json.dumps(history, indent=2))
    log.info("Best %s = %.4f. Artifacts in %s",
             cfg["train"].get("monitor", "miou"), trainer.state.best_metric, out_dir)
    return trainer.state.best_metric


if __name__ == "__main__":
    main()
