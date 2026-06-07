# When mIoU Lies — Thin-Structure Segmentation Evaluation

**A reproducible study and framework showing — and explaining with a geometric
law — when and why mean-IoU is a misleading metric for thin road markings and
lane lines.**

[![tests](https://img.shields.io/badge/tests-62%20passing-brightgreen)]()
[![python](https://img.shields.io/badge/python-3.9%2B-blue)]()
[![license](https://img.shields.io/badge/license-MIT-green)]()

---

## TL;DR

Mean Intersection-over-Union (mIoU) is the default metric for road-marking
segmentation. We show it **systematically under-reports thin structures that a
model has in fact correctly detected**, and we derive the exact functional form
of that error:

> **Gap(w) = clDice − mIoU ≈ 2δ / (w + 2δ)**
>
> where `w` is the structure width in pixels and `δ` is the model's per-side
> boundary-localisation error (≈ 1 px).

The law is **derived from pixel geometry** (Part 7 of the monograph),
**confirmed in a controlled, model-free experiment** (inverse-width fit,
R² = 0.98; linear/exponential/log rejected), **validated on three real datasets**
(Massachusetts Roads, LoveDA, UAVid — they fall on the curve), and yields
**actionable thresholds**: mIoU is misleading below ~5 px (markings), reliable
above ~25 px (wide roads).

The repository also contains the supporting evaluation framework: a config-driven
training/evaluation pipeline, a thin-structure metric suite (clDice, Boundary-IoU,
tolerance-IoU, width-stratified IoU), dataset ingestion, and 62 passing tests.

**This is an *evaluation* study. We claim no new state-of-the-art model, and we
report a proposed loss (CoRe) that did *not* work as an honest null result.**

---

## Start here

| Audience | Read this |
|---|---|
| 2-minute overview | this README + `paper_figures/figA_width_gap_law.pdf` |
| The paper | [`paper_package/final_ieee_paper.pdf`](paper_package/final_ieee_paper.pdf) — *"When mIoU Lies"* |
| The full textbook (58 pp) | [`docs/UAV_Roadmark_Master_Monograph.pdf`](docs/UAV_Roadmark_Master_Monograph.pdf) |
| The law + derivation | [`reports/width_coupling_theory.md`](reports/width_coupling_theory.md), [`reports/first_principles_width_analysis.md`](reports/first_principles_width_analysis.md) |
| Failure thresholds | [`reports/failure_thresholds.md`](reports/failure_thresholds.md) |
| Is it a law or an artifact? | [`reports/law_assessment.md`](reports/law_assessment.md) |
| Honest limits & integrity | [`reports/repository_integrity_report.md`](reports/repository_integrity_report.md), [`FINAL_RESEARCH_VERDICT.md`](FINAL_RESEARCH_VERDICT.md) |

---

## Reproduce the central result (CPU, minutes, no download)

```bash
pip install -e .                              # or: pip install -r requirements.txt
PYTHONPATH=src python scripts/run_controlled_robustness.py   # geometry-only width sweep
PYTHONPATH=src python scripts/fit_width_law.py               # fit candidate forms (R^2/AIC)
PYTHONPATH=src python scripts/make_law_figures.py            # Figures A-D (300 DPI + PDF)
```

This reproduces the law from pure geometry — **no model, no dataset, no GPU** —
and writes `reports/controlled/*.json` and `paper_figures/figA-D`.

### Real-data validation (optional, needs the public datasets + a GPU)

```bash
# Ingest a real dataset (example: UAVid, genuine low-altitude UAV imagery)
PYTHONPATH=src python scripts/prepare_uavid.py --raw <parquet> --out datasets/uavid
# Train a converged binary-road model, then place it on the law curve
bash scripts/run_uav_benchmark.sh
PYTHONPATH=src python scripts/run_width_validation.py \
    --config configs/experiment/uav_uavid.yaml \
    --checkpoints outputs/uav_uavid_s42/best.pth ... --label UAVid
```

Datasets are **not** redistributed; ingestion scripts pull them from their public
sources (see **Data & licences** below).

---

## What's in the box

```
src/uavroadmark/      installable package (data, models, losses, metrics, engine, cli)
  metrics/            mIoU + thin-structure suite: clDice, Boundary-IoU, TolIoU, width-IoU
  losses/             CE, Dice, Focal, Tversky, soft-clDice, CoRe (null result)
  models/             U-Net, U-Net++, DeepLabV3+, PSPNet, SegFormer (smp-backed)
scripts/              the science: controlled study, law fit, figures, real-data validation
configs/              YAML composition (_base_ + CLI overrides); custom_dataset.yaml template
paper_package/        final_ieee_paper.{md,tex,pdf}  ("When mIoU Lies")
docs/                 UAV_Roadmark_Master_Monograph.{md,pdf}  (58-page textbook) + guides
reports/              the law theory, validation, robustness, attacks, audits
tests/                62 tests (metrics, losses, models, data, validator, config, e2e)
```

## Datasets used (all real, all public)

| Dataset | Role | Structure | Note |
|---|---|---|---|
| Synthetic (in-repo generator) | derive & control the law | markings 2–8 px | width is an independent variable |
| RLMD | real ground-view markings | 2–8 px | imbalance study + converged binary model |
| LoveDA | real aerial roads | <6 px | law confirmed (gap +0.22) |
| Massachusetts Roads | real aerial thin roads | 3–6 px | law confirmed (gap +0.27, 3 seeds) |
| UAVid | real low-altitude UAV roads | 12–35 px | wide → law correctly predicts ~0 gap |

> **Honest scope.** There is **no aerial road-*marking* result** here: the ideal
> dataset (SkyScapes) is licence-gated and was unreachable
> (`reports/skyscapes_acquisition_attempt.md`). The law is validated on synthetic
> markings and real thin *roads*; aerial-marking confirmation is future work.

## Key findings (all in `reports/`)

- **The width-coupling law** — derived, fit R²=0.98, real-data confirmed, survives
  10 adversarial attacks (`reviewer_attack_campaign.md`).
- **Failure thresholds** — FAILURE < 5 px, WARNING 5–25 px, SAFE > 25 px.
- **mIoU mis-ranks losses under extreme class imbalance** (`metric_sensitivity_analysis.md`).
- **Negative result:** the proposed CoRe loss ties the CE+Dice baseline across seeds.
- **Negative result:** on wide UAVid roads the effect is absent — and that confirms
  the law's safe-zone prediction.

## Limitations (read these)

- The law is, at core, IoU's definition made explicit; novelty is moderate
  (`reports/law_assessment.md`, `FINAL_RESEARCH_VERDICT.md`).
- `δ` is model-dependent; the *form* is universal, the *scale* is not.
- Real models on the 25-class task are compute-bounded (4 GB GPU); the law itself
  rests on controlled geometry and converged binary models, so it is unaffected.

## Data & licences

Code is **MIT** (`LICENSE`). The datasets retain their own licences — several are
**non-commercial / research-only** (LoveDA CC-BY-NC; UAVid research use;
Massachusetts Roads; RLMD). See [`DATA_LICENSES.md`](DATA_LICENSES.md). Respect each
dataset's terms; this repository redistributes none of them.

## Tests

```bash
PYTHONPATH=src python -m pytest      # 62 tests
```

## Citation

If you use this work, cite the paper (`paper_package/final_ieee_paper.pdf`,
*"When mIoU Lies: A Geometric Width-Coupling Law for Thin-Structure Segmentation
Metrics"*).

## License

MIT — see [`LICENSE`](LICENSE). Datasets: see [`DATA_LICENSES.md`](DATA_LICENSES.md).
