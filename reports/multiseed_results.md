# Multi-Seed Results — and a Result That Overturns a Single-Seed Claim

> Headline loss comparison (CE+Dice vs CoRe), U-Net++/RLMD, **converged budget**
> (subsample 500, 12 epochs, 384², identical to the reference runs), seeds
> **42, 123, 999**. Reproduce: `bash scripts/run_multiseed.sh`,
> `python scripts/analyze_multiseed.py`. (5 seeds at this converged budget exceed
> the GPU-hour budget; 3 converged seeds is the honest, feasible choice — see §4.)

## 1. Per-seed clDice (RLMD test, 276 images)

| seed | CE+Dice | CoRe |
|---|---|---|
| 42 | 0.373 | 0.275 |
| 123 | 0.471 | 0.386 |
| 999 | 0.370 | **0.556** |
| **mean ± std** | **0.405 ± 0.058** | **0.406 ± 0.141** |

Paired (matched-seed) difference CE+Dice − CoRe: **−0.001, 95% CI [−0.18, +0.18]**
— **not significant**, and **CoRe wins at seed 999**.

## 2. The finding: the single-seed "CE+Dice > CoRe" does NOT survive multi-seed

This is the most important result of the final review, and it **corrects our
own earlier claim**:

- At **seed 42 alone**, CE+Dice beats CoRe (per-image paired bootstrap, p<0.001 —
  a *valid within-seed* result, `reports/stats_clean/`).
- Across **3 seeds**, the means are **indistinguishable** (0.405 vs 0.406); the
  per-seed advantage **reverses at seed 999** (CoRe 0.556 ≫ CE+Dice 0.370).
- **CoRe has ~2.4× higher seed variance** (±0.141 vs ±0.058): it is sometimes much
  better and sometimes worse — *less stable*, not *worse on average*.

**Corrected conclusion:** on real RLMD, **CE+Dice and CoRe are statistically
indistinguishable in mean clDice; CoRe is higher-variance.** Neither is a reliable
winner at this budget. The earlier single-seed "CE+Dice significantly beats CoRe"
was a **seed artifact** — exactly the failure mode multi-seed experiments exist to
catch.

## 3. What is unaffected (the central thesis stands)

The project's headline — **mIoU mis-ranks losses** (Tversky/Dice flood the frame,
top mIoU, PixelAcc 0.008; `loss_ablation_clean.md`) — is **independent of the
CoRe/CE+Dice question** and is unaffected. It concerns metric behaviour, is
visible in every seed, and remains the paper's contribution. CoRe is, and remains,
a *studied* loss with an honest, now-multi-seed-confirmed verdict (no reliable
gain), not a claimed win.

## 4. Honest scope

- **3 seeds, not 5.** At the converged budget (~13–20 min/run on the 4 GB GPU),
  5 seeds × 2 losses exceeds the available GPU-hours; we ran 3 converged seeds.
  The variance estimate (CoRe ±0.141) is itself noisy at n=3 — a larger seed set
  is future work, and would tighten the (already null) mean difference.
- CoRe's seed-999 spike (0.556) and seed-42 dip (0.275) suggest its soft-skeleton
  term creates a rougher loss landscape (sensitive to init) — a concrete avenue
  to stabilise it (warm-up/temperature tuning).
- CoRe at seeds 123/999 required batch 2 + grad-accum 4 (its skeleton autograd
  OOMs at batch 4 on 4 GB) — a real memory cost of the connectivity term, noted
  for deployment.

## 5. Verdict for the paper

Report **CE+Dice and CoRe as statistically tied** on real data (mean clDice 0.405
vs 0.406, n=3 seeds), with CoRe higher-variance. Do **not** claim either loss
wins. Keep the mIoU-mis-ranking finding as the contribution.
