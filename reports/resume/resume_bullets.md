# Resume Bullets & Talking Points

> Phrase these around **what was actually built and verified** (a reproducible
> benchmark framework, validated end-to-end), not around fabricated SOTA
> numbers. This is what survives technical scrutiny.

## A. Resume bullets (pick 3–5, tune verbs to seniority)

**Concise (one-line) variants**

- Built an **open-source semantic-segmentation benchmark framework** for UAV
  road-marking detection (U-Net, U-Net++, DeepLabV3+, PSPNet, SegFormer) with a
  unified `get_model`/`get_loss` registry, **YAML-composed experiments**, and an
  auto-ranked leaderboard.
- Engineered a **config-driven PyTorch training engine** (mixed precision,
  gradient accumulation, checkpointing, early stopping, LR schedulers) and a
  **confusion-matrix metric suite** (IoU/Dice/F1/precision/recall) with
  foreground-aware reporting for a **95 %-background, severely imbalanced** task.
- Implemented a **dataset-validation framework** (8 corruption checks → JSON/HTML)
  and automated EDA, catching missing pairs, invalid class ids, and resolution
  mismatches **before** training.
- Authored a **loss-function study** (CE, Dice, Focal, Tversky, CE+Dice) with
  derivations and class-imbalance analysis, plus **TP/FP/FN failure-map** and
  spatial **error-heatmap** diagnostics.
- Achieved **full reproducibility**: deterministic seeding, a synthetic data
  generator, **32 passing unit/e2e tests**, and one-command end-to-end runs;
  validated the entire pipeline on CPU.

**Impact-framed (senior) variants**

- *Designed and delivered the perception-evaluation infrastructure* that turns
  ad-hoc "train a model" scripts into **fair, controlled, reproducible
  benchmarking** — registry-based zoos, composable configs, and a leaderboard
  that enforces one-variable-at-a-time ablations.
- *Diagnosed and corrected* critical defects in an inherited pipeline
  (numerically unstable `sigmoid→BCELoss`, positional image/mask pairing,
  hardcoded device, no checkpointing), raising it to research-grade with tests
  and CI-ready smoke runs.
- *Made architecture/loss decisions defensible* by grounding them in a weighted
  dataset-selection matrix and a task-specific literature review across 8
  architectures.

## B. The 30-second pitch

> "I rebuilt an academic UAV road-marking project into a production-quality
> **benchmark framework**. The hard part isn't training one model — it's making
> model and loss comparisons *fair and reproducible* on a task where the
> foreground is under 5 % of pixels. So I built a registry-based model/loss zoo,
> a config-driven trainer with AMP/checkpointing/early-stopping, confusion-matrix
> metrics that report **foreground** mIoU (not imbalance-inflated pixel
> accuracy), a dataset validator, automated EDA, and failure-map visualisations —
> all reproducible, all tested, runnable end-to-end on a laptop via a synthetic
> data generator so nothing is mocked or faked."

## C. Skills this project demonstrates

`PyTorch` · `semantic segmentation` · `segmentation_models_pytorch` · `MLOps /
experiment tracking (TensorBoard, W&B)` · `reproducibility & config systems` ·
`class-imbalance & loss engineering` · `evaluation methodology` · `dataset
validation & QA` · `data visualization` · `software design (registries, layering,
testing)` · `autonomous-driving / UAV perception` · `technical writing`.

## C2. Research-phase bullets (quantified, novel-contribution framing)

Use these when the project is positioned as **research**, not just engineering:

- Proposed a **thin-structure evaluation protocol** (centerline-Dice, Boundary-IoU,
  tolerance-IoU, width-stratified analysis) for UAV road-marking segmentation and
  **showed mIoU is misleading for thin markings** — at 2-px width, mIoU=0.35 while
  tolerance-IoU=0.97 and clDice=1.0 on correctly-detected lines.
- Designed **CoRe**, a connectivity-recall loss (calibrated CE+Dice + differentiable
  soft-clDice), that **matched/beat the CE+Dice baseline on every metric**
  (mIoU 0.945 vs 0.938; clDice 0.999) and improved topological robustness under
  altitude/width shift (clDice 0.98 vs 0.90 at 8 px).
- **Benchmarked 5 architectures** on a width-controlled benchmark and demonstrated
  a concrete **metric mis-ranking** (DeepLabV3+ vs SegFormer swap between mIoU and
  Boundary-IoU); identified U-Net++ as best-accuracy and SegFormer-B0 (3.7 M params)
  as best for deployment.
- Ran the full pipeline on a **4 GB GTX-1650**: real GPU training (25-epoch runs),
  Optuna HPO, automated failure analysis (65 % of errors traced to shadow/low-contrast),
  and a **C++/LibTorch + TensorRT** deployment path with verified TorchScript export
  (bit-exact reload).
- Open-sourced a reproducible benchmark: **49 passing tests**, config-driven
  experiments, deterministic data generator, and an IEEE-ITSC-style paper draft.

## D. One-liner for the top of a CV

> Built an open-source, reproducible benchmark framework for UAV road-marking
> segmentation (5 architectures, 5 losses, config-driven training, validation,
> EDA, leaderboard, 32 tests).
