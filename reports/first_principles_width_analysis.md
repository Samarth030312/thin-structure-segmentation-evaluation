# First-Principles Derivation of the Width-Coupling Law

A geometric, pixel-level explanation of why IoU collapses on thin structures while
clDice does not — accessible to CV researchers, perception engineers, and autonomy
engineers.

## 1. Setup
Consider a correctly-detected thin structure (a road, lane line, marking) of width
*w* pixels and length *L*. Its area is `A = w·L`. A segmentation model rarely places
the *boundary* exactly; assume a per-side boundary-localisation error of *δ* pixels
(δ ≈ 0.5–1 px is typical — sub-pixel-to-1-pixel edge error). The prediction is the
same structure with its boundary off by δ.

```
   GT (width w)          Prediction (boundary off by  δ per side)
   ┌───────────┐         ┌─────────────────┐
   │███████████│   →     │░███████████░│        ░ = δ-px error rim
   └───────────┘         └─────────────────┘     (here an over-segmentation)
        w                     w + 2δ
```

## 2. Why IoU depends strongly on width
Intersection (overlap) ≈ the GT area `w·L`. Union ≈ the larger of the two ≈
`(w+2δ)·L` for over-segmentation. Therefore

  **IoU ≈ (w·L) / ((w+2δ)·L) = w / (w + 2δ).**

This is the entire effect. The error rim has *fixed* width 2δ; whether it matters
depends on how it compares to *w*:
- **w = 2, δ = 1:** IoU ≈ 2/4 = **0.50** — the rim is as big as the structure.
- **w = 20, δ = 1:** IoU ≈ 20/22 = **0.91** — the rim is negligible.

IoU is an **area-ratio** metric, so a fixed-size boundary error costs a *fraction*
of area that scales as 1/w.

## 3. Why clDice remains stable
clDice measures overlap of *centerlines* (skeletons), not areas:
`clDice = 2·Tprec·Tsens / (Tprec+Tsens)`, with Tprec = |skel(pred) ∩ GT| / |skel(pred)|
and Tsens = |skel(GT) ∩ pred| / |skel(GT)|. A δ-px boundary error (dilation/erosion/
small shift) **does not move the centerline**: skeletonising a slightly-wider or
slightly-shifted structure yields essentially the same medial axis, which still lies
inside the GT and vice-versa. So Tprec ≈ Tsens ≈ 1 and **clDice ≈ 1**, independent of
*w*. Topology, not area, is what clDice sees — and topology is invariant to boundary
jitter.

## 4. Why the disagreement collapses as width increases

  **Gap(w) = clDice − IoU ≈ 1 − w/(w+2δ) = 2δ / (w + 2δ).**

- As **w → 0** (δ-scale thin): Gap → 1. mIoU and topology maximally disagree.
- As **w → ∞** (wide): Gap → 0. The fixed rim vanishes relative to the area; mIoU
  agrees with clDice.
- The crossover is at **w ≈ 2δ** (≈ 1.5–2 px), where the gap is ≈ 0.5.

This is *why* the effect is a property of thinness: it is the ratio of a fixed
boundary-error length-scale (2δ) to the structure's width.

## 5. Pixel-level worked example (w=3, δ=1)
GT: a 3-px-wide line, 100 px long → 300 px. Prediction over-segments by 1 px each
side → 5-px-wide → 500 px, fully containing GT. Intersection 300, union 500 →
**IoU = 0.60**. Skeleton of both is the same 1-px centerline → **clDice ≈ 1.0**.
Gap = 0.40. The model *found the line perfectly*; mIoU reports 0.60 because it is
penalising 200 px of boundary rim.

## 6. Why this matters for perception/autonomy
For lane perception and HD-mapping the operational question is *"did we find the lane
line, continuously and in the right place?"* — a topological/centerline property.
mIoU answers a *different* question ("did we match its exact pixel width?") and, for
markings 2–8 px wide, conflates the two. A perception team selecting or gating
models on mIoU will systematically under-credit thin-structure detectors by the
amount `2δ/(w+2δ)`. Report a centerline/tolerance metric alongside mIoU.

## 7. Scope (where the derivation does NOT apply)
The derivation assumes the *boundary* is off but the *structure is detected*
(topology preserved). If the prediction instead **breaks** the structure (gaps,
missed segments), clDice *correctly* drops and the area-ratio argument no longer
gives a large gap — confirmed empirically (`controlled_robustness_study.md`). The
law describes detected-but-mislocalised thin structures, which is the dominant real
failure mode.
