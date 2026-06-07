# Repository Truth Audit (Phase 1)

Adversarial. Every row cites exact files. "NOT VERIFIED" where evidence is absent.

| Document | Central claim | Evidence source | Figures/Tables | Scripts | Does evidence support the claim? |
|---|---|---|---|---|---|
| `README.md` | mIoU under-reports thin structures; `Gap=2δ/(w+2δ)`; framework + 62 tests | links to `reports/width_coupling_theory.md`, `paper_package/`, `figA` | figA | `run_controlled_robustness.py`, `fit_width_law.py`, `make_law_figures.py` | **Yes**, for the law. README is now consistent with the paper. |
| `paper_package/final_ieee_paper.{md,pdf}` | "When mIoU Lies"; law + thin-structure protocol | `reports/*`, leaderboard, width study | Tables II/III, figs | scripts/* | **Yes**, with honest scope caveats stated in the paper text. clDice/Boundary-IoU cited (`\bibitem{cldice}`, `\bibitem{biou}`). |
| `reports/final_report.md` | rewritten to the law narrative | `reports/*`, validation JSONs | figA | scripts/* | **Yes** (was stale; now matches paper). |
| `reports/width_coupling_theory.md` | inverse-width law, R²=0.98; real datasets on curve | `reports/controlled/{robustness_sweeps,law_fit}.json`, `reports/visualizations/uav_validation/*_width_val.json` | figA | `fit_width_law.py`, `make_law_figures.py` | **Yes** — table values now MEASURED (`measured_mean_width_px`). |
| `reports/law_assessment.md` | "scoped geometric law, not artifact" | controlled study + real data + attacks | figA | `run_controlled_robustness.py` | **Partly** — see caveat: the controlled study is self-consistent by construction (`final_release_audit.md` M1). Disclosed. |
| `reports/failure_thresholds.md` | FAILURE<5px, WARNING 5–25px, SAFE>25px | derived from `Gap=2δ/(w+2δ)`, δ=0.67 | figD | `make_law_figures.py` | **Yes, derived** (w_fail≈8δ≈5px; w_safe≈38δ≈25px). The 0.2/0.05 gap cutoffs are **conventions**, not measured — stated. |
| `reports/metric_sensitivity_analysis.md` | mIoU mis-ranks under imbalance; only clDice passes 3 tests | `reports/leaderboard.csv`, `analyze_metric_sensitivity.py` | Table II | `analyze_metric_sensitivity.py` | **Yes** — numbers match `paper_tables/table2_rlmd_loss_ablation.md`. |
| `FINAL_RESEARCH_VERDICT.md` | publishability ~78/100 | self-assessment | — | — | **Self-assessment, not independent.** Contradicts other top-level verdicts (50/67/75) — see §Contradictions. |
| `LICENSE` | MIT | — | — | — | **Valid** MIT text present. |
| `DATA_LICENSES.md` | dataset licences (NC flagged), no redistribution | dataset cards | — | — | **Yes**; but verify each licence at source (we did not re-fetch licences — partial). |

## Contradictions found (CONFIRMED)
- **Multiple, divergent "verdict/readiness" documents at top level** with different
  publishability scores: `FINAL_VERDICT.md` (50 and 67), `FINAL_RESEARCH_VERDICT.md`
  (78), `PUBLISHABILITY_UPGRADE_REPORT.md` (50→67), `UAV_VALIDATION_VERDICT.md`
  (67→75). A reader cannot tell which is authoritative. **Documentation drift.**
- **`pyproject.toml:8`** still describes the project as *"An evaluation framework for
  Indian road-marking segmentation from UAV imagery."* — the discredited framing the
  integrity reconstruction claimed to remove. **Stale metadata.**

## Unsupported / unverifiable items
- **`reports/failure_thresholds.md`** thresholds depend on δ≈1 px (model-specific);
  the "5 px / 25 px" numbers are **not universal** (the report says so).
- **CoRe null-result CI** ("Δ≈−0.001, 95% CI [−0.18,0.18]"): the means in
  `paper_tables/table7_multiseed.md` are consistent (ce_dice clDice 0.4045 vs core
  0.4056) but the table's `mean_diff` and `ci95` columns are **`nan`** — the stated CI
  is **NOT VERIFIED from the provided table**.

## Verdict
The four *previously critical* claims (phantom dataset, README/report framing,
Figure A) are now supported. **Two new stale/contradiction issues** (pyproject
description; multiple divergent verdicts) and **one unverifiable statistic** (CoRe CI
column = nan) remain.
