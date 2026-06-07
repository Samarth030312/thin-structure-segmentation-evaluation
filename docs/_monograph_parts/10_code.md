# Part 10 — Code Walkthrough

This part teaches the codebase so you could maintain or extend it. Every reference is
a real file. The package is `src/uavroadmark/`; research scripts are in `scripts/`;
configs in `configs/`; tests in `tests/` (62 passing).

## 10.1 Repository structure

```
  src/uavroadmark/
    build.py            # assemble model/loss/data from a config dict
    cli/                # command-line entry points
      train.py          #   python -m uavroadmark.cli.train --config ...
      evaluate.py       #   evaluation on a split
      validate.py       #   dataset sanity checks
    data/
      dataset.py        # RoadMarkDataset (image/mask pairing, class_map)
      transforms.py     # albumentations train/val pipelines
      synthetic.py      # controlled synthetic generator
    models/zoo.py       # U-Net/U-Net++/DeepLabV3+/PSPNet/SegFormer (smp-backed)
    losses/
      functional.py     # CrossEntropy, Dice, Focal, Tversky
      topology.py       # SoftSkeletonize, SoftClDiceLoss, CoReLoss
    metrics/
      segmentation.py   # ConfusionMatrix, SegMetrics, iou/dice
      thin_structure.py # cl_dice, boundary_iou, tolerance_scores, width-stratified
      stats.py          # bootstrap CIs, paired tests
    engine/
      trainer.py        # Trainer.fit (the training loop)
      evaluator.py      # evaluate_model (metrics over a loader)
    tracking/, report/, viz/, utils/   # tracking, leaderboard, figures, config/seed
  scripts/              # research drivers (controlled study, fits, validation)
  configs/              # YAML composition (_base_ + overrides)
```

The package is **torch-free where possible**: all metrics in `metrics/` use only
numpy/scipy/skimage, so they are fast, portable, and unit-testable without a GPU.

## 10.2 Configuration system (`utils/config.py`, `configs/`)

Configs compose via a `_base_` list and are overridable on the command line:

```yaml
# configs/experiment/uav_massroads.yaml
_base_:
  - ../dataset/massroads_bin.yaml   # dataset: root, num_classes, image_size
  - ../model/unet.yaml              # model: unet, resnet34 encoder
  - ../loss/ce_dice.yaml            # loss: CE + Dice
  - ../train/gpu.yaml               # optimizer, schedule, amp=false
run_name: uav_massroads
train: {epochs: 40, batch_size: 4, grad_accum: 2}
```

`load_config` merges bases left-to-right then applies `--opt key=val` overrides
(e.g. `--opt seed=123 run_name=uav_massroads_s123`). This is why one YAML + CLI
overrides produced all multi-seed runs reproducibly.

## 10.3 Dataset ingestion (`data/dataset.py`)

`RoadMarkDataset` pairs images and masks by filename stem and optionally remaps mask
values with a `class_map`:

```python
class RoadMarkDataset(Dataset):
    def __init__(self, root, split, transforms, num_classes,
                 class_map=None, strict=True): ...
    def __getitem__(self, idx):
        image = load(self.images[idx]); mask = load(self.masks[idx])
        if self.class_map:                       # remap arbitrary ids → contiguous
            out = zeros_like(mask)
            for src, dst in self.class_map.items():
                out[mask == src] = dst
            mask = out
        sample = self.transforms(image=image, mask=mask)
        return {"image": sample["image"], "mask": sample["mask"].long()}
```

The **binary** datasets (UAVid, MassRoads, LoveDA, RLMD-bin) are produced by ingestion
scripts (`scripts/prepare_uavid.py`, `prepare_massroads.py`, `prepare_real.py`) that
decode the source (parquet/HF), binarise the target structure (e.g. UAVid road colour
`(128,64,128) → 1`), resize, and write the `images/{split}` + `masks/{split}` folder
contract. `scripts/dataset_validator.py` then checks shape/label consistency.

## 10.4 The metrics — `cl_dice` line by line (the hero)

From `src/uavroadmark/metrics/thin_structure.py`:

```python
def cl_dice(gt, pred):
    gt = gt.astype(bool); pred = pred.astype(bool)
    if gt.sum() == 0 and pred.sum() == 0:   # both empty → perfect
        return 1.0
    if gt.sum() == 0 or pred.sum() == 0:    # one empty → worst
        return 0.0
    skel_pred = skeletonize(pred)           # 1-px medial axis of prediction
    skel_gt   = skeletonize(gt)             # 1-px medial axis of ground truth
    tprec = (skel_pred & gt).sum()   / (skel_pred.sum() + _EPS)   # pred skeleton in GT?
    tsens = (skel_gt   & pred).sum() / (skel_gt.sum()   + _EPS)   # GT skeleton in pred?
    return float(2*tprec*tsens / (tprec + tsens + _EPS))          # harmonic mean
```

Read it against the theory (Part 7): `skeletonize` makes the metric width-blind;
`tprec`/`tsens` are the two ratios that are ≈1 for a detected structure and drop only
when the *topology* is wrong. The `_EPS` guards division; the empty-mask cases give the
correct degenerate values. This ~10-line function is the empirical instrument behind
the entire law.

`boundary_iou` (band IoU via `_boundary = mask − erosion(mask)`), `tolerance_scores`
(skeleton overlap within `τ` px → `cl_recall`, `tol_iou`), and the width-stratified
IoU (IoU as a function of `2×EDT` width) live in the same file.

