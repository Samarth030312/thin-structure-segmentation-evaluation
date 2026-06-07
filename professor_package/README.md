# Project Brief — Width-Coupling of Segmentation Metrics (15-minute read)

## 1. Executive summary
Mean IoU (mIoU) is the standard metric for road/marking segmentation, but it
systematically under-reports *thin* structures that are in fact correctly detected.
We make this precise: there is a **geometric law** relating the disagreement between
mIoU and a centerline metric (clDice) to structure width *w*:

> **Gap(w) = clDice − mIoU ≈ 2δ / (w + 2δ)**,  δ = model boundary-localisation error (≈1 px).

The law is **derived from first principles**, **confirmed in a controlled
geometry experiment** (R² = 0.98, no dataset/model), **validated on three real
datasets** (their (width, gap) points land on the curve, Fig. A), and **survives 10
adversarial attacks**. It yields actionable **failure thresholds**: mIoU is
misleading below ~5 px (markings), safe above ~25 px (wide roads).

## 2. Key contributions
1. A **derived, confirmed geometric law** for area-vs-centerline metric
   disagreement on thin structures (the central result).
2. **Failure-threshold zones** (failure <5 px, warning 5–25 px, safe >25 px) —
   directly usable to gate perception evaluation.
3. **Multi-dataset validation** (synthetic + 3 real: MassRoads, LoveDA, UAVid) and
   a **thinness threshold** (effect present on thin aerial roads, absent on wide UAV
   roads — the boundary the law predicts).
4. A **reproducible benchmark/framework** (62 tests, CI, real-data ingestion,
   deployment path) — engineering support, not the scientific claim.

## 3. Scientific findings
- mIoU ≈ w/(w+2δ); clDice ≈ 1 for detected structures → gap = 2δ/(w+2δ).
- Controlled experiment: inverse-width family fits (R² 0.98); linear/exp/log rejected.
- Real datasets fall on the geometric curve (residual <0.06 for 3 of 4).
- The law is **resolution-invariant** (depends on the dimensionless ratio w/δ).
- It applies to **boundary errors with preserved topology**; for *topology* errors
  clDice correctly drops and the gap vanishes (the law's scope, not a failure).

## 4. Novelty assessment
**Moderate-High.** Turns a folk observation ("IoU is bad for thin things") into a
*derived, parameterised, thresholded, validated* law. The underlying metrics
(clDice, Boundary-IoU) are prior work; the law, its derivation, the thresholds, and
the real-data validation are the contribution.

## 5. Limitations (honest)
- δ is model-dependent (the *form* is universal, the *scale* is not).
- Experiments are compute-bounded (4 GB GPU); real models on the 25-class task are
  under-trained (the *law* uses converged models / controlled geometry, so it is
  unaffected).
- Real validation is on aerial *roads*, not aerial *markings* — SkyScapes (the ideal
  aerial-marking set) is licence-gated and unreachable (documented).
- A proposed connectivity loss (CoRe) gave no reliable gain — reported as a negative.

## 6. Future work
SkyScapes aerial-marking validation; full-scale converged runs; measure δ per
architecture and predict each model's failure threshold; a width-aware mIoU
correction (drop-in tolerance-banded IoU).

## 7. Reading order (≈15 min)
1. `reports/width_coupling_theory.md` — the law + fits (5 min).
2. `reports/first_principles_width_analysis.md` — the geometric derivation (4 min).
3. `paper_figures/figA_width_gap_law.pdf` — the killer figure (1 min).
4. `reports/failure_thresholds.md` — the practical payload (2 min).
5. `reports/controlled_robustness_study.md` + `reviewer_attack_campaign.md` — why
   it is a law, not an artifact (3 min).
6. `reports/law_assessment.md` and `final_paper_positioning.md` — conservative
   classification + positioning (skim).

## 8. Figures and tables
- **Fig A** width-gap law (controlled + real). **Fig B** relative error vs width.
- **Fig C** disagreement heatmap (width × δ). **Fig D** failure zones.
- Earlier: `fig1b_width_multiseed` (CI), `fig7_thinness_threshold` (cross-dataset).
- Tables: candidate-form fits (`width_coupling_theory.md`), thresholds
  (`failure_thresholds.md`), real-data validation (`massroads_width_validation.md`).

## 9. Reproduce
`python scripts/run_controlled_robustness.py` → `fit_width_law.py` →
`make_law_figures.py`. Real-data: `run_width_validation.py`. Tests: `pytest` (62).
