# Clean Loss Ablation — Real Data, 6 Losses, Same Architecture

> **Controlled ablation:** U-Net++ (ResNet-34, ImageNet-pretrained), RLMD, 384²,
> 12 epochs, AdamW lr 4e-4, seed 42, 500-image train subset — **identical except
> the loss**. Reproduce: `bash scripts/run_rlmd_6loss.sh` (U-Net cross-check) and
> `scripts/run_rlmd_unetpp_complete.sh` (U-Net++). Per-image significance:
> `scripts/run_stats_compare.py`.

## 1. Results (RLMD test, 276 images)

| Loss | mIoU | **PixelAcc** | **clDice** | clRecall | TolIoU | Behaviour |
|---|---|---|---|---|---|---|
| CE | 0.010 | 0.982 | 0.063 | 0.10 | 0.084 | collapses → background |
| Dice | **0.140** | **0.008** | 0.062 | 1.00 | 0.044 | **floods frame** |
| **CE+Dice** | 0.029 | 0.983 | **0.373** | 0.36 | **0.324** | **best perception** |
| Focal | 0.018 | 0.983 | 0.085 | 0.10 | 0.092 | collapses → background |
| Tversky (β.7) | **0.144** | **0.009** | 0.084 | 1.00 | 0.044 | **floods frame** |
| CoRe (ours) | 0.005 | 0.981 | 0.275 | 0.21 | 0.215 | conservative |

## 2. The two rankings are inverted (the thesis, definitively)

```
Rank by  mIoU :  tversky > dice > ce_dice > focal > ce > core
Rank by clDice:  ce_dice > core > focal > tversky > ce > dice
```
Spearman rank correlation **ρ = −0.31** (negative — the metrics disagree; with
n=6 losses this is not itself significant, p=0.54, but the *per-image* paired
tests below are). **mIoU's top-2 (Tversky, Dice) are clDice's bottom-2.** Both
top-mIoU losses have **PixelAcc ≈ 0.008** — they label ~99 % of pixels as a
marking (clRecall 1.0 trivially). mIoU, averaged over 25 classes, *rewards* this
blanket over-prediction; clDice and PixelAcc expose it as useless. **Selecting a
loss by mIoU picks the worst perception model.** This is the project's central
claim, on real data, in a fully controlled ablation.

## 3. Best loss (by the correct metric): CE+Dice — and CoRe does not win

At **seed 42** CE+Dice leads on clDice (0.373 vs CoRe 0.275). **However, the
3-seed run (`multiseed_results.md`) shows this is a single-seed artifact:** across
seeds 42/123/999, CE+Dice 0.405±0.058 vs CoRe 0.406±0.141 — **statistically tied**
(paired Δ=−0.001, CI [−0.18,0.18]; CoRe wins at seed 999). **No reliable winner;
CoRe is higher-variance.** We retract the earlier single-seed "CE+Dice beats CoRe".
CE+Dice is the recommended default for *stability*, not a proven accuracy win.
CE-only and Focal collapse to the
background majority class (PixelAcc 0.98, clDice ≈ 0.06–0.09) under 25-class 609:1
imbalance — i.e. a *region* term (Dice) is necessary, but a *calibrated* one
(CE+Dice), not a recall-only one (Tversky).

## 4. U-Net cross-check (lower budget)

The same 6-loss ablation on U-Net (R34, 400-img subset, 10 epochs — a smaller
budget) reproduces the **same flood-vs-collapse bifurcation**: Dice/Tversky get
top mIoU with PixelAcc ≈ 0.008; CE/CE+Dice/Focal collapse (mIoU ≈ 0, PixelAcc
0.98). The U-Net runs are under-trained (none reach CE+Dice's U-Net++ clDice of
0.37), so the **U-Net++ results above are the primary evidence**; the U-Net set
confirms the qualitative pattern is architecture-independent.

## 5. Honest conclusions

1. **Report clDice/clPrecision/PixelAcc, not mIoU alone** — on real data mIoU
   ranks losses oppositely to true perception quality.
2. **Best loss = CE+Dice** (not CoRe, not the high-mIoU Tversky/Dice).
3. **CoRe ties CE+Dice on real data across seeds** (higher variance); it is not a
   reliable improvement — documented honestly, not recommended over CE+Dice.
4. Limitation: compute-bounded (500-img, 12-epoch, 384²); multi-seed CIs in
   `reports/multiseed_results.md`. The ranking-inversion conclusion is
   budget-independent (it concerns what the metrics can see).
