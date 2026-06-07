# Law Assessment: Is It a Law, a Heuristic, or an Artifact?

Conservative classification of the width-coupling observation, against five
hypotheses. Evidence first.

## The candidate statement
> For a *detected* thin structure of width *w* (px), the disagreement between an
> area-overlap metric (mIoU) and a centerline metric (clDice) is
> `Gap = clDice − mIoU ≈ 2δ/(w + 2δ) = 1/(1 + w/2δ)`, where δ is the model's
> per-side boundary-localisation error.

## Hypothesis tests

| Hypothesis | Evidence for | Evidence against | Verdict |
|---|---|---|---|
| **Measurement artifact** (bug in our metrics) | — | reproduced with reference metrics + 62 unit tests; numeric matches the *analytic* derivation (R²=0.98) | **rejected** |
| **Benchmark artifact** (specific to our synthetic data) | — | reproduced on 4 independent sources incl. 3 real datasets, all on one curve (Fig. A) | **rejected** |
| **Dataset-specific observation** | the 4 dataset points alone are few | controlled geometry (no dataset) reproduces it; datasets merely sample the curve at their widths | **rejected as the full story** |
| **Heuristic** (useful rule, no mechanism) | it *is* useful | it has a first-principles geometric derivation and a single physical parameter δ; not merely empirical | **stronger than a heuristic** |
| **Geometric law / principle** (derived, falsifiable, confirmed, scoped) | derivation (Sec. `first_principles`), controlled R²=0.98, 3 real datasets on-curve, survives 10 attacks, resolution-invariant (dimensionless w/δ) | bounded scope (see below) | **best-supported** |

## Conservative classification
We classify it as a **scoped geometric law** (equivalently, a *principle*) governing
the disagreement between area-overlap and centerline metrics under boundary
mislocalisation — **not** a universal "law of segmentation metrics." Precisely:

- It is **derived** (geometry, one parameter δ), **quantitative**, **falsifiable**
  (predicts specific gaps), and **confirmed** out-of-sample (3 real datasets land on
  a curve fixed by the controlled experiment, residual <0.06).
- It is **not an artifact** (controlled geometry rules out dataset/metric/benchmark
  artifacts) and **stronger than a heuristic** (it has a mechanism and a parameter).

## Documented scope (where it is a law, and where it is not)
1. **Holds:** *detected* thin structures (topology preserved) with **boundary/width
   errors** — the dominant real failure mode. w ≳ 2 px (sub-pixel skeletons are
   degenerate).
2. **Does not apply:** *topology* errors (broken/missed structures) — there clDice
   correctly drops and the gap vanishes, width-independent.
3. **Specific to:** area-overlap vs centerline/tolerance metrics. It does not claim
   anything about, e.g., mIoU vs Dice (both area metrics; they track together).
4. **δ is model-dependent** (≈0.7–1 px here); the *form* is universal, the *scale*
   is not.

## What would falsify it
A *detected* thin structure (clDice ≥ 0.9) whose mIoU–clDice gap does **not** fall
with width, or a real dataset whose (width, gap) lands far off the curve in the
boundary-error regime. None was found across 4 datasets and 6 controlled
degradation types.

## Honest bottom line
Within its scope this is a **bona-fide geometric law**, not a heuristic or artifact:
derived, parameterised, confirmed on real data, and robust to attack. Its
contribution is to make the long-noted "IoU is bad for thin things" precise,
mechanistic, and predictive — and to delimit exactly when it does and does not hold.
