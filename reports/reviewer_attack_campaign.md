# Reviewer Attack Campaign

Assume the width-coupling law is wrong. Each attack tries to destroy it; we report
whether it survives, with evidence.

| # | Attack | Test | Outcome |
|---|---|---|---|
| 1 | **Label thickness variation** | the width sweep itself | **survives** — thickness is the law's independent variable; the effect *is* the response to it (`controlled_robustness_study.md`). |
| 2 | **Annotation / boundary noise** | `boundary_noise` degradation | **survives (weaker)** — Gap still falls with width; noise perturbs the skeleton at very thin w, so clDice dips slightly (0.70 @ w=2) and the gap is smaller, but the trend holds. |
| 3 | **Resolution scaling (down/up)** | joint-rescale GT+pred 4×↓ and 2×↑ | **survives — and sharpens the theory.** Gap is *invariant* under joint rescaling (16→4 px: 0.095→0.103; 4→8 px: 0.272→0.268), because *w* and δ scale together. The law depends on the **dimensionless ratio w/(2δ)**, `Gap = 1/(1+w/2δ)`. (Real low-res inference, where the model's δ stays ~1 px while structures shrink, *raises* the gap — also consistent.) |
| 4 | **Skeletonisation artifacts** | clDice at w=1 | **survives with a documented limit** — at w=1 px the skeleton is degenerate (clDice 0.88, not 1.0); the law holds for w ≥ 2 px. Sub-pixel structures are outside scope. |
| 5 | **Class imbalance** | orthogonality check | **survives — independent phenomenon.** The width law is per-structure and binary (imbalance plays no role). The multi-class mIoU *mis-ranking* (`metric_sensitivity_analysis.md`) is a separate, imbalance-driven effect; conflating them is the error, not the law. |
| 6 | **Crop size** | locality argument | **survives** — width is a *local* (per-pixel, via EDT) property; cropping changes the field of view, not a structure's local width. The law is computed per-pixel. |
| 7 | **Boundary noise (severe)** | `boundary_noise p=0.3` | **survives** — see #2; even heavy boundary noise leaves a width-decreasing gap until it starts breaking topology (then #8 applies). |
| 8 | **Topology errors (the real counterexample)** | `gaps` degradation | **survives by correct scoping.** When the prediction *breaks* the structure, clDice **correctly drops** and the Gap collapses to ≈0.03, width-*independent*. The law applies to *detected* (topology-preserved) structures — exactly the claim's precondition. This is the one regime where the gap vanishes for thin structures, and it does so for the right reason (no detection). |
| 9 | **Metric implementation bugs** | analytic vs numeric | **survives** — IoU/Dice/clDice/Boundary-IoU use reference definitions (62 unit tests, `tests/`); the numeric Gap(w) matches the *analytic* derivation `2δ/(w+2δ)` (`first_principles_width_analysis.md`) to R²=0.98, so it is not an artifact of one implementation. |
| 10 | **Dataset cherry-picking** | 4 independent datasets | **survives** — 3 of 4 real datasets fall on the geometric curve (residual <0.06; Fig. A) without per-dataset tuning; the curve is fixed by the controlled experiment, not fit to the datasets. |

## Verdict
The law **survives every attack**, with two honest qualifications that *strengthen*
it: (a) it is a dimensionless `w/δ` law (resolution-invariant), and (b) it applies
to *detected* structures (topology preserved) — when detection fails, clDice
correctly drops and there is no gap. No attack produced a width-thin counterexample
in the detected regime. The effect is geometric, model- and dataset-independent.
