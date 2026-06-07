"""``uavrm-eval`` - evaluate a checkpoint on the test split and append to the
leaderboard.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from ..build import build_model_from_cfg
from ..data import RoadMarkDataset, build_transforms
from ..engine import evaluate_model
from ..utils import get_logger, load_config, seed_everything

log = get_logger("cli.eval")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Evaluate a checkpoint")
    ap.add_argument("--config", required=True)
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--split", default="test")
    ap.add_argument("--opt", nargs="*", default=[])
    args = ap.parse_args(argv)

    import torch
    from torch.utils.data import DataLoader

    cfg = load_config(args.config, overrides=args.opt)
    seed_everything(cfg.get("seed", 42))
    device = "cuda" if torch.cuda.is_available() else "cpu"

    d = cfg["dataset"]
    size = tuple(d.get("image_size", [256, 256]))
    ds = RoadMarkDataset(root=d["root"], split=args.split, num_classes=d["num_classes"],
                         transform=build_transforms("val", size),
                         class_map=d.get("class_map"), strict=d.get("strict", True))
    loader = DataLoader(ds, batch_size=cfg["train"].get("val_batch_size", 4))

    model = build_model_from_cfg(cfg).to(device)
    ckpt = torch.load(args.checkpoint, map_location=device)
    model.load_state_dict(ckpt["model"] if "model" in ckpt else ckpt)

    metrics, cm, thin, width = evaluate_model(
        model, loader, num_classes=d["num_classes"], device=device,
        ignore_index=d.get("ignore_index"), class_names=d.get("class_names"),
        foreground_only=d.get("foreground_only", True),
        thin_structure=True, tau=cfg.get("eval", {}).get("tau", 3))

    run_name = cfg.get("run_name", Path(args.config).stem)
    out_dir = Path(cfg["train"].get("out_dir", "outputs")) / run_name
    out_dir.mkdir(parents=True, exist_ok=True)
    full = metrics.to_dict()
    if thin is not None:
        full["thin_structure"] = thin.to_dict()
        full["width_curve"] = width
    (out_dir / f"eval_{args.split}.json").write_text(json.dumps(full, indent=2))

    # append to the global leaderboard (standard + thin-structure headline)
    from ..report.leaderboard import (count_params_millions, make_row,
                                      update_leaderboard)
    headline = dict(metrics.headline())
    if thin is not None:
        headline.update(thin.to_dict())
    row = make_row(
        run_name=run_name, model=cfg["model"]["name"],
        loss=cfg.get("loss", {}).get("name", "?"), split=args.split,
        headline=headline,
        params_m=count_params_millions(model),
        notes=cfg.get("notes", ""))
    lb_path = cfg["train"].get("leaderboard", "reports/leaderboard.csv")
    update_leaderboard(lb_path, row)

    log.info("%s | seg=%s", run_name, metrics.headline())
    if thin is not None:
        log.info("%s | thin=%s", run_name, thin.to_dict())
    print(json.dumps(full, indent=2))
    return metrics


if __name__ == "__main__":
    main()
