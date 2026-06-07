# Paper Positioning & Novelty Analysis

## Part 1 — Novelty of each contribution (evidence-based)

| Contribution | Novelty | Comparison to prior work | Verdict |
|---|---|---|---|
| **A. Thin-structure evaluation protocol** (clDice, Boundary-IoU, tolerance-IoU, width-stratified) | **Low–Moderate** | clDice [Shit, CVPR'21] and Boundary-IoU [Cheng, CVPR'21] are existing metrics; we *assemble* and *apply* them to road markings and add a width-stratified view. The width-stratified analysis is the only genuinely new piece, and it is a tool, not a metric. | Re-application + a small new analysis. |
| **B. mIoU failure / mis-ranking analysis** | **Moderate** | That overlap/accuracy metrics reward over-prediction under imbalance is known; the *specific, quantified demonstration that loss/model rankings invert on real road markings* (Tversky tops mIoU at PixelAcc 0.009) is a contribution not commonly shown for this task. | **The strongest contribution.** |
| **C. CoRe loss** | **Low** | A CE+Dice+soft-clDice combination; soft-clDice is from [Shit'21]. Empirically a **null result** (ties CE+Dice, higher variance). | Not a contribution; keep as a cautionary ablation. |
| **D. Cross-dataset findings** | **Low** | Binary foreground transfer across disjoint taxonomies + viewpoints; confounded and small (LoveDA test n=41). | Weak; demote to supplementary. |
| **E. Benchmarking framework / engineering** | **Moderate (as artifact)** | A clean, tested, reproducible benchmark with real-dataset ingestion and a deployment path. Engineering value, limited research novelty. | Valuable as a released artifact, not as a paper claim. |

**Primary story (recommended): Contribution B**, supported by A as the *instrument*
and the synthetic width study as the *controlled mechanism*. C and D are
de-emphasised/honest-negative; E is the released artifact.

## Part 2 — What the paper is *actually* about

Not "UAV road-marking perception" (no UAV marking results) and not "a new loss"
(CoRe is null). The defensible thesis is:

> **Standard region-overlap evaluation (mIoU) is unreliable — and can invert model
> and loss rankings — for thin road markings; topology/tolerance metrics
> (clDice, Boundary-IoU, tolerance-IoU) should be reported alongside it.**

This is an **evaluation / measurement** paper, demonstrated on road-marking
segmentation (ground-view RLMD + a controlled width benchmark).

## Part 3 — Recommended title

**Primary:**
> *"When mIoU Lies: Topology-Aware Evaluation of Thin Road-Marking Segmentation"*

**Alternatives:**
- "Beyond mIoU: Rank-Inverting Failures of Overlap Metrics on Thin Road Markings"
- "Does Your Metric Detect the Lane? A Topology-Aware Evaluation Protocol for Road-Marking Segmentation"
- "Mis-Ranking by mIoU: A Cautionary Benchmark for Thin-Structure Segmentation"

*(Drop "UAV" from the title unless real UAV-marking results are added.)*

## Part 4 — Recommended abstract direction

Lead with the **measurement problem** (mIoU couples detection with width matching;
under imbalance it rewards over-prediction). State the **finding** (on real
road markings, mIoU ranks a frame-flooding model first while topology metrics rank
correctly; the inversion is reproduced in a controlled width study). Present the
**protocol** (clDice/Boundary-IoU/tolerance-IoU + width-stratified analysis).
Report the **honest negative** (a connectivity loss does not reliably help — a
single-seed win dissolves under multi-seed). Release the **reproducible
framework**. Be explicit that results are on ground-view markings + a controlled
synthetic benchmark; full-scale and aerial-UAV validation are future work.

## Part 5 — Recommended contribution list (for the paper)

1. A **topology-aware evaluation protocol** for thin road markings, combining
   clDice, Boundary-IoU, and a tolerance-band centerline metric with a novel
   **width-stratified** analysis.
2. **Empirical evidence that mIoU mis-ranks** losses/models on road markings —
   crowning a frame-flooding model — corroborated by a controlled width study;
   with the **flooding mechanism measured directly** (PixelAcc).
3. An **honest, multi-seed connectivity-loss study** (CoRe) showing a single-seed
   loss advantage does not survive multiple seeds — a methodological caution.
4. A **reproducible, tested open-source benchmark** with real-dataset ingestion
   and a deployment (ONNX/TensorRT/C++) path.

**De-scope:** the UAV claim, the cross-dataset result, and any framing of CoRe as
a working method.
