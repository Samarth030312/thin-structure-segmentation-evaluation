# Final Technical Report — When mIoU Lies

**The Width-Coupling Law for Thin-Structure Segmentation Evaluation**

> This report supersedes the project's initial benchmark-building phase. The
> authoritative, current narrative is the **width-coupling law**; the supporting
> framework (model zoo, dataset validation, loss study) is infrastructure, not the
> contribution. Source of truth: `paper_package/final_ieee_paper.pdf`.

---

## Abstract

Mean Intersection-over-Union (mIoU) is the de-facto metric for road-marking
semantic segmentation. We show it systematically under-reports *thin* structures
(road markings, lane lines, narrow roads) that a model has correctly detected, and
we make this precise with a geometric law: the disagreement between mIoU and the
centerline metric clDice obeys `Gap(w) = clDice − mIoU ≈ 2δ/(w+2δ)`, where `w` is
structure width in pixels and `δ` is the model's boundary-localisation error. The
law is derived from pixel geometry, confirmed in a controlled model-free experiment
(inverse-width fit, R²=0.98; linear/exponential/log rejected), validated on three
real datasets (Massachusetts Roads, LoveDA, UAVid), and survives ten adversarial
attacks. It yields actionable thresholds: mIoU is misleading below ~5 px and
reliable above ~25 px. We report two honest negatives — a proposed connectivity
loss (CoRe) that ties the baseline, and a wide-road UAV dataset (UAVid) where the
effect is correctly absent — and one honest gap: no aerial road-*marking* dataset
(SkyScapes is licence-gated and was unreachable).

## 1. Problem

Road markings are thin (2–8 px), sparse (<2% of pixels), and topologically
important (a lane line must be continuous and correctly placed). mIoU, an
area-overlap metric, conflates *detection* with *exact-width matching* and so can
misrank or under-credit thin-structure detectors — a problem because perception
teams select and gate models on mIoU.

## 2. Method

**Metrics.** Region metrics (mIoU, Dice, FWIoU, pixel accuracy) plus a
thin-structure suite: clDice (centerline Dice), Boundary-IoU, tolerance-IoU, and
width-stratified IoU (`src/uavroadmark/metrics/`).

**The law.** For a detected structure of width `w` with a per-side boundary error
`δ`: over-segmentation gives intersection `wL`, union `(w+2δ)L`, so
`IoU ≈ w/(w+2δ)`; the skeleton is unmoved by uniform boundary error, so `clDice ≈
1`; hence `Gap = 1 − w/(w+2δ) = 2δ/(w+2δ)` (`reports/first_principles_width_analysis.md`).

**Controlled experiment.** A model-free width sweep (1–30 px) with a fixed
boundary error reproduces the curve (`scripts/run_controlled_robustness.py`,
`fit_width_law.py`).

**Real-data validation.** Converged binary-road models on UAVid, Massachusetts
Roads, and LoveDA; per-image width measured by the distance transform; gap placed
against the curve (`scripts/run_width_validation.py`).

## 3. Results

- **Controlled fit:** inverse-width family wins (power R²=0.989, rational 0.986,
  derived inverse 0.977); linear (0.626), exponential (0.892), log (0.937)
  rejected.
- **Real data:** Massachusetts Roads mIoU 0.49 vs clDice 0.76 (gap +0.27, 3 seeds);
  LoveDA gap +0.22; UAVid (wide roads) gap ~0 — consistent with the safe-zone
  prediction (`reports/massroads_width_validation.md`, `uav_claim_validation.md`).
- **Thresholds:** FAILURE < 5 px (gap > 0.2), WARNING 5–25 px, SAFE > 25 px
  (`reports/failure_thresholds.md`).
- **Mis-ranking under imbalance:** on RLMD (609:1), mIoU ranks a frame-flooding
  model first; only clDice passes a three-test metric check
  (`reports/metric_sensitivity_analysis.md`).

## 4. Honest negatives and limitations

- **CoRe loss:** no reliable multi-seed gain (Δ ≈ −0.001); reported as a null
  result.
- **UAVid:** no effect (roads are 12–35 px wide) — bounds the law rather than
  contradicting it.
- **No aerial markings:** SkyScapes is gated/unreachable
  (`reports/skyscapes_acquisition_attempt.md`); validation uses real thin *roads*.
- **Novelty:** the law is IoU's definition made explicit (parameterised,
  thresholded, validated); honest ceiling is workshop/ITSC
  (`FINAL_RESEARCH_VERDICT.md`).
- **Compute:** 4 GB GPU; 25-class real models are under-trained, but the law rests
  on controlled geometry and converged binary models.

## 5. Conclusion

mIoU is a predictably misleading metric for thin road markings; the width-coupling
law says exactly when and by how much, and the failure thresholds say what to do
about it (report clDice/tolerance-IoU below ~5 px). The framework, datasets, and 62
tests support reproduction. See `paper_package/final_ieee_paper.pdf` for the paper
and `docs/UAV_Roadmark_Master_Monograph.pdf` for the full treatment.
