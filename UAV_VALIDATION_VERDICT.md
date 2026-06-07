# UAV Validation Verdict (Positioning & Readiness)

## 1. Paper positioning (choose by evidence)

| Option | Verdict |
|---|---|
| **A. "When mIoU Lies"** | ✅ **CHOSEN.** Broad enough to honestly hold: the paper is about mIoU's failure mode on *thin* structures, with a now-measured thinness threshold (synthetic 2 px → thin aerial roads → wide UAV roads). Survives all evidence, including the UAVid negative. |
| B. "Topology-Aware Evaluation of UAV Road-**Marking** Segmentation" | ❌ **reject — overclaim.** No UAV road-marking data exists/was acquired; the claim does not even hold on UAV road *surfaces*. The title would assert evidence we do not have. |
| C. "Thin Structure Evaluation Across UAV Datasets" | ❌ **reject — misleading.** Of the two UAV/aerial datasets, the genuine-UAV one (UAVid) *contradicts* the effect (roads too wide). "Across UAV datasets" implies confirmation we did not obtain. |

**Recommended title:** *"When mIoU Lies: A Thinness Threshold for Topology-Aware
Evaluation of Thin-Structure Segmentation."* The UAV campaign becomes the section
that *bounds* the claim (the thinness threshold), not one that proves a UAV result.

**Justification (evidence):** the effect magnitude scales monotonically with
thinness — synthetic 2 px gap +0.65 (CI-tight, converged) → thin aerial LoveDA
roads gap +0.22 → wide UAVid roads gap +0.007 (≈0). The mechanism (IoU couples
detection with ±1-2 px width matching) *predicts* this threshold; measuring it is a
sharper contribution than a blanket "mIoU is bad."

## 2. Readiness, recalculated (no inflation)

*Updated after acquiring Massachusetts Roads (real aerial, thin) — the
SkyScapes substitute — which CONFIRMS the claim on real aerial thin structures.*

| Venue | Pre-campaign | After UAVid (negative) | After MassRoads (real aerial confirm) | Why |
|---|---|---|---|---|
| GitHub | 90% | 92% | **93%** | 3 real UAV/aerial datasets, ingestion, converged multi-seed models |
| Resume | 85% | 88% | **90%** | genuine UAV + real-aerial confirmation + an honest negative result |
| Professor review | 70% | 75% | **80%** | thinness-threshold confirmed on real aerial data (multi-seed CI) |
| Workshop | 50% | 62% | **72%** | converged models + real-aerial-confirmed, mechanism-backed claim |
| IEEE ITSC | 30% | 42% | **55%** | real aerial confirmation present; still aerial *roads* not *markings* |
| WACV | 20% | 25% | **30%** | still novelty-light for a vision main track |
| T-ITS | 15% | 22% | **30%** | needs the full multi-dataset + gated-marking program |

**Overall publishability: 67 → ~75 / 100.** The Massachusetts Roads result moved
it up meaningfully (real aerial thin-structure confirmation, multi-seed). **Still
not 80**, honestly:

### Why ~75, not 80
1. **Confirmed on real aerial thin *roads*, not aerial *markings*.** The claim now
   holds on two real aerial datasets (Massachusetts Roads gap +0.27 multi-seed;
   LoveDA +0.22) and the UAV boundary (UAVid ~0) — strong. But a reviewer wanting
   *road-marking* aerial evidence still wants SkyScapes specifically.
2. **SkyScapes remains gated/unreachable** (DLR portal HTTP 000;
   `reports/skyscapes_acquisition_attempt.md`). It is the only thing left between
   ~75 and ~80, and it is a licence/network barrier, not a science barrier.
3. Novelty is still moderate (existing metrics; the **thinness-threshold law**
   across real+synthetic data, Fig. 7, is now the freshest and most defensible piece).

### What the campaign achieved
- **3 real UAV/aerial datasets** acquired, validated, converged (UAVid, LoveDA,
  Massachusetts Roads) — rebutting "under-trained" on genuine imagery.
- **The claim CONFIRMED on real aerial thin structures**: Massachusetts Roads
  (mIoU 0.49 vs clDice 0.76, gap +0.27, 3 seeds, CI-tight) and LoveDA (+0.22).
- A **measured thinness threshold** across real + synthetic data (Fig. 7): gap
  0.65 (2 px) → 0.27/0.22 (real aerial 4–5 px) → 0.00 (real UAV 20 px).
- An **honest negative** (UAVid wide roads, gap ~0) that *bounds* the claim and
  matches the mechanism — increasing, not decreasing, credibility.

### Exact path to 80 (now narrow and evidence-grounded)
Acquire **SkyScapes** (aerial road *markings* specifically; ingestion built) → run
the same width validation. The thinness law (Fig. 7) predicts the claim holds; that
would supply the *marking*-specific aerial evidence and clear ~78–80. Blocked only
by a DLR licence + an unreachable portal, not by science.

## Bottom line
The campaign acquired real UAV/aerial data and **confirmed the central claim on
real aerial thin structures** (multi-seed, CI) while honestly bounding it (no
effect on wide UAV roads). Publishability rose from 67 to **~75**. It stopped short
of 80 only because the *marking*-specific aerial set (SkyScapes) is licence-gated
and network-unreachable here — a documented access barrier, not a fabrication I am
willing to make.
