# System Design Discussion

How the benchmark is built, and the design trade-offs — for a systems/perception
design interview.

## 1. Architecture
```
configs (YAML) ─► build() ─► Dataset/Loaders ─► Trainer ─► Evaluator ─► leaderboard
     │                │            │               │            │
  composition     registries   stem-paired     AMP/ckpt/    confusion-matrix +
  + CLI overrides (model/loss)  + class_map     early-stop   thin-structure metrics
```
- **Torch-light core:** metrics, config, synthetic data have no hard torch
  dependency, so validation/EDA/metric tests run anywhere; heavy torch code is
  lazy-imported. *Trade-off:* a little indirection for broad runnability + fast CI.
- **Registries + composable configs:** `get_model("unetpp")`, `get_loss("core")`;
  an experiment is a composed YAML with dotted CLI overrides. *Trade-off:*
  declarative experiments and easy sweeps vs. a small learning curve.

## 2. Key design decisions and why
- **Dataset-level confusion matrix**, not per-image averaging, for unbiased
  micro/macro metrics on variable-content images.
- **Stem-based image/mask pairing** that fails loudly on any unpaired file —
  positional zipping silently corrupts on one missing file.
- **Load-time `class_map`** lets one ingested dataset be re-binarised/remapped
  without re-tiling (used for the cross-dataset binary task).
- **Always-on CSV leaderboard** (idempotent on run/split) so every run leaves a
  machine-readable trace even without TensorBoard/W&B.

## 3. Working within a 4 GB GPU (the real constraint)
- **fp16 diverged** on this card for from-scratch training → fp32; AMP autocast
  kept for the forward but the loss is computed in fp32.
- **Gradient accumulation** (batch 2 × accum 4) to fit U-Net++ and the
  memory-heavy soft-skeleton (CoRe) loss without OOM.
- **`expandable_segments`** allocator to avoid fragmentation OOM across runs.
- **Dataset subsampling** for compute-bounded multi-seed runs (documented as a
  limitation, not hidden).
*Honest consequence:* models were under-trained; the qualitative conclusions are
budget-independent but absolute numbers are not headline-grade.

## 4. Profiling-driven decisions
torch.profiler showed training is **GPU-compute-bound** (dataloader 72 img/s vs
~5 img/s training; convolutions = 85% of CUDA time). So the right levers are
lighter backbones / lower FLOPs and (on tensor-core GPUs) AMP — not dataloader
tuning. The performance leaderboard (params/FLOPs/FPS/VRAM) makes model selection
a Pareto decision, not accuracy-only.

## 5. Train→deploy parity
TorchScript/ONNX export is verified bit-exact against eager PyTorch; the C++
LibTorch engine mirrors the Python preprocessing (resize→RGB→ImageNet-norm→CHW) so
there is no train/serve skew. ONNX Runtime gave 1.47× CPU speedup at identical
output; TensorRT FP16 is the on-device path.

## 6. What I'd change at scale
Move config/registry pattern onto a managed experiment tracker; shard data and use
DDP on multi-GPU (the code is single-GPU); add a metrics service so the
thin-structure protocol runs as a CI gate on every model; and replace subsampling
with full-data, multi-seed sweeps. The evaluation protocol itself is the part most
worth productionising — it is what would have caught the metric failure earlier.
