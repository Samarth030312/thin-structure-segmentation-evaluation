#!/usr/bin/env python3
"""Multi-seed width study with bootstrap confidence intervals.

Evaluates converged synthetic models (CE+Dice, CoRe) at seeds {42,123,999} across
the controlled width series, and reports, per width, the mean and 95% CI (over
seeds) of mIoU vs clDice vs tolerance-IoU. This makes the primary claim
(mIoU under-reports correctly-detected thin markings) statistically robust.

    python scripts/run_width_study_multiseed.py
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from uavroadmark.build import build_model_from_cfg  # noqa: E402
from uavroadmark.data import RoadMarkDataset, build_transforms  # noqa: E402
from uavroadmark.engine import evaluate_model  # noqa: E402
from uavroadmark.utils import load_config, seed_everything  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

# checkpoint locations: seed 42 from the original ablation, 123/999 from rigor runs
CKPT = {
    ("ce_dice", 42): "outputs/abl_unet_ce_dice/best.pth",
    ("ce_dice", 123): "outputs/synth_ce_dice_s123/best.pth",
    ("ce_dice", 999): "outputs/synth_ce_dice_s999/best.pth",
    ("core", 42): "outputs/abl_unet_core/best.pth",
    ("core", 123): "outputs/synth_core_s123/best.pth",
    ("core", 999): "outputs/synth_core_s999/best.pth",
}
CONFIG = {"ce_dice": "configs/experiment/abl_unet_ce_dice.yaml",
          "core": "configs/experiment/abl_unet_core.yaml"}
SEEDS = [42, 123, 999]
SERIES = "datasets/width_series"
OUT = "reports/visualizations/width_study_multiseed"


def width_tags():
    tags = sorted([d for d in os.listdir(SERIES) if d.startswith("width_")],
                  key=lambda t: float(t.replace("width_", "").replace("p", ".")))
    scales = [float(t.replace("width_", "").replace("p", ".")) for t in tags]
    return tags, scales


def eval_ckpt(cfg, ckpt, root, device):
    import torch
    from torch.utils.data import DataLoader
    d = cfg["dataset"]; size = tuple(d.get("image_size", [256, 256]))
    ds = RoadMarkDataset(root, "test", build_transforms("val", size), num_classes=d["num_classes"])
    loader = DataLoader(ds, batch_size=8)
    model = build_model_from_cfg(cfg).to(device)
    ck = torch.load(ckpt, map_location=device)
    model.load_state_dict(ck["model"] if "model" in ck else ck)
    seg, _, thin, _ = evaluate_model(model, loader, d["num_classes"], device=device,
                                     foreground_only=True, thin_structure=True)
    return {"mIoU": seg.miou, "clDice": thin.cl_dice, "TolIoU": thin.tol_iou}


def ci95(x):
    x = np.asarray(x, float)
    if len(x) < 2:
        return float(x.mean()) if len(x) else float("nan"), float("nan")
    return float(x.mean()), float(1.96 * x.std(ddof=1) / np.sqrt(len(x)))


def main():
    import torch
    device = "cuda" if torch.cuda.is_available() else "cpu"
    seed_everything(0); os.makedirs(OUT, exist_ok=True)
    tags, scales = width_tags()
    results = {}  # loss -> metric -> width -> [seed values]
    for loss in ("ce_dice", "core"):
        cfg = load_config(CONFIG[loss])
        results[loss] = {m: {t: [] for t in tags} for m in ["mIoU", "clDice", "TolIoU"]}
        for s in SEEDS:
            ck = CKPT[(loss, s)]
            if not os.path.exists(ck):
                print(f"skip {loss} seed {s} (no checkpoint {ck})"); continue
            for t in tags:
                r = eval_ckpt(cfg, ck, os.path.join(SERIES, t), device)
                for m in ("mIoU", "clDice", "TolIoU"):
                    results[loss][m][t].append(r[m])
            print(f"{loss} seed {s} done")

    # aggregate + save
    agg = {}
    for loss in results:
        agg[loss] = {}
        for m in ("mIoU", "clDice", "TolIoU"):
            agg[loss][m] = {"mean": [], "ci": [], "n": []}
            for t in tags:
                mean, ci = ci95(results[loss][m][t])
                agg[loss][m]["mean"].append(mean); agg[loss][m]["ci"].append(ci)
                agg[loss][m]["n"].append(len(results[loss][m][t]))
    json.dump({"scales": scales, "tags": tags, "agg": agg},
              open(os.path.join(OUT, "width_multiseed.json"), "w"), indent=2)

    # plot CE+Dice with CI bands (the primary-claim figure)
    px = [4 * s for s in scales]
    fig, ax = plt.subplots(figsize=(6.5, 4))
    colors = {"mIoU": "#D55E00", "clDice": "#009E73", "TolIoU": "#0072B2"}
    for m in ("mIoU", "clDice", "TolIoU"):
        mean = np.array(agg["ce_dice"][m]["mean"]); ci = np.array(agg["ce_dice"][m]["ci"])
        ax.plot(px, mean, marker="o", color=colors[m], label=m, lw=2)
        ax.fill_between(px, mean - ci, mean + ci, color=colors[m], alpha=0.2)
    ax.set_xlabel("marking width (px)"); ax.set_ylabel("score (mean ± 95% CI, 3 seeds)")
    ax.set_title("mIoU under-reports thin markings (CE+Dice, multi-seed)")
    ax.legend(); ax.grid(alpha=0.3)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "width_multiseed.png"), dpi=300)
    fig.savefig(os.path.join(OUT, "width_multiseed.pdf"))
    print(f"Wrote {OUT}/width_multiseed.{{json,png,pdf}}")

    # print the headline numbers with CIs
    print("\nCE+Dice, mean[95% CI] across 3 seeds:")
    for i, t in enumerate(tags):
        a = agg["ce_dice"]
        print(f"  {t:9s}: mIoU {a['mIoU']['mean'][i]:.3f}±{a['mIoU']['ci'][i]:.3f} | "
              f"clDice {a['clDice']['mean'][i]:.3f}±{a['clDice']['ci'][i]:.3f} | "
              f"TolIoU {a['TolIoU']['mean'][i]:.3f}±{a['TolIoU']['ci'][i]:.3f}")


if __name__ == "__main__":
    main()
