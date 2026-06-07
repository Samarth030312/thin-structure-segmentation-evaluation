# Part 6 — Experimental Design

Good experiments are *arguments*. Each design choice in this project exists to close a
specific loophole a skeptic could exploit. This part explains the reasoning so you
can defend every choice.

## 6.1 Why synthetic experiments were created

A real dataset confounds many variables at once: width, appearance, lighting,
annotation quality, class frequency. If you observe "mIoU is low on this dataset," you
cannot tell *why*. The synthetic generator lets you **hold everything fixed and change
one thing** — the structure width. That is the only way to attribute the effect to
*width* rather than to some dataset idiosyncrasy. Controlled synthesis trades realism
(irrelevant for a metric study) for **causal clarity** (essential).

## 6.2 Why width-controlled experiments matter

The thesis is a statement about a *function* `Gap(w)`. To characterise a function you
must vary its input across a range and observe the output. A single width gives one
point; you cannot fit or falsify a curve from one point. So the design sweeps width
across `{1,2,3,4,5,6,8,10,12,15,20,25,30}` px — 13 points — which is enough to
distinguish an inverse-width curve from a line, an exponential, or a logarithm
(Part 8 shows linear/exp/log are rejected, inverse-family wins at `R²≈0.98`).

## 6.3 How width was manipulated (two complementary methods)

1. **Generative (training data):** the synthetic renderer paints structures at a
   chosen thickness. Models trained at width 4 px are evaluated across the width
   series (`datasets/width_series/`), exposing how a fixed model's mIoU degrades as
   test structures get thinner/wider.

2. **Controlled-geometry (no model):** in `scripts/run_controlled_robustness.py` we
   generate a structure of width `w`, then *manufacture* a "prediction" by applying a
   **known degradation** (dilate/erode/shift the boundary by a fixed number of
   pixels) and compute the metrics directly. This is the cleanest manipulation: there
   is **no training, no model, no dataset** — only geometry and a controlled error
   `δ`. If the law appears here, it cannot be a model or data artifact.

Width is *measured* on real data (where we cannot set it) via the **Euclidean
distance transform**: for each foreground pixel, `2 × EDT` gives the local structure
width. This lets us place each real dataset on the `Gap(w)` axis (Part 8, Fig. A).

## 6.4 Why multi-seed evaluation matters

Deep-learning training is **stochastic**: random weight initialisation, random data
shuffling, and nondeterministic GPU ops mean two runs differ. A result from **one
seed can be noise**. The project's own cautionary tale: the CoRe loss beat the
baseline on seed 42 (`p < 0.001`!) but, across seeds 42/123/999, the advantage
*vanished* (`Δ ≈ −0.001`). Had we trusted one seed we would have published a false
positive. **Rule: report mean ± confidence interval over ≥3 seeds for any
comparative claim.** The width-validation results (UAVid mIoU 0.57 ± 0.03, MassRoads
gap +0.27 across 3 seeds) follow this.

## 6.5 Why statistical significance matters

A difference of "0.49 vs 0.51" is meaningless without knowing the *spread*. The
project uses:
- **Bootstrap confidence intervals:** resample the per-image scores with replacement
  many times to estimate the metric's sampling distribution and a 95% CI — no
  normality assumption needed.
- **Paired bootstrap tests:** for "is A better than B?", resample the *paired*
  per-image differences; if the 95% CI of the mean difference excludes 0, the
  difference is significant.
- **Tight, non-overlapping CIs** are what let us say the width effect is *real*: at
  2 px, mIoU 0.351 ± 0.007 vs clDice 0.997 ± 0.001 — the intervals do not come close
  to overlapping.

## 6.6 Why cross-dataset validation matters

A law that only holds on the data it was derived from is a *description*, not a
*law*. The design therefore **fixes the curve on the controlled experiment** and then
checks whether **independent real datasets** (MassRoads, LoveDA, UAVid) — never used
to fit the curve — fall on it. Three of four land within 0.06 (the fourth, synthetic,
sits high because its error regime differs). Out-of-sample agreement across datasets
of different viewpoints (ground, aerial, UAV) is the strongest evidence that the
effect is geometric and general, not a benchmark quirk.

## 6.7 Why reviewer attacks were performed

The scientific method is *attempted falsification*, not accumulation of supporting
examples. The project explicitly tries to **destroy** its own law (Part 9): vary label
thickness, add annotation noise, change resolution (down/up-sample), probe
skeletonisation artifacts, test class imbalance, crop size, boundary noise, and
metric-implementation correctness. A law that survives ten genuine attacks is far more
credible than one supported by ten friendly examples. Two attacks even *sharpened* the
law (it is resolution-invariant because it depends on the dimensionless ratio `w/δ`;
it correctly vanishes for topology errors because then the structure is not
"detected").

## 6.8 The experimental hierarchy (how the pieces argue together)

```
  Claim strength ladder (weakest → strongest)
  1. Anecdote:      "mIoU looked low on one thin image."
  2. Dataset trend: "mIoU < clDice on RLMD / LoveDA / MassRoads."
  3. Controlled:    "Sweep width with all else fixed → inverse-width curve, R²=0.98."
  4. Derivation:    "Geometry predicts Gap = 2δ/(w+2δ) a priori."
  5. Out-of-sample: "3 real datasets land on the derived curve (resid < 0.06)."
  6. Adversarial:   "Survives 10 falsification attempts; scope mapped."
```

The project climbs the whole ladder. Most evaluation papers stop at rung 2; reaching
rungs 3–6 is what turns "an observation" into "a law."

## 6.9 Controls, baselines, and fairness

- **Same-architecture comparisons:** the loss ablation fixes U-Net++ and varies only
  the loss, so differences are attributable to the loss.
- **Pre-trained encoders + identical schedules:** every model uses ImageNet
  pre-training, AdamW, cosine LR, fp32 — removing training-protocol confounds.
- **Converged models for claims:** the width law uses converged synthetic models
  (clDice 0.997) and converged binary real models, so "under-training" cannot explain
  the effect.
- **Honest negatives kept in:** UAVid (no effect) and CoRe (no gain) are reported,
  not dropped — removing them would bias the picture.

---
