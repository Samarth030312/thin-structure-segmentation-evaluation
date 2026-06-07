# Figure Provenance Report (Phase 2)

Every figure in `paper_figures/` (PNG + PDF), traced to its generation script, source
data, and any manual constants. Classification: **GREEN** (all values measured),
**YELLOW** (derived but defensible), **RED** (contains hand-assigned values).

| Figure | Script | Source data | Manual values? | Class |
|---|---|---|---|---|
| `figA_width_gap_law` | `make_law_figures.py:fig_A` | `reports/controlled/{robustness_sweeps,law_fit}.json` + `reports/visualizations/uav_validation/*_width_val.json` (`measured_mean_width_px`,`measured_mean_gap`) | none (real points now loaded via `load_real_points()`) | **GREEN** |
| `fig7_thinness_threshold` | `make_law_figures.py:fig_thinness` | validation JSONs (measured) + `law_fit.json` | none | **GREEN** |
| `figB_relative_error` | `make_law_figures.py:fig_B` | `reports/controlled/robustness_sweeps.json` | none | **GREEN** |
| `figC_disagreement_heatmap` | `make_law_figures.py:fig_C` | recomputed from geometry (`run_controlled_robustness` fns) | δ grid {1,2,3,4} (controlled inputs, not results) | **GREEN** |
| `fig1b_width_multiseed` | `run_width_study_multiseed.py` | `reports/visualizations/width_study_multiseed/width_multiseed.json` | none (3 seeds, bootstrap CIs) | **GREEN** |
| `fig6_convergence` | `plot_learning_curve.py` | `outputs/rlmdbin_converge/history.json` | none (real training log) | **GREEN** |
| `fig1_width_study` | `make_paper_figures.py` | `reports/visualizations/width_study/width_study.json` | none | **GREEN** |
| `fig2_rlmd_loss_ablation` | `make_paper_figures.py` | `reports/leaderboard.csv` | none | **GREEN** |
| `fig3_perf_pareto` | `make_paper_figures.py` | `reports/leaderboard_performance.csv` | none | **GREEN** |
| `fig4_stats_ci` | `make_paper_figures.py` | leaderboard + bootstrap | none | **GREEN** |
| `figD_failure_zones` | `make_law_figures.py:fig_D` | `law_fit.json` (δ) for the curve | **zone cutoffs Gap=0.20 and Gap=0.05 are chosen conventions**; label x-positions hand-placed | **YELLOW** |
| `fig5_cross_dataset` | `run_cross_dataset.sh` | cross-dataset run (real) | none, but the **experiment is confounded** (disjoint taxonomies, tiny test set) | **YELLOW** |

## RED items
**None remain.** The two figures previously RED (`figA`, `fig7` — hand-assigned real
widths) were regenerated from measured values (`scripts/run_width_validation.py` now
emits `measured_mean_width_px`/`measured_mean_gap`; `make_law_figures.py` loads them).

## YELLOW items — danger, attack, fix

### `figD_failure_zones`
- **Danger:** the FAILURE/WARNING/SAFE boundaries use **manually chosen gap cutoffs**
  (0.20 and 0.05). A reviewer will say "why 0.2? why 0.05? the zones are arbitrary."
- **Reviewer attack:** *"Your 'failure threshold of 5 px' is an artifact of an
  arbitrary 0.2 gap cutoff and a single δ=0.67; it is not a property of the data."*
- **Fix:** state the cutoffs as **conventions** in the caption (they are, in
  `reports/failure_thresholds.md`), report the threshold as a **function of δ**
  (`w_fail≈8δ`, `w_safe≈38δ`), and label the figure *illustrative*. Do not present
  "5 px" as a universal constant.

### `fig5_cross_dataset`
- **Danger:** the cross-dataset transfer is confounded (RLMD markings vs LoveDA roads,
  disjoint taxonomies, ~41 test images). Presented as evidence it would mislead.
- **Reviewer attack:** *"This transfer result is meaningless — different label spaces
  and a tiny test set."*
- **Fix:** it is already labelled exploratory in `reports/cross_dataset_generalization.md`;
  **keep it out of the paper's evidentiary claims** and caption it "exploratory,
  confounded." Do not cite it to support the law.

## Verdict
Post-reconstruction, **no figure contains hand-assigned data values** (the critical
defect is fixed). Two figures are YELLOW: `figD` (convention-based zone cutoffs — must
be captioned illustrative) and `fig5` (confounded experiment — must stay
non-evidentiary).
