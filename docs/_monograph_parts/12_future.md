# Part 12 — Future Research

The project ends with a derived, validated law and a clear set of next steps. Here is
what to do, why, and what it would buy — in priority order.

## 12.1 A width-normalised / width-aware IoU (diagnosis → cure)

The strongest single upgrade. Right now the contribution is *diagnostic*: "mIoU
misleads on thin structures, by `2δ/(w+2δ)`." The natural cure is a **corrected
metric** that is trustworthy at all widths. Two concrete designs:

1. **Tolerance-banded IoU as a drop-in.** Replace the hard IoU with TolIoU (count
   pixels correct within `τ` px). It already stays high for detected thin structures
   (Part 8). Standardise `τ` (e.g. tie it to the estimated `δ`) and publish it as the
   recommended thin-structure metric.
2. **Width-normalised IoU.** Divide the boundary error out: since
   `IoU ≈ w/(w+2δ)`, an estimate `δ̂` lets you report `IoU·(w+2δ̂)/w` ≈ a
   width-corrected overlap. This turns "mIoU is bad" into "here is a number you *can*
   trust," which is a stronger, more citable contribution.

**Why it matters:** reviewers reward a *fix*, not just a complaint. This would move the
paper from "evaluation critique" toward "evaluation method."

## 12.2 Acquire SkyScapes (the decisive real-aerial-marking test)

The one experiment that closes the campaign's honest gap. SkyScapes is aerial *lane
markings* — genuinely thin, UAV viewpoint, the exact target domain. The thinness law
predicts a large gap there. Obtain the DLR licence + a ≥12 GB GPU, run the existing
ingestion (`scripts/prepare_skyscapes.py`) and `run_width_validation.py` unchanged.
**Outcome:** if confirmed, the "no aerial markings" limitation disappears and
publishability clears ~78–80.

## 12.3 Measure δ per architecture (a predictive tool)

The law's scale `δ` is the model's boundary-localisation error. A small study —
estimate `δ` for U-Net, DeepLabV3+, SegFormer, etc. by fitting `2δ/(w+2δ)` to each
model's width-stratified gap — yields a **per-architecture failure threshold** you can
quote *in advance*: "Model X (δ=0.7) is safe above 5 px; Model Y (δ=1.3) only above
10 px." This converts the law into a model-selection instrument.

## 12.4 Topology-aware metrics beyond clDice

clDice has a `w=1` degeneracy and a skeletonisation cost. Worth exploring: persistent-
homology / Betti-number errors (topology of connectivity), graph-based centerline
matching (APLS, used in road-network extraction), and learned tolerance bands. A
comparison of topology metrics on the controlled benchmark would clarify which is the
best practical reference.

## 12.5 New benchmark opportunities

The controlled-geometry harness (`run_controlled_robustness.py`) is itself a
contribution: a **synthetic, parameterised thin-structure metric benchmark** where
width and error are knobs. Packaged and released, it lets others test *any* new metric
against the width-coupling law. This is a low-cost, high-leverage artifact.

## 12.6 Real UAV road-marking data collection

If public aerial-marking data stays gated, collecting even a small, well-annotated UAV
marking set (a few dozen drone images with lane-line masks) would be a genuine
community contribution and the ideal home-domain validation. Annotation is the cost;
the pipeline is ready.

## 12.7 Beyond roads — generality

The derivation is geometric and applies to any thin structure: blood vessels, cracks
in materials, neurons, wires, rivers in satellite imagery. A cross-domain study (one
medical, one remote-sensing, one industrial dataset) would show the law is a property
of *thin-structure evaluation* in general, not road markings specifically — a broader,
higher-impact framing.

## 12.8 Potential publications (realistic)

1. **Workshop paper (now):** "When mIoU Lies: A Geometric Width-Coupling Law for
   Thin-Structure Segmentation Metrics" — the law, controlled + real validation,
   thresholds. Target CVPR/ICCV/WACV evaluation or autonomous-driving workshops
   (~70% acceptance, `FINAL_RESEARCH_VERDICT.md`).
2. **ITSC/IV paper (with §12.1 fix):** add the width-corrected metric → an
   evaluation *method*, not just a critique (~50–60%).
3. **Journal (T-ITS, later):** with SkyScapes + full-scale + cross-domain → the
   comprehensive version (~35% → higher once the data exists).

## 12.9 The single most important next step

If you do only one thing: **build the width-corrected metric (§12.1).** It is cheap
(no new data, no training — it reuses the existing metrics and the law), and it
transforms the work from "here is a problem" into "here is the solution," which is the
difference between a workshop note and a method paper.

---
