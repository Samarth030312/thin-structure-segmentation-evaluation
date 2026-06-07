# Research Questions and Answers

Every answer cites measured results in this repo (real = RLMD; synthetic = the
controlled width benchmark, used only to isolate variables).

---

### Q1. Why does mIoU fail on thin structures?

**Because IoU is a region-overlap measure dominated by the few-pixel *width* of a
thin structure, so it conflates "detected the marking" with "matched its exact
pixel width."** A 2 px lane line predicted at 3 px loses most of its IoU to a
1 px boundary mismatch, even though the line is perfectly localised. Evidence
(synthetic, controlled width): training at 4 px and testing at 2 px gives
**mIoU 0.35 while TolIoU 0.97 and clDice 1.0** — the line is found; mIoU can't see
it (`loss_function_analysis.md`, `width_study.png`).

### Q2. Under what conditions does it fail?

Measured failure conditions:
- **Width / scale shift** (UAV altitude change): mIoU drops 0.94→0.35 off the
  training width while clDice stays ≥0.90 (synthetic width study).
- **High class imbalance** (real): on RLMD (98 % background, 609:1), multi-class
  foreground mIoU reads **~0.005–0.04** on a model with **90 % centerline
  precision** (`real_data_results.md`).
- **Model selection / ranking** (real): mIoU ranks the frame-flooding Tversky
  model **#1** despite `PixelAcc = 0.009` — it inverts the true ranking (Q3).

### Q3. Which metric best reflects perception quality?

**Topology/tolerance metrics — clDice, TolIoU, clPrecision/clRecall (with
PixelAcc as a sanity check).** Decisive real-data evidence (RLMD, clean U-Net++
loss ablation, 276 imgs): **mIoU ranks Tversky #1 (0.144) — yet Tversky is the
worst model** (`PixelAcc = 0.009`; it floods the frame, `clPrecision = 0.13`).
The genuinely best perception model (CE+Dice, clPrecision 0.91) has **5× lower
mIoU** than the worst. mIoU does not merely under-measure thin structures — **on
real data it inverts the ranking.** The thin-structure protocol ranks the models
correctly. **Report mIoU *and* clDice/clPrecision/PixelAcc; never mIoU alone.**
(See `real_data_results.md` §3.)

### Q4. Which architecture is best?

**U-Net++ for accuracy/topology; SegFormer-B0 for deployment.** Synthetic sweep:
U-Net++ tops Boundary-IoU (0.987) and clDice (0.999); PSPNet is worst (BoundaryIoU
0.62 — coarse decoder). On real RLMD, U-Net++ (with CE+Dice) reaches **clPrecision
0.90**. Skip-connection decoders win because they preserve the high-frequency
detail a thin marking *is* (`architecture_analysis.md`). DeepLabV3+ and SegFormer
**swap rank** between mIoU and Boundary-IoU — a concrete mis-ranking.

### Q5. Which loss is best?

**On real data, CE+Dice and CoRe are statistically TIED** (multi-seed) — and the
journey here is itself the lesson. *Synthetic:* CoRe ≥ CE+Dice on every metric.
*Real, seed 42:* CE+Dice beats CoRe (per-image p<0.001). *Real, 3 seeds:* the
advantage **vanishes** — clDice 0.405 vs 0.406, paired Δ=−0.001, CI [−0.18, 0.18]
(CoRe wins at seed 999); CoRe is ~2.4× higher-variance (`multiseed_results.md`).
**No loss reliably wins on real data.** Recall-only Tversky/Dice are worst — they
flood the frame (PixelAcc 0.008–0.009). **Recommendation: CE+Dice (stable, simple);
CoRe gives no reliable gain at this budget.** Two self-corrections (confound, then
single-seed artifact) are documented — that is what validation is *for*.

### Q6. Which deployment stack is best?

**ONNX Runtime for portable CPU/GPU; TensorRT FP16 for on-board UAV.** Measured:
ONNX Runtime is **1.47× faster than eager PyTorch on CPU at bit-identical accuracy**
(parity 9e-8). TorchScript export is bit-exact; a C++/LibTorch engine is provided.
TensorRT FP16/INT8 typically adds 2-4× on Jetson (`deployment_report.md`).

### Q7. Which model for a Jetson-class platform?

**SegFormer-B0 + CE+Dice, exported to TensorRT FP16.** It has **3.7 M params and
9.9 GFLOPs** (6× fewer than U-Net), competitive boundary/topology quality, and the
best accuracy/latency trade-off (`leaderboard_performance.csv`). Real-time on Orin
with FP16; the C++/TensorRT path is documented.

### Q8. Which model for maximum accuracy?

**U-Net++ + CE+Dice** — best Boundary-IoU/clDice, highest real clPrecision — at the
cost of throughput (**148.9 GFLOPs, 16 GPU FPS**, the slowest in the zoo). The
accuracy↔latency Pareto trade vs SegFormer is explicit and quantified.

### Q9. What remains unsolved?

1. **Rare-class recall** on real data: clRecall ~0.21 (RLMD) — the 609:1 tail is
   under-detected; needs class-balanced sampling, more data/epochs, and likely a
   detector for very rare markings.
2. **Real UAV-viewpoint validation**: confirmed on ground-view RLMD; SkyScapes
   (aerial) ingestion is built but its run needs the licensed data + a larger GPU.
3. **An India-specific UAV marking dataset does not exist** — a data-collection
   contribution (our annotation/validation tooling + SAM pseudo-labeling enable
   it).
4. **Foundation-model adaptation** is hardware-gated here (4 GB); SAM-as-pseudo-
   labeler is the proposed, feasible direction (`foundation_model_study.md`).
5. **Full-scale, multi-seed runs** for tighter CIs (the clean same-architecture
   loss ablation on real data is *done* — `real_data_results.md`; multi-seed at
   full resolution is the remaining step).
6. **Why CoRe is high-variance on real data** (its soft-skeleton term roughens the
   loss landscape → seed-sensitive: clDice 0.28–0.56 across seeds). Warm-up /
   temperature tuning to stabilise it is open.

---

**One-line synthesis:** *For UAV/road-marking perception, evaluate with topology-
aware metrics (clDice/TolIoU), train U-Net++/SegFormer with the CE+Dice loss (our proposed CoRe loss ties it across seeds, with higher variance — no reliable gain), and
deploy via ONNX/TensorRT — because mIoU alone provably mis-measures and mis-ranks
thin-structure perception, on real data, with statistical significance.*
