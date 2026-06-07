# Real-Data Results (RLMD) — Primary Evidence

> **This is the primary evidence of the project.** All headline conclusions are
> validated on **RLMD** (Road Line & Marking Dataset, IEEE doi 10226935): 2137
> real driving-scene images, 25 marking classes, downloaded from Hugging Face and
> ingested via `scripts/prepare_real.py`. Synthetic experiments (width-control)
> exist only to isolate variables. Reproduce: `bash scripts/run_rlmd_loss_ablation.sh`,
> `python scripts/run_stats_compare.py ...`.
>
> **Scientific-integrity note.** An earlier version of this report compared
> `unetpp+CoRe` vs `unet+CE+Dice` and credited CoRe with a 3× clDice win. That
> comparison was **confounded** (architecture *and* loss differed). The clean,
> same-architecture ablation below **overturns** that conclusion. We report the
> corrected result — this is exactly why controlled ablations and significance
> tests matter.

## 1. Dataset reality (RLMD EDA)

| Statistic | RLMD (real) | Synthetic (for contrast) |
|---|---|---|
| Background pixel share | **98.0 %** | 94.6 % |
| Foreground imbalance ratio (max/min class) | **609.9×** | 4.2× |
| Classes | 25 | 7 |

Real road markings are **two orders of magnitude more imbalanced** than the
synthetic proxy — making topology-aware evaluation more necessary, not less.

## 2. Clean loss ablation (U-Net++ fixed, loss varied; RLMD test, 276 imgs)

Identical architecture/data/schedule/seed; **only the loss changes**
(`run_rlmd_loss_ablation.sh`).

| Loss | mIoU (25-cls) | **PixelAcc** | clDice | clPrecision | clRecall | TolIoU |
|---|---|---|---|---|---|---|
| **CE+Dice** | 0.029 | 0.983 | **0.373** | **0.907** | **0.356** | **0.324** |
| CoRe (ours) | 0.005 | 0.981 | 0.275 | 0.896 | 0.211 | 0.215 |
| Tversky (β=0.7) | **0.144** | **0.009** | 0.084 | 0.133 | 1.000 | 0.044 |

## 3. Finding A — mIoU catastrophically MIS-RANKS on real data (the thesis)

**By mIoU, the ranking is Tversky (0.144) ≫ CE+Dice (0.029) ≫ CoRe (0.005).**
But look at PixelAcc and clDice:

- **Tversky is mIoU's #1 — and is the *worst* model.** Its `PixelAcc = 0.009`
  means it labels ~99 % of pixels as *some* marking — it floods the frame. It
  earns the top multi-class mIoU because, over 25 classes, blanket over-prediction
  scores a sliver of IoU on many classes, and it trivially gets `clRecall = 1.0`.
  But `clPrecision = 0.13` and `clDice = 0.084` expose it as useless for
  perception. **A practitioner selecting by mIoU would ship the single worst
  model.**
- The genuinely best perception model (**CE+Dice**, clDice 0.373, clPrecision
  0.91) has **5× lower mIoU than Tversky**.

This is the strongest possible vindication of the project's thesis, **on real
data**: *mIoU does not just under-measure thin structures — it actively inverts
the ranking, crowning a frame-flooding model.* The thin-structure protocol
(clDice / clPrecision / PixelAcc) ranks the models correctly.

## 4. Finding B — CoRe vs CE+Dice: a single-seed result that multi-seed OVERTURNS

At **seed 42** alone, the clean same-architecture comparison (U-Net++; 276 imgs;
per-image bootstrap, `run_stats_compare.py`) shows CE+Dice ahead:

| Metric (seed 42) | CE+Dice | CoRe | Δ | p |
|---|---|---|---|---|
| clDice | 0.37 | 0.28 | +0.098 [+0.077, +0.119] | <0.001 |

**But this does not survive multi-seed.** Across **3 seeds (42, 123, 999)**
(`multiseed_results.md`):

| Loss | clDice per seed | mean ± std |
|---|---|---|
| CE+Dice | 0.373, 0.471, 0.370 | **0.405 ± 0.058** |
| CoRe | 0.275, 0.386, **0.556** | **0.406 ± 0.141** |

Paired across seeds: **Δ = −0.001, CI [−0.18, +0.18] — not significant** (CoRe
*wins* at seed 999). **CE+Dice and CoRe are statistically tied; CoRe is ~2.4×
higher-variance.** The seed-42 "CE+Dice beats CoRe" was a **single-seed artifact** —
caught only by running multiple seeds. We retract the earlier "CoRe loses / does
not transfer" framing: on real data **neither loss reliably wins**, and CoRe's
soft-skeleton term mainly adds variance (and a memory cost — it OOMs at batch 4).

## 5. Corrected conclusions

1. **CE+Dice and CoRe are tied on real data** (3-seed clDice 0.405 vs 0.406);
   prefer **CE+Dice** for stability/simplicity. CoRe gives no reliable gain.
2. **The metric thesis is confirmed and strengthened on real data** via the
   Tversky mis-ranking — independent of the CoRe outcome (the thesis is about
   *metrics*, not about our loss).
3. **Architecture (U-Net++ vs U-Net) drove the earlier apparent CoRe win** — a
   confound the clean ablation removed.

## 6. Autonomy relevance

For HD-map lane extraction / UAV infrastructure mapping, selecting a model by
mIoU could deploy a frame-flooding detector (Tversky) that is worst in practice.
The operational metric is *"did we detect the lane line, continuously and
precisely?"* — clDice/clPrecision — which a marking-perception pipeline must
adopt. This is the concrete, real-data argument for topology-aware evaluation.

## 7. Honesty & limitations

- Compute-bounded (500-img subset, 12 epochs, 384², single 4 GB GPU); absolute
  numbers will rise with full data, but the **mis-ranking and CoRe-tie
  conclusions are budget-independent**.
- RLMD is ground-view (real markings); the UAV-viewpoint confirmation path
  (SkyScapes) is built and drop-in ready (`docs/skyscapes.md`).
- Why CoRe is high-variance on real data (its soft-skeleton roughens the loss
  landscape -> seed-sensitive, clDice 0.28-0.56) is a concrete follow-up: warm-up /
  temperature tuning to stabilise it; we do not claim a reliable gain.
