# Evaluation Guide

## 1. Run evaluation

```bash
uavrm-eval --config configs/experiment/uav_uavid.yaml \
    --checkpoint outputs/uav_uavid/best.pth --split test
# or: python evaluation/evaluate.py --config <cfg> --checkpoint <ckpt> --split test
```

This:
1. accumulates a dataset-level confusion matrix over the split,
2. writes `outputs/<run>/eval_<split>.json` (full per-class metrics),
3. appends a **ranked** row to `reports/leaderboard.csv`.

## 2. Metrics — definitions

All derived from a `C×C` confusion matrix (row = GT, col = pred). With per-class
TP/FP/FN pixel counts:

| Metric | Formula | Meaning |
|---|---|---|
| IoU (Jaccard) | TP / (TP+FP+FN) | overlap; the primary segmentation metric |
| Dice / F1 | 2TP / (2TP+FP+FN) | harmonic overlap; = F1 for binary |
| Precision | TP / (TP+FP) | of predicted marking pixels, fraction correct |
| Recall | TP / (TP+FN) | of true marking pixels, fraction found |
| Pixel Accuracy | ΣTP / Σall | overall correct pixels (imbalance-inflated!) |
| FWIoU | Σ freqₖ·IoUₖ | frequency-weighted IoU |

**mIoU/mDice/… are means over foreground classes by default**
(`dataset.foreground_only: true`), because background ≈ 95 % of pixels makes the
all-class mean and Pixel-Accuracy misleadingly high. Always read foreground
mIoU as the headline.

## 3. The leaderboard

`reports/leaderboard.csv` is idempotent on `(run_name, split)` and re-sorted by
`mIoU` on every update. Render it as markdown:
```python
from uavroadmark.report.leaderboard import render_markdown
print(render_markdown("reports/leaderboard.csv"))
```

## 4. Reading the numbers (a worked diagnosis)

The committed synthetic smoke run shows `PixelAcc≈0.91` but `mIoU≈0.18`. That gap
is the **signature of class imbalance**: the model predicts background almost
everywhere, getting 91 % of pixels right while barely overlapping the thin
markings. This is *exactly* why we report foreground mIoU and why the loss study
exists. On a real target UAV road-marking dataset with a pretrained DeepLabV3+/SegFormer and a recall-
oriented loss, the foreground mIoU is expected to rise substantially — run it to
get the real number.

## 5. Fair-comparison checklist

- same `image_size`, splits, and `seed` across compared runs,
- same eval transform (resize + ImageNet normalise only — no TTA unless reported),
- report params (M) alongside accuracy (the leaderboard does),
- change **one** variable per ablation (architecture *or* loss *or* encoder).