## 10.5 Segmentation metrics (`metrics/segmentation.py`)

`ConfusionMatrix` accumulates an `C×C` count matrix over a dataset; `SegMetrics`
derives mIoU (foreground-mean & all-class), Dice, pixel accuracy, and FWIoU from it.
Accumulating a confusion matrix once and deriving all region metrics from it is both
efficient and the source of the mis-ranking analysis (you can compute every mIoU
variant from the same matrix).

## 10.6 Losses (`losses/functional.py`, `losses/topology.py`)

`functional.py` defines `CrossEntropyLoss`, `DiceLoss`, `FocalLoss`, `TverskyLoss` as
`nn.Module`s operating on logits `(N,C,H,W)` and integer targets. `topology.py` adds:

```python
class SoftSkeletonize(nn.Module):   # differentiable thinning via iterated soft-open
    def forward(self, p): ...        # min/max-pool surrogates, `iter` iterations
class SoftClDiceLoss(nn.Module):    # 1 − softclDice using the soft skeleton
class CoReLoss(nn.Module):          # w_ce·CE + w_r·Dice + w_t·SoftClDice  (the null result)
```

`SoftSkeletonize` is the memory hog (it retains many pooled tensors for autograd),
which is why CoRe needs batch 2 + grad-accum and why fp16 underflows its gradients.

## 10.7 Training loop (`engine/trainer.py`)

`Trainer.fit(train_loader, val_loader, epochs)` is a standard, readable loop:

```python
for epoch in range(epochs):
    model.train()
    for batch in train_loader:
        logits = model(batch["image"])
        loss = loss_fn(logits, batch["mask"]) / grad_accum
        loss.backward()
        if step % grad_accum == 0:
            optimizer.step(); optimizer.zero_grad()
    scheduler.step()                       # cosine LR decay
    val = evaluate(model, val_loader)      # mIoU, clDice, ...
    if val.miou > best: save("best.pth")   # checkpoint best-by-mIoU
    log(epoch, loss, val.miou, lr)         # the lines you see in task outputs
```

Key details that mattered: **gradient accumulation** (simulate a larger batch on 4 GB),
**fp32** (`amp=false`; fp16 diverged), **best-by-metric checkpointing**, and
**cosine LR** (the `lr 7.97e-04 → 0.00e+00` you see in logs). `build_optimizer`/
`build_scheduler` read the config (AdamW, cosine).

## 10.8 Evaluation (`engine/evaluator.py`)

`evaluate_model(model, loader, num_classes, foreground_only, thin_structure)` runs the
model over a loader, accumulates the confusion matrix for region metrics, and (if
`thin_structure=True`) computes clDice/Boundary-IoU/TolIoU per image and averages. The
CLI `python -m uavroadmark.cli.evaluate --checkpoint ... --split test` writes results
to a leaderboard CSV (`reports/leaderboard_*.csv`).

## 10.9 The research scripts (where the science is)

These are the files that produce the law; read them to reproduce it.

**`scripts/run_controlled_robustness.py`** — the geometry-only experiment.
- `make_structure(width, kind="wave")`: paints a wavy 1-px-skeleton line at thickness
  `width` via `cv2.polylines`.
- `degrade(gt, mode, mag)`: manufactures a "prediction" — `dilate`/`erode`/`shift`/
  `boundary_noise`/`gaps`.
- `metrics(gt, pr)`: IoU, Dice, clDice, BoundaryIoU, TolIoU.
- `sweep_width(mode, mag)`: loops widths × seeds → the `Gap(w)` table. Writes
  `reports/controlled/robustness_sweeps.json`.

**`scripts/fit_width_law.py`** — fits six forms with `scipy.optimize.curve_fit`,
ranks by `R²`/AIC, and compares the inverse-law prediction to the four real datasets.
Writes `reports/controlled/law_fit.json`.

**`scripts/make_law_figures.py`** — Figures A–D at 300 DPI + vector PDF (loads the two
JSONs; computes the heatmap directly from the geometry functions).

**`scripts/run_width_validation.py`** — real-data validation: loads converged
checkpoints (a multi-seed *ensemble* by averaging logits), and for each test image
computes mean GT road width (`2×distance_transform_edt`), IoU, clDice, and
tolerance-recall; bins by width; reports the gap and correlations. This is how
MassRoads/LoveDA/UAVid were placed on Figure A.

## 10.10 Tests (`tests/`)

62 tests cover metric correctness (e.g. clDice of identical masks = 1; IoU of disjoint
= 0), loss shapes/values, config composition, dataset pairing, and the synthetic
generator. Because the metrics are torch-free, the suite runs in seconds on CPU and is
the safety net behind every numeric claim (it is what lets us say the law is not a
metric-implementation bug — R6 in Part 9).

## 10.11 How the pieces interact (one run, end to end)

```
  config (YAML+overrides)
        │  load_config
        ▼
  build.py ─► model (zoo) + loss (functional/topology) + dataset (data)
        │
        ▼
  Trainer.fit ──► best.pth                (engine/trainer.py)
        │
        ▼
  cli.evaluate ─► confusion matrix + thin metrics ─► leaderboard CSV
        │
        ▼
  scripts/run_width_validation.py ─► (width, IoU, clDice) per image ─► Fig A point
```

To reproduce the whole law: `run_controlled_robustness.py` → `fit_width_law.py` →
`make_law_figures.py`; for real-data points, train via the configs then
`run_width_validation.py`.

---
