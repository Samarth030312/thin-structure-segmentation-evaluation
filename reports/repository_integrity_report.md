# Repository Integrity Report

Reconstruction following `reports/final_release_audit.md`. Goal: restore credibility,
not impressiveness. Where a claim could not be supported, it was removed or relabelled.
The four critical audit findings (phantom AU-Drone; README contradicts paper;
final_report contradicts paper; Figure A hand-assigned widths) are resolved below.

## 1. What was fixed

### 1.1 Phantom "AU-Drone" dataset purged (was 22 files)
"AU-Drone" was an aspirational, never-acquired target dataset presented in places as
real. Actions:
- **Deleted** the five phantom experiment configs (`*_audrone.yaml`) — they referenced
  non-existent data and produced no results.
- **Renamed** `configs/dataset/audrone.yaml` → `configs/dataset/custom_dataset.yaml`,
  rewritten as an honest "bring-your-own-dataset" template pointing to the real dataset
  configs (`uavid_bin`, `massroads_bin`, `loveda_bin`).
- **Rewrote** code docstrings that named it (`src/uavroadmark/data/synthetic.py`,
  `evaluation/evaluate.py`, `training/train.py`) to reference the real datasets.
- **Scrubbed** all prose references in docs and historical reports; added
  **"Historical / superseded"** banners to the initial-phase reports.
- Also removed the unsupported **"Indian"** geographic framing throughout (the project
  has no Indian data).
- **Remaining mentions are intentional and meta**: only this report and
  `reports/final_release_audit.md` (which document the problem) still contain the
  string "AU-Drone".

### 1.2 Narrative unified to the paper (source of truth: "When mIoU Lies")
- `README.md` **rewritten** around the width-coupling law, the real datasets, honest
  scope/limitations, and correct commands; the discredited "Indian UAV / AU-Drone /
  model-zoo" framing and the false "nothing is hard-coded" claim are gone.
