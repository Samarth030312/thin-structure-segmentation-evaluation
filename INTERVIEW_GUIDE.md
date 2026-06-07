# Interview Guide

Concise, technically-correct answers for perception interviews (Tesla, Waymo,
NVIDIA, Bosch, Mobileye). Each answer is grounded in this project's evidence and
stays honest about limits.

### Why does mIoU fail on thin structures?
IoU = intersection/union of pixels. For a 2–8 px marking, the object is almost all
boundary, so IoU is dominated by a ±1–2 px *width* mismatch. A perfectly localised
line predicted one pixel too wide/narrow loses much of its IoU even though it is
correctly detected. mIoU therefore conflates *detection* with *exact-width
matching*. Evidence: train at 4 px, test at 2 px → mIoU 0.35 but tolerance-IoU
0.97, clDice 1.0.

### Why are thin structures hard to segment?
Few pixels (severe class imbalance — 98% background, 609:1 in our data), so the
loss/gradient is dominated by background; high boundary-to-area ratio, so small
localisation errors are proportionally large; and aggressive encoder downsampling
destroys the signal. Skip-connection decoders (U-Net++) that preserve
high-frequency detail do best (Boundary-IoU 0.987 vs PSPNet 0.62).

### Why does clDice matter / why topology?
For lane perception the operational question is "is the lane line detected as one
continuous curve?" — a *topological* property. clDice skeletonises prediction and
GT and measures centerline overlap, so a broken/dashed prediction is penalised
even if pixel IoU is fine. Two models with equal mIoU can differ drastically in
connectivity; clDice sees it.

### Why did cross-domain transfer collapse?
We transferred a ground-view marking model to aerial land-cover and back. It
collapsed (off-diagonal clDice 0.13–0.46 vs in-domain 0.63–0.67) because the shift
combines *viewpoint* (ground↔aerial) and *semantics* (thin markings vs road
surface) — different low-level statistics and different label meaning. It's an
upper-bound on difficulty, not a clean domain-shift number; I'd want two datasets
sharing the task for a clean measurement.

### Why did your proposed loss (CoRe) not win?
Honest answer: it doesn't reliably help. It added a soft-clDice connectivity term
to CE+Dice. At one seed it beat the baseline (p<0.001), but across three seeds the
difference was null (Δ=−0.001, CI [−0.18, 0.18]) and it had ~2.4× the variance —
the skeleton term roughens the loss landscape. The single-seed "win" was an
artifact I only caught by running multiple seeds. That's the lesson, not a result.

### What did you learn scientifically?
(1) The evaluation metric is a *modeling choice* — mIoU can rank the worst model
first under imbalance, so report precision/recall/topology too. (2) Controlled
ablations and multi-seed runs are non-negotiable: I twice reached a wrong
conclusion (a confound, then a single-seed artifact) and only rigorous protocol
caught it. (3) Negative results are results — a non-working loss, honestly
reported, is more useful than an oversold one.

### What would you do differently / next?
Train to convergence on a ≥12 GB GPU (my real models were under-trained, clDice
0.37); validate on real aerial-UAV marking data (SkyScapes); expand the loss/seed
set for a statistically significant rank-inversion; and reframe the work honestly
as "thin-structure evaluation," not "UAV method."

### Company-specific angle
- **Tesla/Mobileye (vision-first, real-time):** the deployment Pareto (SegFormer-B0
  at 3.7 M params, ONNX 1.47× CPU speedup) and the "don't trust mIoU alone" message
  for lane perception.
- **Waymo (rigour):** the statistical discipline and self-correction story.
- **NVIDIA (systems):** the profiling (GPU-bound, conv-dominated), fp16-instability
  fix, and TensorRT path.
