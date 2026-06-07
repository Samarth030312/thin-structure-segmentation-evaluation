# Plates — The Figures

The key figures of the project, collected for reference. Generate all with
`python scripts/make_law_figures.py` and `scripts/run_width_validation.py`.

![Figure A — The width-coupling law. Controlled geometry points (grey) trace the inverse-width curve Gap = 2 delta/(w+2 delta); three of four real datasets (stars) land on the curve fixed by the controlled experiment.](../paper_figures/figA_width_gap_law.png)

![Figure B — Relative metric under-report (clDice - mIoU)/clDice versus structure width. Over 50 percent at 1 px, about 5 percent by 30 px.](../paper_figures/figB_relative_error.png)

![Figure C — Metric-disagreement heatmap. Gap as a function of structure width and boundary error delta; the hot corner is thin and poorly localised.](../paper_figures/figC_disagreement_heatmap.png)

![Figure D — mIoU reliability zones: FAILURE (under 5 px), WARNING (5 to 25 px), SAFE (over 25 px), shaded under the law curve.](../paper_figures/figD_failure_zones.png)

![Figure E — Multi-seed converged width study with 95 percent confidence intervals: mIoU collapses on thin markings while clDice and tolerance-IoU stay near 1.](../paper_figures/fig1b_width_multiseed.png)

![Figure F — Cross-dataset thinness threshold: the under-reporting gap decreases monotonically with structure width across synthetic and three real datasets.](../paper_figures/fig7_thinness_threshold.png)

---
