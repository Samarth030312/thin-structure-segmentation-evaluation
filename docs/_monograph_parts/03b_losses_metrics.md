## 3.9 Overlap losses: Dice and IoU

**Intuition.** Instead of averaging per-pixel errors, measure how well the predicted
foreground *region* overlaps the true region. This naturally focuses on the small
foreground and ignores the easy background.

**Dice coefficient.** For predicted set `P` and ground-truth set `G` (as binary
masks),
$$\text{Dice} = \frac{2|P\cap G|}{|P| + |G|}.$$
Range `[0,1]`; 1 = perfect overlap. The **Dice loss** is `1 − Dice` (made
differentiable by using soft probabilities for `|P|`).

**IoU (Jaccard).**
$$\text{IoU} = \frac{|P\cap G|}{|P\cup G|} = \frac{|P\cap G|}{|P| + |G| - |P\cap G|}.$$
Dice and IoU are monotonically related: `IoU = Dice/(2 − Dice)`. Both reward overlap;
IoU is stricter (penalises the union more).

**Numerical example.** A 3-px-wide line, GT has 300 px. The model predicts a 5-px
line fully containing it (over-segmentation), 500 px. Intersection = 300, union = 500,
`|P|+|G| = 800`.
- `IoU = 300/500 = 0.60`
- `Dice = 2·300/800 = 0.75`
The model *found the line perfectly* yet IoU reads 0.60 — **this single example is the
seed of the width-coupling law** (Part 7).

**Project relevance.** Dice loss is part of the CE+Dice loss used throughout because
it counteracts class imbalance. But IoU *as a metric* is exactly what the project
shows to be misleading for thin structures.

## 3.10 Tversky and Focal losses

**Tversky loss** generalises Dice with weights `α, β` on false positives and false
negatives:
$$\text{Tversky} = \frac{|P\cap G|}{|P\cap G| + \alpha|P\setminus G| + \beta|G\setminus P|}.$$
`α=β=0.5` recovers Dice. Raising `β` punishes *misses* (false negatives) more — useful
for rare structures you must not miss. **Caution (a project finding):** an
aggressive Tversky setting can make the model *over-predict* foreground to avoid
misses, flooding the image; mIoU can then *reward* that flooding (Part 8, the
mis-ranking result).

**Focal loss** modifies cross-entropy to down-weight easy examples:
$$L_\text{focal} = -(1-p_t)^\gamma \log p_t.$$
When the model is already right (`p_t→1`), `(1−p_t)^γ → 0` kills the loss, so training
focuses on hard pixels. `γ=2` is typical. Helps with imbalance but does not, by
itself, fix the thin-structure metric problem.

## 3.11 The combined and proposed losses

