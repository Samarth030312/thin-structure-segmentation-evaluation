**Multi-seed results (3 seeds: 42, 123, 999), mean ± 95% CI half-width.**

Per-loss summary (CIs are bootstrap 95% half-widths over the 3 seeds):

| loss | mIoU | PixelAcc | clDice | clRecall | TolIoU |
|:-----|:-----|:---------|:-------|:---------|:-------|
| ce_dice | 0.0506 ± 0.0272 | 0.9831 ± 0.0013 | 0.4045 ± 0.0652 | 0.3871 ± 0.0572 | 0.3476 ± 0.0583 |
| core    | 0.0072 ± 0.0027 | 0.9784 ± 0.0026 | 0.4056 ± 0.1599 | 0.3625 ± 0.1782 | 0.3249 ± 0.1272 |

**Paired comparison (CE+Dice − CoRe, clDice), n = 3 paired seeds:**

| quantity | value |
|:---------|:------|
| mean difference (Δ) | **−0.0011** |
| 95% CI of Δ | **[−0.1823, 0.1802]** |
| CE+Dice better on all seeds? | **No** (CoRe wins at seed 999) |

**Interpretation.** The clDice difference between CE+Dice and CoRe is **not
significant**: the paired-difference 95% CI [−0.18, 0.18] straddles 0, and the per-loss
CIs overlap heavily (CoRe's variance is ~2.5× larger). CoRe is a **null result** — it
ties the CE+Dice baseline and is reported as such.

*(Note: per-loss rows have no paired columns by construction; the paired statistics are
the dedicated block above. Source: per-seed eval JSONs aggregated by
`src/uavroadmark/metrics/stats.py`.)*
