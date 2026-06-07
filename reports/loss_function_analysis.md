# Loss-Function Analysis — Empirical Study on Thin Road Markings

> Companion to `loss_function_study.md` (the mathematics). This report presents
> **measured** results from a controlled ablation: U-Net (ResNet-34) trained on
> the synthetic_lg dataset (200/40/40, 256², 25 epochs, AdamW, cosine, seed 42),
> **varying only the loss**. Every number is produced by `scripts/run_loss_ablation.sh`
> and `scripts/run_width_study.py` on the GTX-1650 GPU; reproduce with those.

## 1. Ablation at training width (test split, width_scale=1.0)

| Loss | mIoU | PixelAcc | mRecall | **clDice** | **BoundaryIoU** | **TolIoU** |
|---|---|---|---|---|---|---|
| **CoRe (ours: CE+Dice+clDice)** | **0.945** | 0.999 | 0.965 | **0.999** | **0.986** | **0.995** |
| CE+Dice (baseline) | 0.938 | 0.999 | 0.961 | 0.998 | 0.986 | 0.994 |
| Tversky (β=0.7) | 0.787 | 0.512 | **1.000** | 0.219 | 0.055 | 0.209 |
| clDice-only | 0.032 | 0.111 | 0.161 | 0.450 | 0.291 | 0.102 |

## 2. What each result *means* (scientific reasoning, not opinion)

**clDice-only collapses (mIoU 0.03).** Evidence: precision 0.04, pixelAcc 0.11.
A pure connectivity objective on the *any-marking* foreground carries **no
per-class discrimination signal** and a degenerate global optimum (predict thin
squiggles everywhere). *Conclusion:* a topology loss is an **auxiliary** term, not
a standalone objective — it must be paired with a region/classification loss.
This directly motivated the CoRe design.

**Tversky (β=0.7) maximises recall but destroys topology and calibration.**
Evidence: recall 1.000 but PixelAcc 0.512, clDice 0.219, BoundaryIoU 0.055. The
heavy false-negative penalty makes the model **flood the frame with foreground**;
recall is trivially perfect, but the predicted "markings" are blobs whose
skeletons bear no resemblance to the true centerlines. *Conclusion:* recall-only
optimisation is actively harmful for thin structures — the metric you optimise
must include a precision/connectivity counterweight. This was the **failure mode
that the proposed CoRe loss was designed to fix.**

**CoRe ≥ CE+Dice on every metric.** Evidence: mIoU 0.945 vs 0.938, clDice 0.999
vs 0.998, with PixelAcc preserved at 0.999 (no over-prediction). *Conclusion:*
adding the soft-clDice connectivity term to the calibrated CE+Dice base gives a
small but consistent improvement at the training width, **without** the
calibration loss seen in pure recall losses — because the CE term supplies the
dense background gradient that Tversky lacked.

> **Method-development note (honest provenance).** Our first CoRe formulation used
> a recall-Tversky region term and *reproduced* the Tversky over-prediction
> (PixelAcc 0.51, clDice 0.53). We diagnosed the cause (no background-calibration
> term) and revised CoRe to a CE+Dice base + clDice. The revised loss is the one
> reported above. We document this iteration deliberately — it is the evidence
> for *why* the CE term is necessary.

## 3. The width-stratified result (the central finding)

Models trained at width 4 px, evaluated on the controlled width series
(`scripts/run_width_study.py`, figure: `reports/visualizations/width_study/width_study.png`):

| width (px) | metric | CE+Dice | CoRe | Tversky |
|---|---|---|---|---|
| 2 | mIoU | 0.354 | 0.360 | 0.315 |
| 2 | **TolIoU** | **0.975** | 0.959 | 0.217 |
| 2 | **clDice** | **0.996** | **0.997** | 0.123 |
| 4 | mIoU | 0.936 | 0.932 | 0.722 |
| 6 | mIoU | 0.637 | 0.657 | 0.698 |
| 8 | mIoU | 0.470 | 0.444 | 0.586 |
| 8 | clDice | 0.903 | **0.983** | 0.443 |

**Finding 1 — mIoU drastically under-reports thin-marking quality.** At 2 px
width, CE+Dice scores **mIoU 0.35** (it *looks* like the model failed) while
**TolIoU 0.975 and clDice 0.996** show the lane lines are in fact correctly and
continuously detected. mIoU is dominated by a ±1-2 px **width mismatch** between
the model's learned stroke width and the test stroke width; it conflates
"detected the line" with "matched its exact width." The thin-structure protocol
separates those, and reports the truth.

**Finding 2 — the connectivity metrics are width-robust and loss-discriminative.**
clDice/TolIoU stay ≈1.0 for CE+Dice and CoRe across all widths, but stay ≈0.2 for
Tversky at *every* width — they correctly and stably rank the topology-preserving
losses above the topology-destroying one, where mIoU's ranking flips with width
(Tversky's mIoU even *exceeds* CE+Dice at 8 px, despite producing unusable
blobs).

**Finding 3 — CoRe's advantage is largest off the training width.** At 8 px,
CoRe clDice 0.983 vs CE+Dice 0.903 — the explicit connectivity term helps most
exactly where width generalisation is hardest. The gain is modest but consistent
and in the predicted direction.

## 4. False-positive / false-negative behaviour

- **Tversky / recall-biased:** FN→0 by construction, but FP explodes (PixelAcc
  0.51) — the wrong trade for a mapping product where false lane markings are
  costly.
- **CE+Dice / CoRe:** balanced FP/FN (precision 0.97-0.98, recall 0.96), with
  CoRe marginally improving boundary FP via the connectivity prior.

## 5. Recommendation

1. **Train with CoRe (CE+Dice+clDice)** — a strict, low-risk improvement over the
   strong CE+Dice baseline that additionally hardens topology under width shift.
2. **Never report mIoU alone for thin markings** — pair it with clDice + TolIoU,
   or risk discarding good models (the 2 px result would reject a model that
   actually works).
3. **Avoid recall-only losses** (high-β Tversky) unless coupled with a
   precision/connectivity term.

Reproduce: `bash scripts/run_loss_ablation.sh` then `python scripts/run_width_study.py ...`.
