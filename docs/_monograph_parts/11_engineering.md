# Part 11 — Engineering & System Design

A research result is only as trustworthy as the system that produced it. This part
covers the engineering that makes the project reproducible and the lessons learned
running real deep learning on a 4 GB GPU.

## 11.1 Experiment tracking

Every run has a `run_name` and writes to `outputs/<run_name>/` (checkpoints
`best.pth`/`last.pth`, `history.json`, `metrics.csv`, `config.json`) and appends a row
to a leaderboard CSV (`reports/leaderboard_*.csv`). The `tracking/tracker.py` module
records per-epoch metrics; optional TensorBoard. Because the config is saved alongside
the checkpoint, any result is traceable to the exact settings that produced it —
essential for the multi-seed comparisons.

## 11.2 Configuration management

The `_base_` composition system (Part 10.2) keeps experiments DRY: a dataset YAML, a
model YAML, a loss YAML, and a training YAML compose into an experiment, and CLI
`--opt` overrides handle seeds and run names. This is what made "the same experiment
across 3 seeds and 3 datasets" a few one-line commands rather than copy-pasted scripts.

## 11.3 Reproducibility

- **Seeding (`utils/seed.py`):** seeds Python, NumPy, and PyTorch; deterministic where
  feasible.
- **Saved configs:** each run stores its resolved config.
- **Torch-free metrics:** identical metric numbers on any machine.
- **Regeneration scripts:** datasets are git-ignored but rebuilt by ingestion scripts
  from public sources; the law is rebuilt by three scripts. A reviewer can reproduce
  the central figure without a GPU (the controlled study runs on CPU in minutes).

## 11.4 Testing and CI

62 unit/integration tests (`tests/`) cover metrics, losses, configs, datasets, and the
generator. They run in seconds on CPU (no GPU dependency), making them suitable for
continuous integration on every change. The tests are the formal guarantee behind the
"not an implementation artifact" defense.

## 11.5 Deployment

`deploy/` holds an export path: the trained model exports to **ONNX**, and ONNX
Runtime was benchmarked at **1.47× faster than eager PyTorch on CPU** at bit-identical
output (`max|Δ| = 9e-8`). A C++/LibTorch engine and a TensorRT path are scaffolded.
This is engineering support for the benchmark, not part of the scientific claim, but it
demonstrates the metrics/models are production-portable.

## 11.6 Profiling, benchmarking, GPU utilisation

Profiling informed the architecture choices: DeepLabV3+ inference ~0.56 GB at 512²;
U-Net++ training OOM at batch 8. Training logs report per-epoch wall-time (≈7 s/epoch
synthetic, ≈12 s UAVid at 512², ≈19 s MassRoads, ≈43 s binary RLMD at 384²), used to
budget the multi-seed campaigns within wall-clock limits.

## 11.7 Memory management — the binding constraint

The single hardest engineering reality was **4 GB of VRAM**. Techniques used:

- **Small batch + gradient accumulation:** batch 2–4 with `grad_accum` to simulate a
  larger effective batch (Part 10.7).
- **fp32, not fp16:** mixed precision (AMP) *diverged* — the soft-skeleton gradients
  underflowed to zero/NaN. fp32 is slower but stable. *Lesson: AMP is not free;
  operations with tiny gradients (iterated morphology) can underflow.*
- **`PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`:** reduces fragmentation OOMs.
- **CPU for light eval:** the width-validation inference was run on CPU when the GPU was
  busy training, avoiding contention/OOM.
- **Subsampling:** real datasets were subsampled (e.g. MassRoads 160/40) to fit
  converged training in the budget; the *law* is unaffected because it rests on
  controlled geometry and converged binary models.

## 11.8 Background-job orchestration (a hard-won lesson)

Long trainings ran as background jobs. The reliable pattern is harness-tracked
background execution with explicit completion signals; the *unreliable* patterns
(learned the hard way) were `nohup`/`setsid` (orphaned/zombie processes immune to
`pkill`) and `cat <<EOF` heredocs combined with a launch in one shell command (the file
rewrite silently failed). The fix: write scripts with a real editor/tool, launch via
tracked background, and verify the actual Python interpreter (`pgrep -x python3` +
`/proc/PID/cmdline`), not shell wrappers.

## 11.9 How this repository would scale

The design scales along three axes with minimal change:

1. **More data / bigger models:** the config system and `Trainer` are
   resolution/batch agnostic; on a ≥12 GB GPU, raise batch size, drop gradient
   accumulation, enable larger encoders and SegFormer variants, and remove
   subsampling. Nothing in the pipeline assumes small data.
2. **More datasets:** add an ingestion script + a dataset YAML; the binary-road
   contract is uniform, so the width-validation runs unchanged (this is exactly how
   UAVid and MassRoads were added).
3. **More experiments:** seeds/losses/architectures are CLI overrides; a sweep is a
   shell loop writing to a shared leaderboard.

The scientific bottleneck is **data access** (aerial markings), not the codebase. Given
SkyScapes and a 12 GB GPU, the existing pipeline would run the decisive experiment with
no architectural change — the ingestion (`scripts/prepare_skyscapes.py`) is already
built and tested on a stand-in.

---
