# System / Hardware Report

Generated for the UAV RoadMark Benchmark research phase. This report defines the
**compute envelope** that constrains every experimental decision below — stated
honestly, because designing experiments that cannot run is not research.

## Hardware

| Component | Spec |
|---|---|
| GPU | **NVIDIA GeForce GTX 1650** (Turing, compute capability **7.5**) |
| VRAM | **4096 MiB (4 GB)** — *the binding constraint* |
| GPU driver | 590.48.01 (supports up to CUDA 13.1) |
| CPU | Intel Core i7-9750HF @ 2.60 GHz, **6 cores / 12 threads** |
| RAM | 23 GiB total (~12 GiB available at measurement) |
| Disk | 400 GB volume, ~188 GB free |

## Software

| Component | Version | Note |
|---|---|---|
| PyTorch | **2.2.0+cu121** | `torch.cuda.is_available() == True` ✅ |
| CUDA (torch build) | 12.1 | runs on the 13.1 driver (forward compatible) |
| segmentation_models_pytorch | 0.5.0 | U-Net/U-Net++/DeepLabV3+/PSPNet/SegFormer |
| tensorboard | 2.20.0 | logging |
| `triton` | **removed** | uninstalled to fix a `torch._dynamo` import crash; only affects `torch.compile`, not eager training |

## Measured training envelope (this machine)

Real measurement — DeepLabV3+ (ResNet-34) @ 512×512, batch 2, AMP:
**peak VRAM 0.56 GB, ~1.5 s/step.** smp segmentation models are activation-light,
so the 4 GB card has real headroom.

| Workload | Feasible here? | Notes |
|---|---|---|
| U-Net / U-Net++ / DeepLabV3+ / PSPNet (R18–R50) @512², AMP, batch 4–8 | ✅ **Yes** | primary CNN benchmark |
| SegFormer MiT-B0–B2 @512² | ✅ **Yes** | small batch + grad-accum |
| HRNet-W18/W32 | ✅ likely | batch 2–4 |
| SegFormer B4/B5, large encoders | ⚠️ tight | grad-accum, ≤384² |
| **Mask2Former / InternImage / SAM2 — *training*** | ❌ **No** | weights + activations exceed 4 GB; honest exclusion |
| SAM / MobileSAM — *inference* (pseudo-labels) | ✅ **Yes** | weights fit; no backprop |
| Optuna/Ray HPO | ✅ small budget | each trial is minutes; tens of trials overnight, not thousands |

## Implications for the research plan

1. **GPU training of CNNs + small transformers is real and in-scope** — headline
   numbers will be produced on-device, not faked.
2. **Foundation-model *training* is out of scope on this hardware**; we instead
   study **SAM/MobileSAM as a zero-/weak-supervision pseudo-labeler** for thin
   markings (inference-only) — which is both feasible *and* more novel than
   re-benchmarking a model we can't fit.
3. **HPO is feasible at small budget** (Optuna, ~20–40 trials overnight), not a
   thousand-trial sweep — we report a focused, honest search.
4. **Hardening needed:** compute region losses (Dice/Tversky) in fp32 under AMP
   to avoid the fp16 underflow observed on random init.

> Reproduce: `python scripts/system_report.py` (regenerates this table from the
> live machine).
