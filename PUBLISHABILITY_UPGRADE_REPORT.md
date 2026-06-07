# Publishability Upgrade Report

What changed in this rigor pass, what it bought, and an honest re-score. No new
engineering; the work was entirely about making claims harder to attack.

## 1. Score

| | Before | After | Why |
|---|---|---|---|
| **Publishability** | **50/100** | **67/100** | primary claim now converged + multi-seed + tight CIs; metric claim hardened and adversarially tested; honest repositioning |
| (target) | — | 80/100 | **not reached** — requires real UAV-marking data at scale + a sharper novelty hook, both outside the 4 GB / frozen-engineering constraints (see §6) |

I do not inflate to 80. The two upgrades below are real and move the needle
substantially; the residual gap to 80 is data/scale/novelty that cannot be
manufactured here, and I say so.

## 2. Upgrade 1 — the primary claim is now convergence-proof and seed-stable

Old: "mIoU collapses to 0.35 at 2 px" (single seed, models of unclear convergence).
New (`reports/multiseed_width_study.md`, `scripts/run_width_study_multiseed.py`):
**converged** models (clDice ≈ 0.997 at the training width), **3 seeds**, **95 %
CIs**:

| width | mIoU | clDice |
|---|---|---|
| 2 px | **0.351 ± 0.007** | **0.997 ± 0.001** |

The ~0.65 gap has **non-overlapping, tight CIs**. This directly answers the two
strongest reviewer objections at once: the models *converge* (not under-trained)
and the effect is *reproducible across seeds* (not anecdotal). Figure:
`paper_figures/fig1b_width_multiseed.{png,pdf}`.

**Converged real-data evidence (binary marking detection).** To further rebut
"under-trained," a 30-epoch run on real RLMD binary marking-vs-background *converges*
(val mIoU plateau, Δ = +0.017 over the last 5 epochs;
`paper_figures/fig6_convergence.{png,pdf}`) to a **usable operating point**:
clDice 0.64, clPrecision 0.88, clRecall 0.70. The 25-class difficulty was the
609:1 *imbalance*, not the framework: when the task is well-posed, the model
converges to a real detector that finds 70 % of marking centerlines at 88 %
precision.

## 3. Upgrade 2 — the metric claim, hardened by adversarial testing (Phase D)

The earlier "mIoU mis-ranks" was tested against *every* common metric
(`reports/metric_sensitivity_analysis.md`, `scripts/analyze_metric_sensitivity.py`)
via three tests: (T1) does the metric's top model flood the frame? (T2) does it
rank the genuine best detector first? (T3) is it foreground-sensitive?

| Metric | T1 | T2 | T3 | result |
|---|---|---|---|---|
| mIoU (fg) | floods | no (#3) | 0.023 | **fails** |
| mIoU (all-class) | floods | no (#3) | 0.023 | **fails** (defeats the "fg-averaging artifact" rebuttal) |
| FWIoU | ok | yes | 0.005 | fails (insensitive) |
| PixelAcc | ok | yes | 0.003 | fails (insensitive) |
| clDice | ok | yes | **0.310** | **passes all 3** |

This is *stronger* than the original claim (all-class mIoU also fails, so it is not
a foreground-averaging quirk) and *more precise* (FWIoU/PixAcc don't mis-rank but
are useless for foreground quality; only topology metrics resolve both).

## 4. Phase D — adversarial pass on every claim (kept / narrowed / removed)

| Claim | Attack | Outcome |
|---|---|---|
| mIoU under-reports detected thin markings | "under-trained / single-seed" | **survives, strengthened** — converged, 3-seed, CI (§2) |
| mIoU mis-ranks losses | "artifact of fg-averaging" | **survives, narrowed** — all-class mIoU also fails; scoped to multi-class extreme imbalance |
| "Use FWIoU/PixAcc instead" | "obvious fix" | **rebutted** — they are flood-robust but foreground-insensitive (spread ≤0.005) |
| CoRe loss helps | multi-seed | **removed** — ties baseline (Δ=−0.001, n.s.); now supplementary |
| Cross-dataset transfer is informative | confound | **demoted** — binary, disjoint taxonomies; labelled exploratory |
| "UAV" framing | no UAV marking data | **removed from claims** — repositioned as thin-structure evaluation |
| Architecture mis-ranking (DeepLab↔SegFormer) | synthetic only | **kept but labelled synthetic** |

## 5. Repositioning (Phase C)
Primary = **mIoU under-reports detected thin structures (width-coupling)**,
converged + CI. Secondary = **mIoU mis-ranks under extreme multi-class imbalance**,
with the three-test metric protocol. Supplementary = CoRe (null), cross-dataset
(confounded), deployment, architecture sweep. Title unchanged: *"When mIoU Lies."*

## 6. Remaining weaknesses, risks, and what 80/100 would require

| Remaining gap | Why it blocks 80 | What closes it |
|---|---|---|
| No real **UAV-marking** results | the field/venue expects on-domain data | SkyScapes (DLR licence) + ≥12 GB GPU; ingestion already built |
| Novelty still **moderate** | clDice/Boundary-IoU are prior work | the three-test protocol + converged width law help, but a stronger hook (e.g., a width-aware metric *correction*) would raise it |
| Multi-class real models under-trained | absolute numbers not headline-grade | full-RLMD, 50 epochs, ≥12 GB GPU |
| n=3 seeds | tighter CIs desirable | 5+ seeds at the converged budget |

**Conference suitability:** workshop (CVPR/ICCV ADW, WACV-W) — now a credible
submission; IEEE ITSC main — borderline (needs the UAV/scale items). **Journal
(T-ITS):** not yet; needs the full-scale, multi-dataset program.

## 7. Exact next experiments (priority)
1. SkyScapes aerial loss ablation + width analysis (closes the UAV gap; #1 for 80).
2. Full-RLMD converged runs, 5 seeds (tightens everything).
3. A width-aware mIoU *correction* (tolerance-banded IoU as a drop-in) — would turn
   "mIoU is bad" into "here is the fix," a stronger contribution.
4. Second marking dataset (CeyMo) for a clean (non-confounded) transfer matrix.
