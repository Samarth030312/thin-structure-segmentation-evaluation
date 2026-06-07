# Part 1 — Executive Overview

## 1.1 What problem was solved

Self-driving cars, driver-assistance systems, and automated map-makers all need to
**find road markings** — lane lines, stop lines, arrows, crosswalks — in images.
The computer-vision task that does this is called **semantic segmentation**: label
every pixel of an image with a class ("this pixel is lane-marking", "this pixel is
road", "this pixel is background").

To know whether a segmentation model is any good, you need a **metric** — a single
number that says how well the predicted labels match a human-drawn ground truth. The
overwhelmingly dominant metric in the field is **mean Intersection-over-Union
(mIoU)**. Almost every paper, leaderboard, and benchmark reports it.

The problem this project tackles is narrow but consequential:

> **For thin structures — road markings are typically 2–8 pixels wide — mIoU is a
> misleading metric. It reports a low score even when the model has correctly found
> the marking, because mIoU is exquisitely sensitive to small errors in the exact
> *width* of a thin object.**

If your evaluation metric lies, then everything built on top of it — model
selection, hyper-parameter tuning, "is version B better than version A?", go/no-go
decisions for deployment — can be wrong. A team could discard a genuinely better
thin-structure detector because mIoU told them it was worse. This project explains
*precisely when and by how much* that happens, and what to do instead.

## 1.2 Why it matters

Three reasons, in increasing order of depth.

1. **Practical (engineering).** Perception teams gate models on metrics. If mIoU
   under-credits thin-structure detectors, teams make systematically wrong choices
   for exactly the safety-critical thin things (lane lines!) that matter most for
   lane-keeping and HD-mapping. This monograph gives a **failure-threshold rule**:
   below ~5 px structure width, do not trust mIoU alone.

2. **Scientific (evaluation methodology).** "IoU is bad for thin objects" is *folk
   wisdom* — everyone half-knows it, nobody had written down *the exact functional
   form* of the error and validated it. This project converts the folk wisdom into a
   **derived, quantitative, falsifiable law** with a single physical parameter.

3. **Epistemic (how to do honest research on a tiny budget).** The entire project
   ran on a single 4 GB laptop GPU. It shows how to produce a defensible scientific
   result under severe compute limits by leaning on **controlled experiments and
   geometry** rather than brute-force scale — and how to report negative results and
   unreachable data honestly instead of papering over them.

## 1.3 What was discovered

The central discovery is the **width-coupling law**. In plain words:

- A good model usually *finds* a road marking — it puts the predicted marking in
  roughly the right place — but it gets the exact *boundary* slightly wrong, by
  about one pixel on each side. Call that boundary error `δ` (delta).
- mIoU measures **area overlap**. A one-pixel boundary error adds or removes a
  one-pixel "rim" all around the marking. For a 2-pixel-wide marking, that rim is as
  big as the marking itself, so mIoU plummets. For a 20-pixel-wide road, the same
  rim is negligible, so mIoU is fine.
- A **centerline metric** called **clDice** measures whether the *skeleton* (the
  one-pixel-thick spine) of the marking was found. The skeleton barely moves when
  the boundary wobbles by a pixel, so clDice stays high regardless of width.
- Therefore the **disagreement** between the two metrics — how much mIoU
  under-reports relative to clDice — follows

$$\text{Gap}(w) \;=\; \text{clDice} - \text{mIoU} \;\approx\; \frac{2\delta}{w + 2\delta},$$

where `w` is the structure width in pixels. This is an **inverse-width** curve: huge
for thin structures (`w → 0` gives Gap → 1), vanishing for wide ones (`w → ∞` gives
Gap → 0).

We did not merely *assert* this. We:

- **derived it** from pixel geometry (Part 7),
- **confirmed it** in a controlled experiment using pure synthetic shapes with no
  model and no dataset, getting an inverse-width fit with $R^2 = 0.98$ and rejecting
  linear, exponential, and logarithmic alternatives (Part 8),
- **validated it on real data**: three independent real datasets (Massachusetts
  Roads, LoveDA, UAVid) land on the curve that the controlled experiment fixed, to
  within a residual of 0.06 (Figure A), and
- **attacked it** ten ways (resolution changes, annotation noise, skeletonisation
  quirks, class imbalance, …) and watched it survive (Part 8, Part 9).

From the law we read off **operational thresholds**: a *failure* zone (`w < 5` px,
mIoU misleading by >20%), a *warning* zone (5–25 px), and a *safe* zone (`w > 25`
px, mIoU trustworthy).

## 1.4 What failed (honest negatives)

Good science reports what did not work. Three failures shaped the project:

1. **The proposed loss function (CoRe) did not help.** We designed a connectivity-
   aware loss (cross-entropy + Dice + a soft-clDice term) hoping it would beat a
   plain CE+Dice baseline at thin-structure segmentation. On a single random seed it
   looked better; across three seeds the advantage vanished (`Δ ≈ −0.001`, not
   significant). We report it as a **null result** and demote it to supplementary.
   *Lesson: single-seed deep-learning results are often noise.*

2. **UAVid did not show the effect.** We acquired real UAV imagery (UAVid) expecting
   to confirm the law on drone data. Instead the gap was ~0. Why? UAVid labels road
   *surfaces*, which are 12–35 px wide — too wide. This is a **dataset-level
   contradiction** that, properly understood, *confirms* the law: wide structures
   are in the safe zone. We documented it rather than hiding it.

3. **SkyScapes was unreachable.** The ideal dataset — aerial *lane markings* — is
   DLR-licence-gated and its download portal is network-unreachable from our
   environment (HTTP 000). We tried every channel, documented the failure, and used
   a legitimate substitute (Massachusetts Roads, which has genuinely thin roads)
   rather than fabricating data.

## 1.5 What remains open

- **Aerial road *markings* specifically.** The law is validated on synthetic
  markings and real thin *roads*, not real aerial *markings*. SkyScapes would close
  this; it needs a licence and adequate hardware.
- **A width-aware corrected metric.** The natural next step is to turn "mIoU is
  misleading" into "here is a drop-in fix" — a tolerance-banded or width-normalised
  IoU. This would raise the contribution from *diagnosis* to *cure*.
- **Per-architecture `δ`.** The law's scale parameter `δ` depends on the model. A
  small study measuring `δ` per architecture would let you *predict* each model's
  failure threshold in advance.
- **Scale.** All real models were trained on a 4 GB GPU with subsampled data. The
  *law* is robust to this (it rests on controlled geometry and converged binary
  models), but a full-scale multi-dataset benchmark would strengthen the applied
  claims.

## 1.6 The shape of the rest of the book

Parts 2–6 build the foundations a newcomer needs: what segmentation is, the maths of
tensors/convolutions/losses/metrics, the architectures, the datasets, and the logic
of the experimental design. Part 7 is the intellectual core — the full derivation of
the law. Part 8 walks every result. Part 9 is a defense drill (100 Q&A). Parts 10–11
teach the code and engineering. Part 12 looks forward. Part 13 is a 100-question
self-test with an answer key. Read linearly the first time; thereafter use it as a
reference.

---
