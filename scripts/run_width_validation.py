#!/usr/bin/env python3
"""Real-data validation of the primary claim on UAV/aerial datasets.

Claim: mIoU under-reports correctly-detected thin structures. On real data we
cannot control width, so we *stratify*: for each test image of a converged binary
road model, we measure the mean ground-truth road width (2*EDT) and the per-image
IoU, clDice, and tolerance-recall. If, as roads get thinner, IoU drops while
clDice/recall stay high, the claim holds on real UAV data.

    python scripts/run_width_validation.py --config configs/experiment/uav_uavid.yaml \
        --checkpoints outputs/uav_uavid_s42/best.pth outputs/uav_uavid_s123/best.pth ... \
        --label UAVid --out reports/visualizations/uav_validation
"""
import argparse
import json
import os
import sys

import numpy as np
from scipy.ndimage import distance_transform_edt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from uavroadmark.build import build_model_from_cfg  # noqa: E402
from uavroadmark.data import RoadMarkDataset, build_transforms  # noqa: E402
from uavroadmark.metrics.thin_structure import cl_dice, tolerance_scores  # noqa: E402
from uavroadmark.utils import load_config, seed_everything  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

WIDTH_BINS = [0, 6, 12, 20, 35, 1e9]
BIN_LABELS = ["<6", "6-12", "12-20", "20-35", ">35"]


def per_image(cfg, ckpts, device):
    import torch
    from torch.utils.data import DataLoader
    d = cfg["dataset"]; size = tuple(d.get("image_size", [512, 512]))
    ds = RoadMarkDataset(d["root"], "test", build_transforms("val", size),
                         num_classes=d["num_classes"], class_map=d.get("class_map"),
                         strict=d.get("strict", True))
    loader = DataLoader(ds, batch_size=4)
    models = []
    for ck in ckpts:
        m = build_model_from_cfg(cfg).to(device)
        s = torch.load(ck, map_location=device)
        m.load_state_dict(s["model"] if "model" in s else s); m.eval(); models.append(m)
    recs = []  # (mean_width, iou, cldice, tol_recall)
    with torch.no_grad():
        for batch in loader:
            x = batch["image"].to(device)
            # average logits over seeds (ensemble) -> stable per-image estimate
            logits = sum(m(x) for m in models) / len(models)
            preds = torch.argmax(logits, 1).cpu().numpy()
            gts = batch["mask"].numpy()
            for gt, pr in zip(gts, preds):
                g = gt > 0; p = pr > 0
                if g.sum() < 50:
                    continue
                width = (2 * distance_transform_edt(g))[g]
                inter = (g & p).sum(); union = (g | p).sum()
                iou = inter / max(1, union)
                cld = cl_dice(g, p)
                rec = tolerance_scores(g, p, tau=3)["cl_recall"]
                recs.append((float(width.mean()), float(iou), float(cld), float(rec)))
    return np.array(recs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--checkpoints", nargs="+", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--out", default="reports/visualizations/uav_validation")
    args = ap.parse_args()

    import torch
    device = "cuda" if torch.cuda.is_available() else "cpu"
    seed_everything(0); os.makedirs(args.out, exist_ok=True)
    cfg = load_config(args.config)
    R = per_image(cfg, args.checkpoints, device)
    if len(R) == 0:
        print("no valid images"); return
    width, iou, cld, rec = R[:, 0], R[:, 1], R[:, 2], R[:, 3]

    # MEASURED dataset-level statistics (used to place the point on the law curve;
    # these replace the previously hardcoded width/gap literals in the figures).
    summary = {
        "label": args.label, "n_images": len(R),
        "measured_mean_width_px": round(float(np.mean(width)), 3),
        "measured_median_width_px": round(float(np.median(width)), 3),
        "measured_mean_mIoU": round(float(np.mean(iou)), 3),
        "measured_mean_clDice": round(float(np.mean(cld)), 3),
        "measured_mean_gap": round(float(np.mean(cld - iou)), 3),
        "bins": {},
    }
    # bin by mean road width
    bins = np.digitize(width, WIDTH_BINS) - 1
    for b, lab in enumerate(BIN_LABELS):
        m = bins == b
        if m.sum() == 0:
            continue
        summary["bins"][lab] = {
            "n": int(m.sum()),
            "mIoU": round(float(iou[m].mean()), 3),
            "clDice": round(float(cld[m].mean()), 3),
            "tol_recall": round(float(rec[m].mean()), 3),
        }
    # correlation: does IoU rise with width while clDice stays flat?
    from scipy.stats import pearsonr
    summary["corr_width_iou"] = round(float(pearsonr(width, iou)[0]), 3)
    summary["corr_width_cldice"] = round(float(pearsonr(width, cld)[0]), 3)
    # the claim metric: mean (clDice - IoU) for the thinnest tertile
    thin = width <= np.quantile(width, 0.33)
    summary["thin_tertile"] = {
        "n": int(thin.sum()),
        "mean_IoU": round(float(iou[thin].mean()), 3),
        "mean_clDice": round(float(cld[thin].mean()), 3),
        "mean_recall": round(float(rec[thin].mean()), 3),
        "clDice_minus_IoU": round(float((cld[thin] - iou[thin]).mean()), 3),
    }
    json.dump(summary, open(os.path.join(args.out, f"{args.label}_width_val.json"), "w"), indent=2)

    # figure: binned IoU vs clDice vs recall by road width
    labs = [l for l in BIN_LABELS if l in summary["bins"]]
    x = np.arange(len(labs))
    fig, ax = plt.subplots(figsize=(6.5, 4))
    for key, c in [("mIoU", "#D55E00"), ("clDice", "#009E73"), ("tol_recall", "#0072B2")]:
        ax.plot(x, [summary["bins"][l][key] for l in labs], marker="o", color=c, label=key, lw=2)
    ax.set_xticks(x); ax.set_xticklabels(labs)
    ax.set_xlabel("mean GT road width (px)"); ax.set_ylabel("score")
    ax.set_title(f"{args.label}: mIoU vs clDice/recall by road width (real UAV/aerial)")
    ax.legend(); ax.grid(alpha=0.3); fig.tight_layout()
    fig.savefig(os.path.join(args.out, f"{args.label}_width_val.png"), dpi=300)
    fig.savefig(os.path.join(args.out, f"{args.label}_width_val.pdf"))

    print(f"\n{args.label}: {len(R)} images, "
          f"corr(width,IoU)={summary['corr_width_iou']}, "
          f"corr(width,clDice)={summary['corr_width_cldice']}")
    for l in labs:
        b = summary["bins"][l]
        print(f"  width {l:6s} (n={b['n']:3d}): mIoU {b['mIoU']:.3f} | "
              f"clDice {b['clDice']:.3f} | recall {b['tol_recall']:.3f}")
    t = summary["thin_tertile"]
    print(f"  THIN tertile: IoU {t['mean_IoU']:.3f} vs clDice {t['mean_clDice']:.3f} "
          f"(gap {t['clDice_minus_IoU']:+.3f}), recall {t['mean_recall']:.3f}")


if __name__ == "__main__":
    main()
