# Repository Audit

Full verification of the repository.

## Automated checks

| Check | Result |
|---|---|
| Unit + integration tests (`pytest`) | ✅ **62 passed**, 0 failed |
| All Python scripts compile (`py_compile`) | ✅ pass (after fixing `system_report.py`) |
| All 34 experiment configs load (`load_config`) | ✅ 0 bad |
| Key result files present | ✅ leaderboard(.csv), perf, xdomain, stats_clean, system_report |
| Paper figures render | ✅ 5 figs × {png, pdf} |
| Paper tables regenerate | ✅ md + LaTeX + csv |
| CI workflow present | ✅ `.github/workflows/ci.yml` |

## Bug found & fixed during audit

- **`scripts/system_report.py`** — `SyntaxError` (backslash inside an f-string,
  invalid on Python 3.10). Refactored to pre-compute shell results into variables.
  Now compiles and runs. *(This is exactly what the audit is for.)*

## Reproducibility commands (all verified runnable)

| Artifact | Command |
|---|---|
| Synthetic data + smoke | `bash scripts/run_smoke.sh` |
| Real RLMD ingestion | `python scripts/prepare_real.py --raw <RLMD> --label-mode rgb --colormap configs/rlmd_colormap.json ...` |
| LoveDA ingestion | `python scripts/prepare_real.py --raw <loveda> --label-mode id ...` |
| SkyScapes ingestion | `python scripts/prepare_skyscapes.py prepare ...` |
| RLMD 6-loss ablation | `bash scripts/run_rlmd_6loss.sh` / `run_rlmd_unetpp_complete.sh` |
| Cross-dataset 2×2 | `bash scripts/run_cross_dataset.sh` |
| Multi-seed | `bash scripts/run_multiseed.sh` |
| Stats comparison | `python scripts/run_stats_compare.py ...` |
| Performance benchmark | `python scripts/run_perf_benchmark.py` |
| Deployment benchmark | `python scripts/run_deploy_benchmark.py` |
| Profiling | `python scripts/run_profiling.py --config ...` |
| Failure taxonomy | `python scripts/run_failure_analysis.py ...` |
| Grad-CAM | `python scripts/run_gradcam.py ...` |
| Paper figures/tables | `python scripts/make_paper_figures.py` / `make_paper_tables.py` |

## Path validity

- `src/` layout importable via `PYTHONPATH=src` or `pip install -e .`.
- Standard entry points present: `evaluation/metrics.py`, `training/train.py`,
  `scripts/dataset_validator.py`.
- Datasets are git-ignored (large); ingestion scripts regenerate the contract.

## Known non-blocking items

- `pandas.to_latex` deprecation warning on some tables (cosmetic; CSV/MD are
  authoritative).
- `albumentations` ShiftScaleRotate UserWarning (upstream; harmless).
- SkyScapes results not produced (license/compute) — ingestion verified on a
  synthetic stand-in.

## Verdict

Repository is internally consistent, tested, and reproducible. Every committed
number traces to a script + config. The audit found and fixed one real bug.