- `reports/final_report.md` **rewritten** to match the paper (was "Indian Road-Marking
  Detection from UAV Imagery").
- Docs (`training_guide`, `evaluation_guide`, `architecture`) repointed to real configs.
- README, `final_report`, paper, and monograph now describe the **same** project.

### 1.3 Figure A regenerated from MEASURED values (was hand-assigned)
- `scripts/run_width_validation.py` now emits `measured_mean_width_px`,
  `measured_median_width_px`, and `measured_mean_gap` per dataset.
- Re-ran validation on UAVid, Massachusetts Roads, LoveDA → JSONs with measured stats.
- `scripts/make_law_figures.py` now **loads** the real-data points from those JSONs
  (`load_real_points()`); the hardcoded `REAL = [...]` literals are gone. `figA` and
  `fig7` are regenerated from measured data. Measured vs old-hardcoded:

| Dataset | old (hardcoded) | measured (now) |
|---|---|---|
| MassRoads | 4.0 px / +0.265 | **4.31 px / +0.254** |
| LoveDA | 5.0 px / +0.220 | **4.90 px / +0.220** |
| UAVid | 20.0 px / +0.007 | **16.24 px / +0.015** |
| Synthetic | 2.0 px / +0.65 | 2.0 px (GT) / **+0.646** |

The qualitative conclusion is unchanged (three of four land on the curve; UAVid is in
the safe zone), but the figure is now **reproducible from data**, not eyeballed. The
theory table in `reports/width_coupling_theory.md` and the monograph were updated to
the measured values.

### 1.4 Other fixes
- Added `DATA_LICENSES.md` (LoveDA CC-BY-NC, UAVid research-only, etc.; no
  redistribution).
- Laundered the literal vendor name in `reports/github_release_audit.md`.
- 62 tests still pass after config deletion and docstring edits.

## 2. Figure audit (source data · script · assumptions)

| Figure | Source data | Script | Assumptions / notes |
|---|---|---|---|
| `figA_width_gap_law` | `reports/controlled/robustness_sweeps.json` + `law_fit.json` + validation JSONs | `make_law_figures.py:fig_A` | real points **measured**; synthetic at GT width 2 px (labelled outlier) |
| `figB_relative_error` | controlled sweep JSON | `make_law_figures.py:fig_B` | derived from controlled data only |
| `figC_disagreement_heatmap` | recomputed from geometry | `make_law_figures.py:fig_C` | width × δ grid; pure geometry |
| `figD_failure_zones` | `law_fit.json` (δ) | `make_law_figures.py:fig_D` | zone thresholds are illustrative (scale with δ) |
| `fig7_thinness_threshold` | validation JSONs + `law_fit.json` | `make_law_figures.py:fig_thinness` | real points **measured** (regenerated; previously a one-off) |
| `fig1b_width_multiseed` | `width_study_multiseed.json` | `run_width_study_multiseed.py` | converged synthetic, 3 seeds, bootstrap CIs |
| `fig6_convergence` | `outputs/rlmdbin_converge/history.json` | `plot_learning_curve.py` | real training history |
| `fig5_cross_dataset` | `paper_figures` / cross-dataset run | `run_cross_dataset.sh` | **confounded** (disjoint taxonomies, tiny test set) — kept, labelled exploratory |
| `fig1–fig4` (`width_study`, `rlmd_loss_ablation`, `perf_pareto`, `stats_ci`) | leaderboard / run outputs | `make_paper_figures.py` | initial-phase benchmark figures; real (synthetic/RLMD) numbers |

**No figure now depends on a hand-assigned value.** `figD`'s zone boundaries are
explicitly *illustrative* (they scale with the model-dependent δ). `fig5` is the
confounded cross-dataset probe and is clearly labelled exploratory, not evidence for the
law.

## 3. Evidence supporting every major claim

| Claim | Evidence | Status |
|---|---|---|
| `Gap = 2δ/(w+2δ)` (the law) | geometric derivation (`first_principles_width_analysis.md`) + controlled fit R²=0.98 (`fit_width_law.py`) | supported |
| Real datasets obey the law | **measured** widths/gaps on the curve, 3/4 within ±0.06 (`figA`, validation JSONs) | supported (now reproducible) |
| Failure thresholds | derived from the law; δ-dependent and labelled illustrative | supported (with caveat) |
| mIoU mis-ranks under imbalance | RLMD three-test analysis (`metric_sensitivity_analysis.md`) | supported, scoped |
| CoRe loss helps | multi-seed: Δ≈−0.001, n.s. | **removed** (null result) |
| UAV / aerial-marking validation | none — SkyScapes unreachable | **removed / future work** |
| "Indian UAV road-marking benchmark" | no such data | **removed** (framing) |
| "AU-Drone headline results" | no such dataset | **removed** (phantom) |

## 4. What remains uncertain (honest)

- **Controlled experiment is partly self-consistent by construction** (inject δ, recover
  `w/(w+2δ)`); the non-circular evidence is the real datasets, now measured but still
  only four, at three viewpoints. (Documented; `final_release_audit.md` M1.)
- **δ is model-dependent**; the failure-threshold widths (5/25 px) assume δ≈1 px.
- **No aerial road *markings*** (SkyScapes gated); the marking claim rests on synthetic +
  ground-view RLMD + real thin *roads*.
- **Novelty is bounded** — the law is IoU's definition made explicit.
- **`reports/final_release_audit.md` and this report retain "AU-Drone"/"Claude"** by
  necessity (they document the cleanup); exclude them from a public release if a
  zero-occurrence grep is required.

## 5. What claims were removed (not weakened — removed)
- The proposed CoRe loss as a contribution (now a null result).
- Any "headline results on a real (AU-Drone) dataset."
- The "Indian UAV road-marking" domain framing.
- The "nothing is hard-coded" README claim (it was false for Figure A).
- Hand-assigned figure widths (replaced by measured values).
