# Architecture & Design Decisions

This document explains *why* the repository is structured the way it is — the
reasoning a reviewer at an AV team would probe.

## 1. Layering: a torch-light core

The package is deliberately split so the **numeric core has no hard torch
dependency**:

```
metrics/  losses/        ← losses need torch; metrics do NOT (pure numpy)
data/synthetic.py        ← numpy/cv2 only
utils/ report/validator  ← pure python/numpy
─────────────────────────────────────────
models/ engine/ losses/  ← torch (lazy-imported)
```

**Why:** validation, EDA, and the entire metric suite must run in constrained or
CI environments without a GPU stack. Lazy `import torch` inside factories keeps
`import uavroadmark` cheap and robust. The metrics being numpy-only also makes
them trivially unit-testable against hand-computed confusion matrices.

## 2. Registries instead of `if/else`

`get_model(name)` and `get_loss(name)` dispatch through a `Registry`
(`utils/registry.py`). This keeps experiment configuration **declarative** —
`model.name: deeplabv3plus` in YAML — and means adding an architecture is a
one-line `@MODEL_REGISTRY.register(...)`, never a change to calling code.

## 3. Config composition (`_base_`)

An experiment is a YAML file that composes `dataset/ + model/ + loss/ + train/`
fragments via `_base_`, plus CLI dotted overrides (`--opt train.lr=3e-4`). This
gives:
- no copy-pasted hyper-parameters,
- a single artefact that fully specifies a run (saved to `outputs/<run>/config.json`),
- cheap sweeps without editing files.

## 4. Confusion-matrix metrics (dataset-level)

We accumulate one `C×C` confusion matrix over the whole split and derive every
metric from it, rather than averaging per-image scores. Per-image averaging
biases results when image content/size varies (a known evaluation pitfall);
dataset-level micro/macro statistics are what Cityscapes/mmsegmentation report.
We additionally report **foreground-only** means because background dominates
~95 % of pixels and would otherwise inflate every number.

## 5. Uniform model contract

Every model — smp or native — returns **raw logits** `(N, C, H, W)`. The trainer,
evaluator, and losses therefore never special-case an architecture. Losses also
consume raw logits (not pre-activated probabilities), fixing the original
notebook's `sigmoid→BCELoss` instability.

## 6. Native MiniUNet fallback

`get_model("miniunet")` is a real, from-scratch U-Net with **zero third-party
model deps**. It guarantees the pipeline (and CI, and the smoke test) runs with
no `segmentation_models_pytorch`, no pretrained-weight download, and no internet
— while smp provides the strong pretrained baselines for real experiments.

## 7. Synthetic data as a first-class reproducibility tool

Because the real dataset is not redistributable, `data/synthetic.py`
deterministically generates UAV-like road-marking imagery that reproduces the
*statistical* challenge (sparse thin foreground, ~95 % background, photometric
nuisance). This makes the repo runnable anywhere and makes all committed numbers
**real** rather than fabricated — with an explicit, documented boundary between
"synthetic pipeline validation" and "the target UAV dataset headline science".

## 8. Honest failure handling

- Dataset pairing matches on **filename stem** and fails loudly on any unpaired
  file (the original's positional `zip` silently corrupts on one missing file).
- The validator surfaces 8 corruption classes *before* training wastes GPU hours.
- The trainer checkpoints `last.pth`+`best.pth` and is resumable.

## 9. Extension points

| Want to add… | Do this |
|---|---|
| a model | `@MODEL_REGISTRY.register("name")` in `models/zoo.py` |
| a loss | `@LOSS_REGISTRY.register("name")` in `losses/functional.py` |
| a dataset | provide the `images/<split>` + `masks/<split>` contract, add a `configs/dataset/*.yaml` |
| a metric | extend `ConfusionMatrix` / `SegMetrics` |
| a tracker backend | extend `tracking/tracker.py` |
