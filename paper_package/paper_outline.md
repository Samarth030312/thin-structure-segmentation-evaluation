# Paper Outline

**Working title:** *Beyond mIoU: Topology-Aware Evaluation Reveals That Standard
Metrics Mis-Rank Road-Marking Segmentation Models*

**Target venue:** IEEE ITSC (8-page) → extend to IEEE T-ITS (journal). Alt: CVPR
Workshop on Autonomous Driving / WACV.

## Abstract (≈200 words)
Thin road markings; mIoU is the field standard; we show it mis-measures *and*
mis-ranks on real data; propose a thin-structure protocol; controlled + real
evidence; honest multi-seed CoRe result (ties CE+Dice); deployment.

## 1. Introduction
- UAV/AV marking perception; thin+sparse+imbalanced.
- Gap: evaluation uses mIoU, blind to connectivity.
- Contributions: (i) thin-structure protocol; (ii) real-data mis-ranking finding;
  (iii) connectivity-loss study incl. honest synthetic→real transfer; (iv) open
  framework + ingestion + C++ deploy.
- Fig 1 teaser: width study (mIoU collapses, clDice stable).

## 2. Related Work
- Segmentation architectures (U-Net…SegFormer); thin/tubular (clDice, Boundary-IoU);
  losses (Dice/Focal/Tversky); aerial-marking datasets; AV evaluation.

## 3. Thin-Structure Evaluation Protocol
- clDice, Boundary-IoU, tolerance-IoU/centerline-F1, width-stratified analysis.
- Definitions + why each is appropriate for markings. (Table: metric definitions.)

## 4. Connectivity-Recall (CoRe) Loss
- soft-skeleton clDice + calibrated CE+Dice; warm-up. (Eq. 1.)
- Stated as a *studied* method, not assumed winner.

## 5. Benchmark & Datasets
- RLMD (real, 25 classes) — primary; LoveDA (real aerial) — cross-dataset;
  controlled synthetic (width) — variable isolation. (Table: dataset survey.)
- Ingestion, splits, EDA (imbalance 609:1).

## 6. Experiments
- 6.1 Setup (HW, schedule, seeds, metrics).
- 6.2 mIoU mis-ranks (real loss ablation) — **headline** (Fig 2, Table 2).
- 6.3 Width-stratified mechanism (synthetic) (Fig 1).
- 6.4 Architecture sweep (Table 3).
- 6.5 CoRe: synthetic win, real multi-seed tie (higher variance); Fig 4.
- 6.6 Cross-dataset generalization (Fig 5).
- 6.7 Performance/deployment Pareto (Fig 3, Table 4).
- 6.8 Failure taxonomy + explainability (Fig 6).

## 7. Discussion
- What metric to report; recommended model/loss; honest limitations
  (compute-bounded, ground-view real data, CoRe high-variance tie).

## 8. Conclusion + Future Work
- Adopt topology-aware eval; aerial-UAV validation; rare-class recall; India dataset.

## Figures (paper_figures/)
1. width_study · 2. rlmd_loss_ablation · 3. perf_pareto · 4. stats_ci ·
5. cross_dataset · 6. qualitative (failure/gradcam panels).

## Tables (paper_tables/)
1. metric defs · 2. RLMD loss ablation · 3. arch sweep · 4. perf/deploy ·
5. dataset survey · 6. multi-seed CIs.
