# Part 7 — The Width-Coupling Theory

This is the intellectual centre of the monograph. We derive, from pixel geometry and
nothing else, the law

$$\boxed{\;\text{Gap}(w)\;=\;\text{clDice}-\text{mIoU}\;\approx\;\frac{2\delta}{w+2\delta}\;}$$

with every algebraic step shown and every symbol defined. Then we read off the
failure/warning/safe zones and map exactly where the law breaks.

## 7.1 The original observation

Across four data sources we saw the same pattern: a model would *clearly find* a thin
structure (you could see the line in the prediction; centerline/tolerance metrics were
high) yet mIoU reported a mediocre number. Tabulating the gap against structure width:

```
   Dataset              measured width (px)   Gap = clDice − mIoU
   Synthetic markings        2.0 (GT)              +0.65
   Massachusetts Roads       4.31                  +0.25
   LoveDA                    4.90                  +0.22
   UAVid                    16.24                  +0.02
```

The gap is large for thin structures and disappears for wide ones. The question:
*is there a precise functional form, and does it come from something fundamental?*

## 7.2 Symbols and assumptions (define everything)

| symbol | meaning | units |
|---|---|---|
| `w` | structure width (thickness of the line/road) | pixels |
| `L` | structure length (along its long axis) | pixels |
| `δ` | model's per-side boundary-localisation error | pixels |
| `A` | structure area `= w·L` | pixels² |
| `G` | ground-truth foreground pixel set | — |
| `P` | predicted foreground pixel set | — |

**Assumptions (and why each is reasonable):**

1. **The structure is detected.** `P` covers `G`'s location — the model found the
   line. (If not, this is a *detection* failure, a different regime; Sec. 7.7.)
2. **The error is at the boundary.** The model places the structure's *boundary* off
   by about `δ` pixels per side — it slightly over- or under-estimates the width or
   shifts it. This is the dominant real error for detected thin structures (edge
   localisation is sub-pixel-to-one-pixel hard).
3. **`δ` is roughly constant in pixels**, set by the model/output resolution, *not*
   by the structure's width. A model has ~1 px edge error whether the line is 2 px or
   20 px wide.
4. **Long thin structure:** `L ≫ w`, so the two long sides dominate the perimeter and
   the short ends are negligible.

## 7.3 Step 1 — IoU of a detected, boundary-perturbed structure

Take over-segmentation (the argument is symmetric for under-segmentation). The
prediction is the GT structure widened by `δ` on each side: predicted width `w + 2δ`.

**Intersection.** The GT lies entirely inside the prediction, so
$$|P\cap G| = |G| = w\,L.$$

**Union.** The union is the (larger) prediction:
$$|P\cup G| = |P| = (w+2\delta)\,L.$$

**IoU.** By definition,
$$\text{IoU} = \frac{|P\cap G|}{|P\cup G|} = \frac{w\,L}{(w+2\delta)\,L}.$$
The lengths cancel:
$$\boxed{\;\text{IoU} \approx \dfrac{w}{w+2\delta}\;}$$

Pause on what this says. IoU is **not** a measure of "did we find it"; it is the ratio
of true width to (true + error) width. A fixed boundary error `2δ` shrinks IoU by an
amount that depends entirely on how `2δ` compares to `w`.

*Sanity numbers (δ = 1):*
- `w = 2`: IoU = 2/4 = **0.50**
- `w = 4`: IoU = 4/6 = **0.67**
- `w = 20`: IoU = 20/22 = **0.91**
- `w = 100`: IoU = 100/102 = **0.98**

(The general under/over case with per-side error gives `IoU = w/(w+2δ)` for
over-seg and `IoU = (w−2δ)/w` for under-seg; both behave as `1 − O(δ/w)`. We use the
over-seg form as the representative; the controlled experiment averages real cases and
matches.)

## 7.4 Step 2 — clDice is (nearly) width-independent

clDice compares **skeletons** (Sec. 3.12.5). The skeleton of a width-`w` straight or
gently-curved structure is its central 1-px curve. Crucial fact: **dilating or eroding
a structure by a uniform amount does not move its medial axis.** A 4-px line and the
same line widened to 6 px share the identical centerline.

Therefore, for the detected-and-boundary-perturbed prediction:
- the predicted skeleton `S_P` is the same central curve, which lies inside `G` →
  `T_prec = |S_P ∩ G|/|S_P| ≈ 1`;
- the GT skeleton `S_G` lies inside the (containing) prediction `P` →
  `T_sens = |S_G ∩ P|/|S_G| ≈ 1`.

Hence
$$\text{clDice} = \frac{2T_\text{prec}T_\text{sens}}{T_\text{prec}+T_\text{sens}} \approx \frac{2\cdot1\cdot1}{1+1} = 1.$$
$$\boxed{\;\text{clDice} \approx 1\quad\text{(width-independent, for detected structures)}\;}$$

*(Caveat at `w=1`: a 1-px structure's skeleton is degenerate and clDice dips slightly
below 1 — the law holds for `w ≥ 2`; Sec. 7.7.)*

## 7.5 Step 3 — combine to get the law

Subtract:
$$\text{Gap}(w) = \text{clDice} - \text{IoU} \approx 1 - \frac{w}{w+2\delta}.$$

Put over a common denominator:
$$1 - \frac{w}{w+2\delta} = \frac{(w+2\delta) - w}{w+2\delta} = \frac{2\delta}{w+2\delta}.$$

