# Reproducibility Audit (Phase 4)

Scenario: a professor runs `git clone`, `pip install -e .`, then the README's
"reproduce the central result" commands on a clean machine.

## CRITICAL — missing core dependency (CONFIRMED)
- The central metric `cl_dice` imports scikit-image:
  `src/uavroadmark/metrics/thin_structure.py:31` → `from skimage.morphology import skeletonize`.
- The controlled study and width analysis import scipy:
  `scripts/run_controlled_robustness.py`, `scripts/run_width_validation.py` →
  `from scipy.ndimage import ...`, `scipy.optimize.curve_fit`.
- **Neither `scikit-image` nor `scipy` is listed in `requirements.txt` or
  `pyproject.toml` `dependencies`** (verified by grep — both absent).
- `scipy` is likely pulled transitively by `scikit-learn` (a listed dep). **`scikit-image`
  is NOT a hard dependency of `albumentations>=1.3`** and is **not guaranteed to
  install.**

**Consequence:** on a clean environment, `import uavroadmark.metrics.thin_structure`
(and therefore `scripts/run_controlled_robustness.py`, the README's first reproduce
command) **raises `ModuleNotFoundError: skimage`.** The headline reproduce path
**fails**. This is a genuine reproducibility blocker.

**Exact fix (not performed):** add `scikit-image>=0.20` and `scipy>=1.9` to
`requirements.txt` and `pyproject.toml` `dependencies`.

## Other checks

| Check | Result | Evidence |
|---|---|---|
| `pyproject` installable / entry points | OK | `[project.scripts] uavrm-train/eval/validate` present |
| README scripts exist | OK | `run_controlled_robustness.py`, `fit_width_law.py`, `make_law_figures.py`, `run_width_validation.py`, `prepare_uavid.py`, `run_uav_benchmark.sh` all present |
| README configs exist | OK | `configs/experiment/uav_uavid.yaml` present |
| Fig-source data exists | OK | `reports/visualizations/width_study/width_study.json`, `reports/leaderboard.csv`, `leaderboard_performance.csv` present |
| Tests pass | OK **in this env** | 62 passed — but **the env already has skimage/scipy**; a clean env would fail to import (see CRITICAL) |
| `PYTHONPATH=src` required | documented | README uses `PYTHONPATH=src` / `pip install -e .` |
| Real-data checkpoints on clone | **absent (by design)** | README real-data example cites `outputs/uav_uavid_s42/best.pth` — git-ignored, not in clone; README labels this "optional, needs datasets + GPU" (acceptable, but the paths will not exist) |
| Hardware/machine assumptions | partial | timings (`table4`) are machine-specific; `δ`-dependent thresholds; 4 GB-GPU subsampling baked into some configs |

## Hidden assumptions discovered
- The metric suite needs **skimage** (undeclared) — the CRITICAL item above.
- `make_law_figures.py` imports `run_controlled_robustness` via `sys.path`/importlib
  (`scripts/make_law_figures.py:10-15`) — runs only from repo root with `PYTHONPATH=src`.
- The real-data path assumes the user separately downloads UAVid/LoveDA/MassRoads and
  produces checkpoints; these are **not** reproducible from the clone alone.

## Verdict
**The law itself is reproducible from the clone on CPU — *after* the missing
`scikit-image`/`scipy` dependencies are added.** As shipped, a clean `pip install`
**fails to import the core metric**. This is a **must-fix before release**. Everything
else (scripts, configs, fig-source data, tests-in-env) checks out.
