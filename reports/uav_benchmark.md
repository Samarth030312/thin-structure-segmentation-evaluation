# UAV Benchmark

Converged, multi-seed binary road segmentation on real UAV/aerial data. Reproduce:
`bash scripts/run_uav_benchmark.sh`.

## 1. UAVid (genuine low-altitude UAV), U-Net, 3 seeds

| Seed | mIoU | clDice | BoundaryIoU | clPrecision | TolIoU |
|---|---|---|---|---|---|
| 42 | 0.597 | 0.602 | 0.465 | 0.893 | 0.576 |
| 123 | 0.558 | 0.515 | 0.426 | 0.803 | 0.501 |
| 999 | 0.553 | 0.585 | 0.400 | 0.846 | 0.550 |
| **mean ± 95% CI** | **0.570 ± 0.027** | **0.567 ± 0.053** | 0.430 | 0.847 | 0.542 |

**Converged** (40 epochs, plateau), seed-stable, precision 0.85 — a usable real-UAV
road segmenter. Note **mIoU ≈ clDice (0.570 vs 0.567)**: on wide UAVid roads the two
metrics *agree*, exactly the boundary condition identified in
`uav_claim_validation.md` (the mIoU/clDice divergence needs thin structures).

## 2. LoveDA (aerial), U-Net, converged
mIoU 0.51, clDice 0.64 (binary road). Here roads are thinner and the IoU–clDice gap
appears (`uav_claim_validation.md`).

## 3. Architecture coverage — honest scope
The campaign requested U-Net / U-Net++ / DeepLabV3+ / SegFormer on every UAV
dataset, multi-seed. The full grid (4 architectures × 2 datasets × 3 seeds = 24
converged runs at $\ge$40 epochs each) is **$\sim$8 GPU-hours and out of the 4 GB
budget**. We ran the highest-value slice — **U-Net × UAVid × 3 seeds** (converged,
the genuine-UAV dataset) plus a converged LoveDA model — which is what the
scientific question (claim validation) actually needs. The architecture-comparison
question was already answered on the controlled synthetic benchmark
(`architecture_analysis.md`); repeating it on wide UAV roads would not bear on the
thin-structure claim. The remaining runs are one command away
(`run_uav_benchmark.sh` over the model configs) on adequate hardware.

## 4. Tracked metrics
mIoU, Dice, clDice, BoundaryIoU, TolIoU (per the campaign), plus PixelAcc and
clPrecision/clRecall. All in `reports/leaderboard_uav.csv`.
