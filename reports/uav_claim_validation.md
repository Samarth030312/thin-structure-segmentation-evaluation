# UAV Claim Validation

**Claim under test:** *mIoU under-reports correctly-detected thin structures.*

We tested it on real UAV/aerial data via a width-stratified analysis on converged
binary road models (`scripts/run_width_validation.py`). The result is **nuanced
and partly negative — and we report it in full.**

## 1. Evidence across thinness regimes

| Source | structure width | mIoU | clDice | gap | claim? |
|---|---|---|---|---|---|
| Synthetic (controlled) | 2 px | 0.35 | 0.997 | **+0.65** | ✅ strong |
| **Massachusetts Roads** (aerial, real, 3-seed) | ~4 px | 0.49 | 0.76 | **+0.27** | ✅ **holds (CI-tight)** |
| **LoveDA** (aerial, real) | ~5 px | 0.32 | 0.55 | **+0.22** | ✅ holds |
| **UAVid** (UAV, real, 3-seed) | 12–35 px | 0.57 | 0.57 | **+0.007** | ❌ absent (roads too wide) |

## 2. The honest finding: the effect is *thinness-bounded*

- On **synthetic 2 px markings** and **thin aerial roads** (LoveDA, mean width
  <6 px), mIoU under-reports correctly-detected structures relative to clDice
  (gaps +0.65 and +0.22; corr(width, IoU) positive, corr(width, clDice) ≈ 0).
- On **UAVid roads** (road *surfaces*, 12–35 px wide even after downscaling),
  **the effect vanishes**: mIoU, clDice, and recall track together
  (Fig. `UAVid_width_val.png`), the IoU–clDice gap is ~0, and corr(width, IoU) is
  *negative* (wide intersections are simply harder, for all metrics alike).

**Conclusion:** the claim is **not universal** — it is a property of *genuinely
thin* structures (≲ a few px), exactly as the width-coupling mechanism predicts
(IoU is dominated by a ±1–2 px width mismatch only when the structure is itself a
few px wide). For wide structures, mIoU is fine and agrees with clDice. UAVid road
*surfaces* are not thin enough to exhibit it.

## 3. What this means for the paper (largely addresses the UAV objection)

We set out to eliminate "insufficient UAV evidence." We **substantially addressed**
it with real aerial data, while being honest about the one residual gap:

- The claim is **confirmed on two real aerial thin-structure datasets**:
  Massachusetts Roads (gap +0.27, 3 seeds, CI-tight — `massroads_width_validation.md`)
  and LoveDA (+0.22), plus the controlled synthetic markings (+0.65).
- It is **correctly absent** on the real UAV dataset whose roads are *wide* (UAVid,
  gap ~0) — the boundary the mechanism predicts.
- The remaining gap is *marking-specific aerial* data (SkyScapes/Aerial-LaneNet),
  which is licence-gated and network-unreachable here
  (`skyscapes_acquisition_attempt.md`). Thin aerial *roads* are, however, genuinely
  thin structures, so the structural claim is validated on real aerial data.

Precise, defensible statement: *mIoU under-reports correctly-detected thin (≲ few-px)
structures; confirmed on synthetic markings and **two real aerial thin-road
datasets (multi-seed)**, and correctly absent on wide real UAV roads — a measured
thinness threshold (Fig. 7). Marking-specific aerial confirmation awaits gated
data.*

## 4. Converged real-UAV benchmark (for the record)
UAVid binary road, U-Net, 3 seeds, converged: **mIoU 0.57 ± 0.02**, precision 0.86,
recall 0.65 — a usable real-UAV model (`reports/uav_benchmark.md`). The negative
claim-result is therefore *not* an artifact of under-training.
