#!/usr/bin/env python3
"""Hyper-parameter optimisation with Optuna (TPE / Bayesian).

A focused, honest search appropriate to the 4 GB compute envelope: a small
number of trials, few epochs each, optimising validation foreground mIoU. We
search lr, weight decay, loss family, and (for Tversky/CoRe) the FP/FN balance β.

    python scripts/run_hpo.py --base configs/experiment/abl_unet_ce_dice.yaml \
        --trials 20 --epochs 8 --out reports/hyperparameter_study
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from uavroadmark.build import (build_loaders, build_loss_from_cfg,  # noqa: E402
                               build_model_from_cfg)
from uavroadmark.engine import Trainer, build_optimizer, build_scheduler  # noqa: E402
from uavroadmark.utils import load_config, merge_configs, seed_everything  # noqa: E402


def objective_factory(base_cfg, epochs, device):
    def objective(trial):
        import optuna  # noqa: F401
        lr = trial.suggest_float("lr", 1e-4, 3e-3, log=True)
        wd = trial.suggest_float("weight_decay", 1e-6, 1e-3, log=True)
        loss_name = trial.suggest_categorical("loss", ["ce_dice", "tversky", "core"])
        overrides = {"train": {"epochs": epochs, "optimizer": {"lr": lr, "weight_decay": wd},
                               "tensorboard": False},
                     "loss": {"name": loss_name}}
        if loss_name in ("tversky", "core"):
            beta = trial.suggest_float("beta", 0.5, 0.8)
            overrides["loss"]["beta"] = beta
            overrides["loss"]["alpha"] = round(1.0 - beta, 3)

        cfg = merge_configs(base_cfg, overrides)
        seed_everything(cfg.get("seed", 42))
        train_loader, val_loader = build_loaders(cfg)
        model = build_model_from_cfg(cfg)
        loss_fn = build_loss_from_cfg(cfg)
        opt = build_optimizer(model, cfg["train"]["optimizer"])
        sched = build_scheduler(opt, cfg["train"].get("scheduler"), epochs)
        trainer = Trainer(model, loss_fn, opt, num_classes=cfg["dataset"]["num_classes"],
                          device=device, scheduler=sched, amp=False,
                          class_names=cfg["dataset"].get("class_names"),
                          foreground_only=True, monitor="miou", patience=epochs,
                          out_dir=f"outputs/hpo/trial_{trial.number}")
        trainer.fit(train_loader, val_loader, epochs)
        return trainer.state.best_metric
    return objective


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--trials", type=int, default=20)
    ap.add_argument("--epochs", type=int, default=8)
    ap.add_argument("--out", default="reports/hyperparameter_study")
    args = ap.parse_args()

    import optuna
    import torch
    device = "cuda" if torch.cuda.is_available() else "cpu"
    base_cfg = load_config(args.base)
    os.makedirs(args.out, exist_ok=True)

    study = optuna.create_study(direction="maximize",
                                sampler=optuna.samplers.TPESampler(seed=42))
    study.optimize(objective_factory(base_cfg, args.epochs, device),
                   n_trials=args.trials)

    best = {"best_value": study.best_value, "best_params": study.best_params,
            "trials": [{"number": t.number, "value": t.value, "params": t.params}
                       for t in study.trials]}
    with open(os.path.join(args.out, "hpo_results.json"), "w") as f:
        json.dump(best, f, indent=2)

    # importance + history figures (best-effort)
    try:
        import matplotlib
        matplotlib.use("Agg")
        from optuna.visualization.matplotlib import (plot_optimization_history,
                                                     plot_param_importances)
        import matplotlib.pyplot as plt
        plot_optimization_history(study); plt.tight_layout()
        plt.savefig(os.path.join(args.out, "hpo_history.png"), dpi=150); plt.close()
        plot_param_importances(study); plt.tight_layout()
        plt.savefig(os.path.join(args.out, "hpo_importance.png"), dpi=150); plt.close()
    except Exception as e:  # noqa: BLE001
        print("viz skipped:", e)

    print("Best mIoU=%.4f params=%s" % (study.best_value, study.best_params))


if __name__ == "__main__":
    main()
