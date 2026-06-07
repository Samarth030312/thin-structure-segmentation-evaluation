# Loss-Function Study for Class-Imbalanced Road-Marking Segmentation

> **Historical / superseded.** This document is from the project's initial benchmark-building phase. The project's actual contribution and current narrative is the **width-coupling law** for thin-structure evaluation metrics — see `reports/width_coupling_theory.md` and `paper_package/final_ieee_paper.pdf`. The "target UAV dataset" referenced below was an aspirational road-marking set that was **never acquired**; the experiments actually used a synthetic generator and the public datasets RLMD, LoveDA, Massachusetts Roads, and UAVid. See `reports/repository_integrity_report.md`.


> For thin, sparse road markings, the loss function is a *first-class*
> experimental variable. This study derives each loss mathematically, analyses
> its behaviour under extreme class imbalance, and states its suitability for
> road markings. Implementations live in
> `src/uavroadmark/losses/functional.py` and are unit-tested in
> `tests/test_losses.py`.

Notation: for pixel *i* and class *c*, let \(p_{i,c}\) be the predicted
probability (softmax of logits) and \(y_{i,c}\in\{0,1\}\) the one-hot ground
truth. All losses operate on **raw logits** — the single most important fix vs.
the original notebook, which applied `sigmoid` then `BCELoss`, causing
numerically unstable, vanishing gradients.

---

## 1. The core problem: imbalance

Our EDA measures **background ≈ 94.6 %** of pixels and a foreground imbalance
ratio ≈ 4.2 between the most- and least-common marking classes. Under this
regime a model that predicts "background everywhere" already scores ~95 % pixel
accuracy and near-zero foreground IoU. Any useful loss must **stop the abundant,
easy background from dominating the gradient.**

---

## 2. Cross-Entropy (CE)

$$\mathcal{L}_{CE} = -\frac{1}{N}\sum_i \sum_c w_c\, y_{i,c}\,\log p_{i,c}$$

- **Mechanism.** Per-pixel classification loss; smooth, well-conditioned
  gradients; the default optimisation workhorse.
- **Imbalance effect.** **Poor by itself** — every pixel contributes equally, so
  the 95 % background swamps the loss. Class weighting \(w_c\) (e.g. inverse
  frequency) partially compensates but is brittle (weights must be tuned; large
  weights destabilise training).
- **Road-marking suitability.** ★★☆☆☆ alone; ★★★★☆ as the *stabilising* half of a
  combo loss. Provides clean gradients that region losses lack near
  probabilities of 0/1.

## 3. Dice Loss

$$\mathcal{L}_{Dice} = 1 - \frac{1}{|C_{fg}|}\sum_{c\in C_{fg}}
\frac{2\sum_i p_{i,c} y_{i,c} + \epsilon}{\sum_i p_{i,c} + \sum_i y_{i,c} + \epsilon}$$

- **Mechanism.** A soft, differentiable surrogate for the Dice/F1 overlap.
  Region-based and **scale-invariant**: a 50-pixel lane line and a 50 000-pixel
  background region contribute *the same* per-class term.
- **Imbalance effect.** **Strong.** Because it normalises by region size, it is
  intrinsically insensitive to how many background pixels exist. We compute it
  over **foreground classes only**, directly optimising the headline metric.
- **Weaknesses.** Gradients are noisy/ill-conditioned when predictions are near
  0 or 1 (the denominator-coupled gradient), and unstable for empty classes
  (handled by \(\epsilon\) smoothing).
- **Road-marking suitability.** ★★★★☆ — directly targets foreground IoU/Dice.

## 4. Focal Loss

$$\mathcal{L}_{Focal} = -\frac{1}{N}\sum_i \sum_c \alpha_c\,
(1-p_{i,t})^{\gamma}\, y_{i,c}\,\log p_{i,c}, \quad p_{i,t}=p_{i,\text{true}}$$

- **Mechanism.** Multiplies CE by a **modulating factor** \((1-p_t)^\gamma\) that
  shrinks the loss of well-classified (easy) pixels. With \(\gamma=2\) (Lin et
  al.), a background pixel predicted at \(p_t=0.99\) has its loss scaled by
  \(10^{-4}\).
- **Imbalance effect.** **Strong** in the *hard-example* sense: it reweights by
  difficulty, not by region, so the easy background stops dominating while hard
  marking edges keep full gradient. \(\alpha\) adds optional class weighting.
