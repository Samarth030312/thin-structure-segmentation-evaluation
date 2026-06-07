
# When mIoU Lies — Thin-Structure Segmentation Evaluation

**An evaluation study of when and why mean-IoU misleads for thin road markings and
lane lines — with a geometric explanation and a reproducible benchmark.**

![tests](https://img.shields.io/badge/tests-62%20passing-brightgreen)
![python](https://img.shields.io/badge/python-3.9%2B-blue)
![license](https://img.shields.io/badge/license-MIT-green)

> **This is a measurement/evaluation study — not a new segmentation model.** No
> state-of-the-art accuracy is claimed.

---

## The result in one box

mIoU systematically **under-reports thin structures that a model has correctly
detected**. The disagreement between mIoU and a centerline metric (clDice) follows a
simple geometric relationship with structure width `w`:

```
Gap(w) = clDice − mIoU ≈ 2δ / (w + 2δ)      (δ ≈ boundary-localisation error, ~1 px)
```

Thin markings (2–8 px) live where mIoU is most misleading; wide structures do not.
**Takeaway: for thin structures, report clDice / tolerance-IoU alongside mIoU.**

## Why it matters

Perception teams select and gate models on metrics. If mIoU under-credits
thin-structure detectors, model selection is biased against the safety-relevant thin
things (lane lines, markings). This repo quantifies that bias and gives a width-based
rule for when mIoU can be trusted.

## Evidence at a glance (all numbers traceable)

**Controlled experiment** — synthetic structures, width 1→30 px, fixed 1-px boundary
error (`scripts/run_controlled_robustness.py`). Fitting candidate forms
(`scripts/fit_width_law.py`): the inverse-width family fits (power R²=0.989, rational
0.986, inverse 0.977); linear (0.626), exponential (0.892), logarithmic (0.937) are
rejected. Fitted δ ≈ 0.67 px.

**Measured on real datasets** (`scripts/run_width_validation.py`):

| Dataset | Type | Mean width | mIoU | clDice | Gap |
|---|---|---|---|---|---|
| Synthetic | controlled markings | 2 px | 0.351 | 0.997 | **0.65** |
| Massachusetts Roads | real aerial thin roads | 4.31 px | 0.509 | 0.763 | **0.25** |
| LoveDA | real aerial thin roads | 4.90 px | 0.478 | 0.698 | **0.22** |
| UAVid | real UAV wide roads | 16.24 px | 0.528 | 0.543 | **0.02** |

Thin → large gap; wide (UAVid) → ≈ 0, exactly as the relationship predicts. Key
figure: `paper_figures/figA_width_gap_law.png`.

**Reliability rule:** below ~5 px, mIoU under-reports a detected structure by >20 %;
above ~25 px the disagreement is <5 % (`reports/failure_thresholds.md`). Thresholds
scale with δ.

## Reproduce in minutes (CPU, no download)

```bash
pip install -e .
python scripts/run_controlled_robustness.py   # geometry-only width sweep
python scripts/fit_width_law.py               # fit candidate forms
python scripts/make_law_figures.py            # figures
python -m pytest                              # 62 tests
```

## What's included

```
src/uavroadmark/   package: metrics (clDice, Boundary-IoU, TolIoU, width-IoU),
                   losses, models (U-Net, U-Net++, DeepLabV3+, PSPNet, SegFormer),
                   data, engine, cli
scripts/           controlled study, law fit, figures, real-data validation, ingestion
configs/           YAML composition; custom_dataset.yaml template
paper_package/     final_ieee_paper.{md,tex,pdf}
paper_figures/  paper_tables/  reports/   results, analysis, validation
tests/             62 tests       deploy/  ONNX/TorchScript export
```

## What is NOT claimed

- **No aerial road-*marking* result** — the ideal dataset (SkyScapes) is licence-gated
  and was not obtained; validation uses real thin *roads* + synthetic markings
  (`reports/skyscapes_acquisition_attempt.md`).
- The relationship is, at core, IoU's definition made explicit — an evaluation
  contribution, not a new method (`reports/law_assessment.md`).
- δ is model-dependent; the 5 px / 25 px thresholds are illustrative, not universal.
- A proposed connectivity loss (CoRe) did **not** beat the baseline — reported as a
  null result (`paper_tables/table7_multiseed.md`).

## Datasets & licenses

Code is **MIT**. Datasets keep their own terms — LoveDA (CC-BY-NC), UAVid
(research-only), Massachusetts Roads, RLMD. This repo **redistributes no data or
checkpoints**; ingestion scripts fetch from public sources. See `DATA_LICENSES.md`.

## Paper & citation

`paper_package/final_ieee_paper.pdf` — *"When mIoU Lies: Topology-Aware Evaluation of
Thin Road-Marking Segmentation."*

## License

MIT (`LICENSE`). Datasets: `DATA_LICENSES.md`.
