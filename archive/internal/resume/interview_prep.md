# Technical Interview Prep — UAV RoadMark Benchmark

> **Historical / superseded.** This document is from the project's initial benchmark-building phase. The project's actual contribution and current narrative is the **width-coupling law** for thin-structure evaluation metrics — see `reports/width_coupling_theory.md` and `paper_package/final_ieee_paper.pdf`. The "target UAV dataset" referenced below was an aspirational road-marking set that was **never acquired**; the experiments actually used a synthetic generator and the public datasets RLMD, LoveDA, Massachusetts Roads, and UAVid. See `reports/repository_integrity_report.md`.


Talking points, likely questions, and strong answers, organised by company
emphasis. Answer honestly: this is a **framework** validated on synthetic data,
with a documented path to real results.

---

## 1. Project architecture explanation (whiteboard version)

> "Layered package. The **core** — metrics, config, synthetic data — is
> numpy-only and torch-free, so validation/EDA/tests run anywhere. The **heavy**
> layer — models, losses, training engine — lazy-imports torch. Models and losses
> are pulled from **string registries** (`get_model`, `get_loss`), so an
> experiment is a **composed YAML** (`dataset+model+loss+train`) with CLI
> overrides — no code edits to sweep. Training goes through one engine with AMP,
> grad-accum, checkpointing, early stopping, and a tracker (TB/W&B/CSV).
> Evaluation accumulates a **dataset-level confusion matrix** and appends a
> ranked row to a leaderboard. Everything is reproducible: seeded, config-saved,
> 32 tests, one-command smoke run on synthetic data."

---

## 2. Core CV/ML questions & strong answers

**Q: Why is pixel accuracy the wrong headline metric here?**
A: Background is ~95 % of pixels, so predicting "background everywhere" scores
~95 % pixel accuracy with ~0 foreground IoU. I report **mean IoU over foreground
classes** and also FWIoU; the synthetic runs show the tell-tale gap (PixelAcc
0.91 vs mIoU 0.18). IoU penalises both FP and FN per class, which is what we
care about for thin markings.

**Q: Why confusion-matrix metrics instead of averaging per-image scores?**
A: Per-image averaging biases the result when image content/size varies — a few
small images with tiny objects can dominate. Accumulating one C×C matrix over the
whole split gives exact dataset-level micro/macro metrics, matching the
Cityscapes/mmsegmentation convention.

**Q: Walk me through your loss choice.**
A: Default is **CE+Dice**: CE gives smooth, well-conditioned pixel gradients;
Dice is region-based and scale-invariant, so it's robust to the imbalance and
aligns with the IoU/Dice metric. For safety-critical recall I switch to
**Tversky with β>α** (0.7/0.3) to penalise false negatives — missing a lane line
is worse than a spurious one. Focal is the hard-example alternative. I can derive
each on the board.

**Q: Why are flips/rotations safe augmentations here but risky for dashcam?**
A: Nadir UAV imagery has no canonical "up"; a horizontally/vertically flipped or
90°-rotated frame is still a valid road scene. Dashcam imagery has gravity/horizon
priors that flips would violate. So I use flips + 90° rotations + mild
scale/shift/brightness, but avoid elastic/grid warps that would bend straight
thin markings.

**Q: DeepLabV3+ vs U-Net vs SegFormer for this task?**
A: U-Net's skip connections give the best fine-structure localisation (it was
built for thin membranes — analogous to lane lines). DeepLabV3+'s ASPP adds
multi-scale context for mixed marking scales without losing resolution. SegFormer
brings a global receptive field and scale-robustness (no positional encodings) —
great for variable UAV altitude, but it's data-hungry and needs pretrained MiT
weights. PSPNet has strong context but a coarse decoder → soft boundaries, the
weakest property for thin markings.

**Q: Your SegFormer collapsed. What happened?**
A: That run is **from scratch, 3 epochs, 24 images** — the worst case for a
transformer. Its validation mIoU oscillated and pixel accuracy stayed low. It's a
*predicted* failure mode (transformers need pretraining + data), and I think it's
a feature that the benchmark surfaced it rather than hiding it. With ImageNet-MiT
weights and a full schedule it should be among the best.

**Q: How would you get real numbers?**
A: Drop the target UAV dataset into the folder contract, run the validator, then the same
`uavrm-train`/`uavrm-eval` with `configs/train/default.yaml` (pretrained
encoders, 60 epochs, 512², AMP) on a GPU. The synthetic run proves the machinery;
only data and budget change.

---

## 3. Company-specific questions & answers

### Tesla Autopilot (vision-only, real-time, scale)
- **Q: This is segmentation; Tesla does multi-task vision at scale. How does it
  transfer?** A: The *infrastructure* transfers: registry zoos, config-driven
  training, fair evaluation, imbalance-aware losses/metrics, failure analysis. I'd
  extend the metric layer to multi-task heads and add latency/throughput to the
  leaderboard, since deployment is a Pareto problem (I already argue BiSeNetV2 as
  the latency anchor).
- **Q: Real-time constraints?** A: I'd report FPS/params alongside accuracy and
  bring in BiSeNetV2 + INT8/ONNX export; the uniform logits contract makes export
  straightforward.

### NVIDIA AV (platforms, optimization, TensorRT)
- **Q: How would you optimise these for a Jetson/Orin?** A: ONNX export →
  TensorRT, FP16/INT8 calibration, pick efficient encoders (MiT-B0, resnet18),
  measure on-device latency, and add an accuracy-vs-latency leaderboard column.
  My MiniUNet fallback already shows I can write architectures from scratch when
  a dependency isn't deployable.
- **Q: Mixed precision details?** A: AMP autocast + GradScaler, auto-disabled on
  CPU; I unscale before grad-clip. I also hit and fixed a real env issue (stale
  triton breaking torch._dynamo) — I can debug the stack, not just call it.

### Waymo (rigorous evaluation, long-tail, safety)
- **Q: How do you ensure fair comparison?** A: One variable per ablation, shared
  seeds/splits/resolution, dataset-level confusion-matrix metrics, foreground
  reporting, and a leaderboard idempotent on (run, split). I validate data before
  training so silent corruption can't confound results.
- **Q: Long-tail / rare classes?** A: EDA shows arrows are the rarest fg class
  (6 %); I'd add per-class IoU tracking (already computed), class-balanced
  sampling, and Tversky/Focal to protect recall on rare markings.

### Bosch / Cruise / Mobileye / Zoox (productionisation, QA)
- **Q: How is this production-quality vs. a notebook?** A: I list the exact
  defects I fixed (Appendix B of the final report): unstable `sigmoid→BCELoss`,
  positional pairing corruption, hardcoded device, no checkpointing/validation.
  I added tests (32), CI-able smoke runs, config persistence, and reproducible
  seeding — the difference between a demo and a maintainable system.

---

## 4. Questions to ASK them (shows seniority)
- What's your accuracy/latency budget on the target compute, and how do you
  arbitrate the Pareto front today?
- How do you handle label noise and class imbalance in your evaluation harness?
- Where does aerial/UAV data fit in your stack — mapping, validation, or
  online perception?

## 5. Honesty guardrail
If asked "what are your a real target UAV road-marking dataset numbers?" — say plainly: *"The committed
numbers are synthetic-data pipeline validation; I didn't have the licensed
dataset or a GPU in this environment. The framework runs the real benchmark with
identical commands — here's the protocol and my falsifiable hypothesis for the
ordering."* That answer builds more trust than any invented SOTA table.