- **CE+Dice** (the project's reliable baseline): `L = w₁·CE + w₂·Dice`. CE gives
  stable pixel-wise gradients; Dice gives region/imbalance robustness. This is the
  best thin-structure *detector* in the ablation (highest clDice).

- **CoRe** (the proposed, *null-result* loss): `L = w_ce·CE + w_r·Dice +
  w_t·(1 − softclDice)`. The idea: add a connectivity term so the model is rewarded
  for preserving the *centerline*. On one seed it beat CE+Dice; across three seeds the
  gain vanished (`Δ ≈ −0.001`, n.s.). Reported honestly as a negative (Part 8). It is
  *supplementary*, not a contribution.

## 3.12 Metrics — the heart of the project

A **loss** is what you optimise (must be differentiable); a **metric** is what you
*report* (need not be differentiable). The project's thesis is about *metrics*. We
now define each precisely.

### 3.12.1 Pixel accuracy and its trap
`PixelAcc = (correct pixels)/(total pixels)`. For thin structures this is **useless**:
predict all-background and you score ~0.98. Worse, in the mis-ranking experiment a
flooding model scored `PixelAcc ≈ 0.009` (predicting foreground *everywhere*),
exposing flooders — but pixel accuracy cannot tell a clDice-0.06 model from a
clDice-0.37 one (it is foreground-insensitive). Never use it alone.

### 3.12.2 Mean IoU (mIoU) and its variants
Compute IoU per class, then average. Variants differ in *how* you average:
- **Foreground-mean mIoU:** average IoU over foreground classes only.
- **All-class mIoU:** include background.
- **Frequency-weighted IoU (FWIoU):** weight each class by its pixel frequency.

A project result: the thin-structure mis-ranking afflicts **both** foreground-mean
and all-class mIoU (it is not a mere averaging artifact), while FWIoU and PixelAcc
avoid the *flooding* trap but are *foreground-insensitive*. Only a topology metric is
both flood-robust and foreground-sensitive.

### 3.12.3 Boundary-IoU
**Intuition.** Compute IoU but only over a thin band of width `d` around the
boundaries of GT and prediction. It directly measures boundary quality.
**Definition.** `BoundaryIoU = |(∂G_d)∩(∂P_d)| / |(∂G_d)∪(∂P_d)|`, where `∂X_d` is
the set of pixels within `d` of `X`'s boundary. For thin structures the boundary band
*is* essentially the whole structure, so Boundary-IoU also drops with thinness — it
diagnoses the boundary sensitivity rather than curing it.

### 3.12.4 Tolerance-IoU (TolIoU)
**Intuition.** Count a predicted pixel as correct if it is within `τ` pixels of the
true structure (and vice-versa) — i.e. forgive small localisation errors.
**Effect.** With `τ=3`, a 1-px boundary wobble no longer counts as an error, so
TolIoU stays high for *detected* thin structures (≈0.95–0.98 in the controlled study)
while plain IoU collapses. TolIoU is one of the "honest" metrics for thin structures.

### 3.12.5 clDice — the centerline metric (the hero)
This metric is central to the law, so we build it carefully.

**Skeleton / centerline.** The **skeleton** of a shape is its one-pixel-thick "spine"
— the medial axis equidistant from the boundaries. Skeletonising a 5-px line and a
7-px line of the same path gives *the same* 1-px centerline. The skeleton captures
**topology and placement**, not width.

**clDice definition.** Let `S_P = skeleton(P)`, `S_G = skeleton(G)`. Define
- **Topology precision** `T_\text{prec} = |S_P \cap G| / |S_P|` — what fraction of
  the predicted skeleton lies inside the true mask;
- **Topology sensitivity** `T_\text{sens} = |S_G \cap P| / |S_G|` — what fraction of
  the true skeleton lies inside the prediction;
then
$$\text{clDice} = \frac{2\,T_\text{prec}\,T_\text{sens}}{T_\text{prec}+T_\text{sens}}.$$

**Intuition.** clDice asks: *did the prediction capture the true centerline, and is
the predicted centerline really on the structure?* It is blind to a uniform
±1-px width error, because that does not move the centerline. Hence **clDice ≈ 1 for a
correctly-detected structure regardless of width** — the other half of the law.

**Numerical example.** The 3-px line predicted as a 5-px line (Sec 3.9): both
skeletons are the same central curve. `S_G ⊂ P` and `S_P ⊂ G`, so `T_prec ≈ T_sens ≈
1` and `clDice ≈ 1.0` — versus IoU 0.60. The metrics *disagree by 0.40*, and that
disagreement is the project's signal.

**When clDice correctly drops.** If the prediction *breaks* the line (gaps, missed
segments), the skeleton no longer matches: `T_sens` falls, clDice falls. So clDice
rewards *detection/continuity* and ignores *width* — exactly the right behaviour for
"did we find the lane line?"

### 3.12.6 Soft skeletonisation (making clDice differentiable)
The skeleton (via iterative thinning) is non-differentiable, so it cannot be used in
a *loss*. The **soft skeleton** approximates it with differentiable morphology:
iterated soft-erosion and soft-opening using min/max-pooling surrogates. Each
iteration peels a layer; the residual that cannot be "opened" away is the soft
skeleton. This is what the CoRe loss's `softclDice` term uses. **Cost:** the iterated
pooling holds many intermediate tensors for autograd, which is memory-hungry — on the
4 GB GPU it caused out-of-memory at batch 4, forcing batch 2 + gradient accumulation
(Part 11). Its gradients are also tiny, contributing to the fp16 divergence.

## 3.13 Putting metrics in a table (the conceptual map)

```
  Metric         Measures            Thin-structure behaviour      Role here
  ----------------------------------------------------------------------------
  PixelAcc       per-pixel correct   ~0.98 always (useless)        trap
  mIoU           area overlap        COLLAPSES with thinness       the "lying" metric
  Dice           area overlap        collapses (like IoU)          loss component
  BoundaryIoU    boundary-band IoU   collapses (boundary = whole)  diagnostic
  TolIoU         overlap within τ    STAYS HIGH if detected        honest metric
  clDice         centerline overlap  STAYS HIGH if detected        the hero / reference
```

The whole project is, in one line: **mIoU and clDice disagree by a width-dependent
amount, and that amount is a law.** Sections 3.9 and 3.12.5 already contain the two
ends of it (IoU = 0.60 vs clDice = 1.0 for the 3-px example); Part 7 derives the full
curve.

---
