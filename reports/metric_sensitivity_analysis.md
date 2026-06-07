# Metric-Sensitivity Analysis: Which Metrics Mis-Rank, and Why

This analysis hardens the paper's central claim by adversarially testing it
against *every* common IoU/accuracy definition, not only the foreground-averaged
mIoU. It uses the converged-operating-point models from the RLMD 25-class loss
ablation (U-Net++). Reproduce: `python scripts/analyze_metric_sensitivity.py`.

## 1. The data (RLMD test, 6 losses, all metric variants)

| Loss | fg-mIoU | all-class mIoU | FWIoU | PixelAcc | clDice |
|---|---|---|---|---|---|
| CE | 0.010 | 0.049 | 0.965 | 0.982 | 0.063 |
| Dice | 0.140 | 0.134 | 0.006 | 0.008 | 0.062 |
| CE+Dice | 0.029 | 0.067 | **0.969** | **0.983** | **0.373** |
| Focal | 0.018 | 0.057 | 0.967 | 0.983 | 0.085 |
| Tversky | **0.144** | **0.138** | 0.006 | 0.009 | 0.084 |
| CoRe | 0.005 | 0.044 | 0.965 | 0.981 | 0.275 |

Rankings (best→worst):
```
fg-mIoU       : tversky > dice > ce_dice > focal > ce > core
all-class mIoU: tversky > dice > ce_dice > focal > ce > core      (SAME — flooders win)
FWIoU         : ce_dice > focal > ce > core > dice > tversky      (flooders lose)
PixelAcc      : ce_dice ≈ focal ≈ ce ≈ core ≫ dice ≈ tversky
clDice        : ce_dice > core > focal > tversky > ce > dice      (correct order)
```

## 2. Three tests — only clDice passes all three

A metric for thin-marking model selection should pass three tests (automated in
`scripts/analyze_metric_sensitivity.py`):

1. **Test 1 — does its #1-ranked model flood the frame?** (a frame-flooder has
   PixelAcc < 0.05: it labels ~99 % of pixels as a marking).
2. **Test 2 — does it rank the genuine best detector first?** (CE+Dice is the only
   loss with high centerline precision, 0.91; it is the de-facto best.)
3. **Test 3 — is it foreground-sensitive?** (does it spread the non-flooding losses,
   whose true quality spans clDice 0.06–0.37, by more than noise?)

| Metric | T1: top pick floods? | T2: best detector #1? | T3: spread | Pass? |
|---|---|---|---|---|
| **mIoU** (fg) | ❌ **floods** (Tversky, PixAcc 0.009) | ❌ no (#3) | 0.023 | **fails** |
| **mIoU** (all-class) | ❌ **floods** (Tversky) | ❌ no (#3) | 0.023 | **fails** |
| FWIoU | ✅ ok (CE+Dice) | ✅ yes | ❌ **0.005** | fails (insensitive) |
| PixelAcc | ✅ ok (CE+Dice) | ✅ yes | ❌ **0.003** | fails (insensitive) |
| **clDice** | ✅ ok (CE+Dice) | ✅ yes | ✅ **0.310** | **passes all 3** |

**Key result:** mIoU — the field default, in **both** its all-class and
foreground forms — ranks a *frame-flooding* model first (Test 1) and buries the
genuine best detector at #3 (Test 2). The obvious fixes, FWIoU and PixelAcc, avoid
rewarding flooding but are *dominated by the 98 % background* and cannot tell a
clDice-0.06 model from a clDice-0.37 one (spread ≤0.005 vs clDice's 0.31). Only the
topology metric, clDice, passes all three.

## 3. Why all-class mIoU also mis-ranks (mechanism)

mIoU averages per-class IoU *equally* across classes. The flooding losses earn a
small but non-zero IoU on *many* of the 24 rare foreground classes (by predicting
them everywhere), while the calibrated losses score ≈0 on rare classes (they
predict background). Equal averaging therefore favours the flooder even though its
background IoU is ≈0. This is not a quirk of the foreground-only convention; it is
intrinsic to equal-per-class averaging under extreme imbalance.

## 4. Honest scope (what this claim is and is NOT)

- **It is a multi-class, extreme-imbalance phenomenon.** On a *binary* marking task
  mIoU does *not* reward flooding (a flooder's foreground IoU ≈ coverage ≈ 0.02,
  so binary mIoU is low). We state this explicitly; the mis-ranking claim is
  scoped to multi-class segmentation with a long-tail class distribution — which
  is the realistic road-marking setting (25 classes, 609:1).
- **The models are at different operating points**, none excellent (best clDice
  0.37). The claim is about *metric ordering*, not absolute quality: a metric
  should rank the least-bad detector highest; mIoU instead ranks the flooder
  highest.
- The *separate*, convergence-clean evidence that mIoU under-reports *correctly
  detected* thin structures (width-coupling) is the synthetic width study
  (`multiseed_width_study.md`), which does not depend on imbalance.

## 5. The precise, defensible claims (post-adversarial)

**C-primary (width-coupling, converged, synthetic):** mIoU under-reports
correctly and continuously detected thin markings because it couples detection
with exact-width matching (mIoU 0.35 vs clDice 1.0 / TolIoU 0.97 at 2 px).

**C-secondary (multi-class imbalance, real):** under extreme multi-class imbalance,
equal-averaged mIoU (all-class and foreground) *rewards frame-flooding* and so
*mis-ranks* losses; FWIoU/PixelAcc avoid this but are *insensitive* to foreground
quality; only topology metrics (clDice) are both flood-robust and sensitive.

These two are the claims the paper should make. The earlier blanket "mIoU
mis-ranks" is replaced by these scoped, evidence-backed statements.
