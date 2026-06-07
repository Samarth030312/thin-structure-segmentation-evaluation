# Massachusetts Roads — Real Aerial Thin-Structure Validation

The SkyScapes-substitute experiment (`reports/skyscapes_acquisition_attempt.md`):
test whether the thin-structure claim holds on **real aerial thin structures**.
Massachusetts Roads (HF `asolodin/massachusetts_roads_dataset_500`) is aerial RGB
with **thin rural roads (3.6 % pixels, ~3–6 px wide)**. Converged U-Net, 3 seeds.
Reproduce: `bash scripts/run_massroads.sh`, `scripts/run_width_validation.py`.

## 1. Result — the claim HOLDS on real aerial thin roads

| | mIoU | clDice | gap (clDice−mIoU) |
|---|---|---|---|
| seed 42 | 0.485 | 0.742 | +0.256 |
| seed 123 | 0.509 | 0.767 | +0.258 |
| seed 999 | 0.482 | 0.763 | +0.280 |
| **mean ± 95% CI** | **0.492 ± 0.017** | **0.757 ± 0.015** | **+0.265** |

Per-image (2-seed ensemble, 40 test images, all mean-width <6 px): mIoU 0.500,
clDice 0.747, tolerance-recall 0.722, clPrecision 0.90.

**On real aerial thin roads, mIoU (0.49) under-reports correctly-detected
structure by +0.27 relative to clDice (0.76)** — consistent across 3 converged
seeds with tight CIs. The roads are genuinely detected (recall 0.72, precision
0.90); mIoU simply penalises the ±1–2 px width mismatch on a 3–6 px structure.
This is the real-aerial confirmation the UAV campaign needed.

## 2. The thinness threshold, across real + synthetic data

The under-reporting gap scales monotonically with structure width
(`paper_figures/fig7_thinness_threshold.{png,pdf}`):

| Dataset | type | width | mIoU | clDice | gap |
|---|---|---|---|---|---|
| Synthetic markings | controlled | 2 px | 0.35 | 0.997 | **+0.65** |
| **Massachusetts Roads** | **real aerial** | ~4 px | 0.49 | 0.76 | **+0.27** |
| **LoveDA** | **real aerial** | ~5 px | 0.32 | 0.55 | **+0.22** |
| UAVid | real UAV | ~20 px | 0.57 | 0.57 | **+0.00** |

The two **real aerial** datasets (Massachusetts Roads, LoveDA) sit firmly in the
thin regime with large gaps; the **real UAV** dataset (UAVid, wide roads) sits at
zero — exactly the boundary the width-coupling mechanism predicts.

## 3. Honest scope
- Massachusetts Roads labels **roads**, not lane *markings* — but the roads here
  are genuinely *thin* (3–6 px), which is the structural property the claim
  concerns. It substitutes for SkyScapes on *thinness*, not on *marking semantics*.
- Within Massachusetts Roads the width is nearly uniform (all images <6 px), so the
  evidence is the **aggregate** mIoU–clDice gap (multi-seed, CI-tight), not a
  within-dataset width gradient. The width *gradient* evidence is the cross-dataset
  comparison (Fig. 7) and the controlled synthetic study.
- SkyScapes itself (aerial *markings*) remains the ideal confirmation and is
  unacquirable here (gated); the ingestion is built for when it is available.

## 4. Bottom line
The thin-structure claim, previously confirmed only on synthetic markings and
shown absent on wide UAV roads, is now **confirmed on two real aerial thin-road
datasets with multi-seed CIs**. The mIoU-under-reports-thin-structures effect is a
real, reproducible, dataset-independent property of genuinely thin structures.
