# Cross-Dataset Generalization

> **Executed** RLMD ↔ LoveDA 2×2 transfer on real data, plus a controlled
> within-domain width-shift study. Binary foreground task (RLMD: any marking;
> LoveDA: road, class 3) — the only common label space, since the two datasets'
> class taxonomies are disjoint. Reproduce: `bash scripts/run_cross_dataset.sh`.
> Figure: `paper_figures/fig5_cross_dataset.{png,pdf}`.

## 1. Setup and the honest caveat

| Dataset | Viewpoint | Foreground (binary) | Train/Test |
|---|---|---|---|
| RLMD | ground / dashcam | any road marking | 400 / 276 |
| LoveDA | aerial / nadir | road surface (class 3) | 136 / 41 |

**Caveat (stated up front):** this measures a *combined* shift — **viewpoint**
(ground↔aerial) **and semantics** (thin markings vs. road *surface*). It is an
*upper bound* on transfer difficulty, not a pure domain-shift measurement (no two
public datasets share both viewpoint and the marking taxonomy — see
`dataset_survey.md`). We report it as such.

## 2. Results — 2×2 transfer (U-Net R34, binary)

Rows = train domain, columns = test domain. (in-domain = diagonal.)

| | → RLMD | → LoveDA |
|---|---|---|
| **train RLMD** | mIoU **0.517**, clDice **0.634** | mIoU 0.0001, clDice 0.463 |
| **train LoveDA** | mIoU 0.077, clDice 0.131 | mIoU **0.508**, clDice **0.667** |

(clDice shown in the figure heatmap.)

## 3. Findings (evidence-based)

**F1 — In-domain works; cross-domain collapses.** Diagonal clDice 0.63–0.67;
off-diagonal 0.13–0.46. The combined viewpoint+semantic gap is severe, as
expected — a ground-view marking detector and an aerial road detector do not
share low-level statistics. This quantifies *how hard* marking perception transfer
is across capture conditions, a real concern for deploying one model fleet-wide.

**F2 — Transfer is asymmetric.** RLMD→LoveDA (clDice 0.463) ≫ LoveDA→RLMD (0.131).
The marking model's thin-edge detectors partially fire on aerial road *edges*
(roads have linear boundaries), whereas the road-*surface* model has no notion of
thin markings. Markings ⊂ road-structure, so the marking→road direction degrades
more gracefully.

**F3 — mIoU under-reports even cross-domain.** RLMD→LoveDA gives **mIoU 0.0001**
(reads as total failure) but **clDice 0.463** (real partial structure transfer).
The thin-structure metric again reveals signal that mIoU hides — the project's
thesis holds in the cross-dataset regime too.

## 4. Controlled within-domain generalization (synthetic width shift)

For a *clean* (single-variable) generalization measurement, the width study
(train @4 px, test @2/6/8 px) isolates altitude/GSD shift with everything else
fixed: region overlap (mIoU) drops 0.94→0.35 off-width while clDice stays ≥0.90
(`reports/visualizations/width_study/`, fig1). This complements the noisy real
2×2 with a controlled-variable result.

## 5. Limitations & next steps
- Binary task + disjoint taxonomies limit interpretability; a true marking↔marking
  aerial transfer needs SkyScapes (ingestion ready, license/compute pending).
- Small LoveDA subset (136 train); a larger run would tighten the off-diagonal.
- A domain-adaptation recipe (photometric/style aug + target pseudo-labels) is the
  natural follow-up to recover the cross-domain gap.
