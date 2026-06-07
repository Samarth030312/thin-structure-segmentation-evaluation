# Anticipated Reviewer Concerns & Responses

Pre-emptive notes for rebuttal — each pairs a likely critique with our evidence.

### R1: "Your main results are on synthetic data."
**Response:** The *headline* result (mIoU mis-ranks losses) is on **real RLMD**
(`loss_ablation_clean.md`): Tversky tops mIoU (0.144) but PixelAcc 0.009. Synthetic
is used *only* to isolate the *mechanism* (width-coupling). Real RLMD EDA (609:1
imbalance) shows the problem is *worse* in the wild.

### R2: "Why not test on aerial UAV data (the title says UAV)?"
**Response:** We acquired/ingested two real datasets (RLMD ground markings; LoveDA
aerial) and built drop-in ingestion for SkyScapes (aerial markings). SkyScapes
requires a DLR research agreement + >4 GB GPU not available for this submission;
the pipeline runs it unchanged. We will add it in a future revision. (Honest limitation,
stated in §7.)

### R3: "Your proposed CoRe loss — does it actually help?"
**Response:** Honestly, no reliable gain on real data, and we say so. CoRe wins on
synthetic; at seed 42 CE+Dice beats it; but across **3 seeds** they are **tied**
(clDice 0.405 vs 0.406, Δ=−0.001, CI [−0.18,0.18]), CoRe higher-variance. We
include it as a *methodological cautionary tale* — a single-seed loss win that
multi-seed dissolves. The contribution is the **metric** finding, not CoRe.

### R4: "mIoU mis-ranking could be an artifact of 25-class averaging."
**Response:** The effect is driven by *frame-flooding* (PixelAcc 0.008 for the
top-mIoU losses), which we measure directly; it is not a pure averaging artifact.
The synthetic *binary* width study shows the same metric/quality divergence with
clean control. We report mIoU, clDice, *and* PixelAcc so the mechanism is visible.

### R5: "Compute is tiny (4 GB GPU, subsampled, few epochs)."
**Response:** Acknowledged and disclosed. The *qualitative* conclusions
(mis-ranking, flood/collapse, CoRe high-variance tie) are budget-independent — they concern
what the metrics *can see*, not absolute accuracy. Multi-seed CIs
(`multiseed_results.md`) test stability. Full-scale runs are future work.

### R6: "Statistical significance?"
**Response:** Per-image bootstrap 95% CIs + paired bootstrap tests
(`run_stats_compare.py`) at the per-image level *within a seed*; across 3 seeds
the CE+Dice–CoRe difference is null (Δ=−0.001, CI [−0.18,0.18]) — we report the
multi-seed result as authoritative. Rank inversion (mIoU vs clDice over 6 losses)
quantified by Spearman ρ=−0.31; the *flood* mechanism (PixelAcc 0.008) is measured
directly and is robust across seeds.

### R7: "Novelty — clDice/Boundary-IoU already exist."
**Response:** Our contribution is **not** inventing clDice; it is (i) the
*demonstration*, on real road-marking data, that mIoU *inverts* model/loss
rankings — a finding specific to this task that the community currently ignores;
(ii) a width-stratified protocol; (iii) an honest connectivity-loss transfer
study; (iv) an open, reproducible benchmark + deployment path.

### R8: "Reproducibility?"
**Response:** All seeds fixed, configs committed, every report lists its command,
62 tests + CI, hardware report, ingestion scripts for 3 datasets.