$$\boxed{\;\text{Gap}(w) \approx \dfrac{2\delta}{w+2\delta}\;}$$

That is the entire law, derived from two facts: IoU is an *area ratio* that pays the
fixed boundary rim, and clDice is a *centerline* metric blind to that rim.

### 7.5.1 A more revealing form
Divide numerator and denominator by `2δ`:
$$\text{Gap}(w) = \frac{1}{\,1 + \dfrac{w}{2\delta}\,}.$$
The gap depends **only on the dimensionless ratio `w/(2δ)`** — width measured in units
of the boundary error. This is why the law is **resolution-invariant**: rescale the
image and both `w` and `δ` scale together, leaving the ratio — and the gap —
unchanged (confirmed empirically, Part 8/9).

## 7.6 Reading the curve: limits, crossover, zones

**Limits.**
- As `w → 0`: `Gap → 2δ/2δ = 1`. Maximum disagreement — mIoU says ~0 while clDice
  says ~1.
- As `w → ∞`: `Gap → 0`. The metrics agree; mIoU is trustworthy.

**Crossover.** Gap = 0.5 when `2δ = w`, i.e. `w = 2δ ≈ 2 px` (for δ≈1). At the
structure width equal to twice the boundary error, the metrics are at maximal
*half*-disagreement.

**Visual example (δ = 1, the worked 3-px case).**
```
   GT  (w=3, 100px long, area 300)         Prediction (over by 1px/side, w=5, area 500)
   ███                                      ░█████░      ░ = 1px boundary rim
   ███   skeleton = central 1px curve ───►  ░█████░      skeleton UNCHANGED (central curve)
   ███                                      ░█████░
   IoU = 300/500 = 0.60     clDice ≈ 1.0     Gap = 0.40   (law: 2/(3+2)=0.40 ✓)
```
The law predicts `2/(3+2) = 0.40`; the geometry gives exactly 0.40. The model found
the line perfectly; mIoU's 0.60 is *entirely* the boundary rim.

**The three operational zones** (from `reports/failure_thresholds.md`):

```
   width band     Gap        zone        meaning
   ----------------------------------------------------------------
   w < 5 px       > 0.20     FAILURE     mIoU misleading >20%; markings live here
   5–25 px        0.05–0.20  WARNING     interpret mIoU with care; report clDice too
   w > 25 px      < 0.05     SAFE        mIoU agrees with clDice; trustworthy
```

Because the zones are set by the ratio `w/δ`, the thresholds scale with the model's
boundary error: roughly `w_fail ≈ 8δ` (Gap≈0.2) and `w_safe ≈ 38δ` (Gap≈0.05). A
better-localised model (smaller δ) shrinks the failure zone.

## 7.7 When the law breaks — and why (be honest about scope)

The derivation made specific assumptions; violate them and the law changes. Knowing
*where it breaks* is part of knowing the law.

1. **Topology errors (detection failure).** If the prediction *breaks* the structure
   (gaps, missed segments) rather than merely mis-placing its boundary, then `S_G ⊄ P`
   and `T_sens` drops — **clDice falls**. Now both metrics agree the prediction is
   bad, and the gap is small and width-*independent*. Controlled evidence: the `gaps`
   degradation gives Gap ≈ 0.03 at both w=2 and w=20. *This is not a failure of the
   law — it is its precondition.* The law describes *detected* structures; when
   detection fails, there is correctly no under-reporting to explain.

2. **Sub-pixel structures (`w = 1`).** The skeleton of a 1-px structure is degenerate;
   clDice dips (≈0.88, not 1.0). The law holds for `w ≥ 2`.

3. **Very large boundary errors (`δ` comparable to `w`).** If the model's localisation
   is so poor that `δ ≳ w`, the "small rim" picture breaks; under-segmentation can
   erase the structure (`w − 2δ ≤ 0`), at which point it is again a *detection*
   failure (case 1).

4. **Non-area / non-centerline metrics.** The law is specifically about *area-overlap*
   (IoU/Dice) versus *centerline* (clDice). It says nothing about, e.g., mIoU vs Dice
   (both area metrics — they track together).

5. **Texture/curvature extremes.** Very high curvature or branching changes the
   skeleton's stability; the *form* survives but the effective `δ` and clDice baseline
   shift slightly (the synthetic outlier in Fig. A reflects a different error regime,
   not a different law).

## 7.8 Why this is a *law*, conservatively stated

It is **derived** (one parameter `δ`), **quantitative**, **falsifiable** (predicts
specific gaps), **confirmed out-of-sample** (3 real datasets on a curve fixed by
controlled geometry), and **robust** (survives 10 attacks; resolution-invariant). It
is **not** a universal "law of segmentation" — it is the precise law of *area-vs-
centerline metric disagreement for detected thin structures under boundary error*. Its
contribution is to make a folk observation **mechanistic, predictive, and bounded**.
(Full classification: `reports/law_assessment.md`.)

## 7.9 What the law buys you (practical payload)

1. **A go/no-go rule for trusting mIoU:** if your structures are narrower than ~5× the
   model's boundary error, mIoU is misleading — report clDice/TolIoU.
2. **A predictor:** measure a model's `δ` once, and you can predict its mIoU
   under-report for any structure width via `2δ/(w+2δ)`.
3. **A design principle:** to make mIoU trustworthy, either work at higher resolution
   (raise `w` in pixels) or improve boundary localisation (lower `δ`) — both raise
   `w/δ`.

---
