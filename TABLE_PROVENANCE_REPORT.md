# Table Provenance Report (Phase 3)

Each table in `paper_tables/` traced: table → source report → script → raw data, with
numeric verification.

| Table | Content | Source report | Script | Raw data | Numbers verified? |
|---|---|---|---|---|---|
| `table2_rlmd_loss_ablation` | RLMD 6-loss (mIoU/PixelAcc/clDice/clRecall/TolIoU) | `reports/metric_sensitivity_analysis.md` | `scripts/analyze_metric_sensitivity.py` | `outputs/rlmd_unetpp_*/eval_test.json`, `reports/leaderboard.csv` | **Yes** — e.g. ce_dice clDice 0.3728, tversky mIoU 0.144 / PixelAcc 0.0091 match the report. |
| `table3_arch_sweep` | architecture comparison (synthetic) | `reports/architecture_analysis.md` (now banner-superseded) | `scripts/run_arch_sweep.sh` | `reports/leaderboard.csv` | **Partly** — synthetic-only numbers; the source report is flagged historical. |
| `table4_performance` | latency/throughput/params | `reports/model_comparison.md` (banner-superseded) | profiling scripts | `reports/leaderboard_performance.csv` | **NOT FULLY VERIFIED** — hardware-dependent timings; raw profiling run not re-executed here. |
| `table6_cross_dataset` | RLMD↔LoveDA transfer | `reports/cross_dataset_generalization.md` | `scripts/run_cross_dataset.sh` | cross-dataset run | **Confounded** — disjoint taxonomies, ~41 test images; numbers real but **non-evidentiary**. |
| `table7_multiseed` | CE+Dice vs CoRe, 3 seeds, CIs | `reports/multiseed_width_study.md` / loss study | `scripts/run_rigor_experiments.sh` + `metrics/stats.py` | per-seed eval JSONs | **PARTIAL — see defect below.** |

## CORRECTED — `table7_multiseed` (prior "defect" was an incomplete read)
The headline negative result (CoRe ties CE+Dice) is stated as *"Δ ≈ −0.001, 95% CI
[−0.18, 0.18]."* The earlier audit used `head -6` and saw only the per-loss rows
(`nan` in the paired columns, which is correct — paired stats are not per-loss).
**Line 7 of the original CSV/MD is the `_paired_ce_dice_minus_core_clDice` row** with
`mean_diff=-0.0011`, `ci95=[-0.1823, 0.1802]`, `n_pairs=3`, `ce_dice_better_all_seeds=0`
— which **matches the prose exactly**. The CI **is supported by the table**.

**Action taken:** the table was reformatted (`table7_multiseed.{md,tex}`) into a
per-loss block plus an explicit paired-comparison block so the CI is unambiguous and no
reader misinterprets the per-loss `nan` cells.

## Verification notes
- `table2` is the most-cited and **checks out** against its report and raw eval JSONs.
- `table4` timings are **machine-specific** and were not re-measured in this audit →
  **NOT VERIFIED** (state hardware in the caption before release).
- `table6` is real but confounded; must not be used as evidence for the law.

## Verdict
One table (`table2`) is fully verified. `table7` has a **NaN paired-CI** that makes its
printed interval unverifiable (qualitative claim still holds via the means). `table4`
is hardware-dependent and unverified. `table6` is confounded. Tables 3/4/6 trace to
**historical, banner-superseded** reports.