- **Weaknesses.** Two hyper-parameters (\(\gamma,\alpha\)); can over-focus on
  noisy/mislabeled hard pixels.
- **Road-marking suitability.** ★★★★☆ — excellent for the thin, hard boundaries
  that define markings.

## 5. Tversky Loss

$$\mathcal{L}_{Tv} = 1 - \frac{1}{|C_{fg}|}\sum_{c}
\frac{TP_c + \epsilon}{TP_c + \alpha\,FP_c + \beta\,FN_c + \epsilon}$$
with soft \(TP_c=\sum_i p_{i,c}y_{i,c}\), \(FP_c=\sum_i p_{i,c}(1-y_{i,c})\),
\(FN_c=\sum_i (1-p_{i,c})y_{i,c}\).

- **Mechanism.** Generalises Dice (recovered at \(\alpha=\beta=0.5\)) by
  **decoupling the penalty on false positives vs. false negatives.**
- **Imbalance effect.** **Strong + tunable for recall.** Road markings are
  *under*-detected (thin → easy to miss). Setting \(\beta>\alpha\) (default
  0.7/0.3) penalises false negatives more, **pushing recall up** — usually the
  right bias for safety-relevant lane detection. (Unit-tested: with β>α a missed
  marking is penalised more than a spurious one — see
  `test_tversky_beta_gt_alpha_penalizes_false_negatives_more`.)
- **Weaknesses.** Same near-0/1 gradient issues as Dice; \(\alpha,\beta\) must be
  chosen (a small sweep is cheap and worthwhile).
- **Road-marking suitability.** ★★★★★ — the most *task-aware* loss: directly
  trades precision for recall in the direction safety demands.

## 6. Combo (CE + Dice)

$$\mathcal{L}_{Combo} = w_{ce}\,\mathcal{L}_{CE} + w_{dice}\,\mathcal{L}_{Dice}$$

- **Mechanism.** Sum of a **distribution** loss (CE: smooth pixel-wise gradients,
  good optimisation) and a **region** loss (Dice: imbalance-robust, metric-aligned).
- **Imbalance effect.** **Best of both.** CE keeps the optimisation
  well-conditioned where Dice's gradients are noisy; Dice supplies the
  imbalance-robust signal CE lacks. This is the pragmatic default across the
  medical/remote-sensing segmentation literature.
- **Road-marking suitability.** ★★★★★ — our **default** (`configs/loss/ce_dice.yaml`,
  \(w_{ce}=w_{dice}=0.5\)).

---

## 7. Summary & recommendation

| Loss | Gradient quality | Imbalance robustness | Recall control | Hyper-params | Default? |
|---|:--:|:--:|:--:|:--:|:--:|
| Cross-Entropy | **High** | Low | none | weights (opt.) | — |
| Dice | Med | **High** | none | — | — |
| Focal | High | **High** (hard-ex) | indirect (α) | γ, α | — |
| Tversky | Med | **High** | **direct (β>α)** | α, β | recall-critical runs |
| **Combo (CE+Dice)** | **High** | **High** | none | w_ce, w_dice | ✅ **default** |

**Recommendation.** Use **Combo (CE+Dice)** as the default; run **Tversky
(β=0.7)** when recall on thin markings is the priority (most AV lane-keeping
cases); benchmark **Focal** as the hard-example alternative. The loss is treated
as a controlled experimental axis in the final report's ablation — *changing only
the loss, holding architecture/data/schedule fixed.*

### How to reproduce the loss ablation

```bash
for L in ce dice focal tversky ce_dice; do
  uavrm-train --config configs/experiment/uav_uavid.yaml \
      --opt loss.name=$L run_name=deeplab_$L
  uavrm-eval  --config configs/experiment/uav_uavid.yaml \
      --opt run_name=deeplab_$L --checkpoint outputs/deeplab_$L/best.pth
done   # -> rows appended to reports/leaderboard.csv, ranked by foreground mIoU
```

---

## 8. References
- Lin et al. *Focal Loss for Dense Object Detection.* ICCV 2017.
- Milletari et al. *V-Net (Dice loss).* 3DV 2016.
- Sudre et al. *Generalised Dice overlap as a loss for imbalanced segmentation.* DLMIA 2017.
- Salehi et al. *Tversky loss for image segmentation.* MLMI 2017.
- Ma et al. *Loss odyssey in medical image segmentation.* Medical Image Analysis 2021.
