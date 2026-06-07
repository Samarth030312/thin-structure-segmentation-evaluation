# Part 13 — Personal Mastery Checklist

100 questions, ordered easy → medium → hard → expert. If you can answer all without
notes, you understand the project. An answer key follows.

## 13.1 Easy (1–25)

1. What task is semantic segmentation?
2. What does mIoU stand for?
3. Write the IoU formula.
4. Write the Dice formula.
5. What is the foreground class in this project (binary case)?
6. Roughly what fraction of RLMD pixels are markings?
7. What is the class-imbalance ratio in RLMD?
8. What is a skeleton of a shape?
9. What does clDice measure?
10. State the width-coupling law.
11. What is `w` in the law?
12. What is `δ` in the law?
13. What is `Gap`?
14. As `w → 0`, what does Gap approach?
15. As `w → ∞`, what does Gap approach?
16. Which metric "lies" for thin structures?
17. Which metric stays high for detected thin structures?
18. Name the primary architecture used.
19. Why pre-train encoders on ImageNet?
20. What is a skip connection?
21. What is cross-entropy loss for?
22. What is the failure-zone width threshold?
23. Name the five datasets.
24. Which dataset is genuine UAV?
25. Which real dataset best confirmed the law?

## 13.2 Medium (26–50)

26. Derive `IoU = w/(w+2δ)` for over-segmentation.
27. Why is clDice width-independent?
28. Combine to get `Gap = 2δ/(w+2δ)`.
29. Why is the law resolution-invariant?
30. What is the crossover width and its Gap value?
31. Why did UAVid not show the effect?
32. Why is UAVid's negative actually supporting?
33. What does the controlled experiment vary, and what does it hold fixed?
34. Why use no model in the controlled experiment?
35. Which functional forms were rejected in the fit, and which won?
36. What was the controlled-fit `R²`?
37. What is `δ` numerically (controlled fit)?
38. Give MassRoads' mIoU, clDice, and gap (3-seed means).
39. Why was multi-seed evaluation necessary (give the CoRe example)?
40. What is a bootstrap confidence interval?
41. What is Tolerance-IoU and why does it stay high?
42. What is Boundary-IoU and why does it *drop* for thin structures?
43. What is the Euclidean distance transform used for here?
44. Why did fp16 (AMP) fail?
45. Why does U-Net++ use more memory than U-Net?
46. What is ASPP and which architecture uses it?
47. What is self-attention's formula?
48. What is the CoRe loss composed of?
49. Why did CoRe fail?
50. What is the safe-zone width threshold and its Gap?

## 13.3 Hard (51–75)

51. Why does a fixed boundary error affect thin structures more (boundary-fraction
    argument)?
52. Show the law depends only on the ratio `w/(2δ)`.
53. Why do FWIoU and PixelAcc avoid the flooding trap but fail the foreground test?
54. In the mis-ranking result, which loss floods and what is its PixelAcc?
55. Why does *all-class* mIoU failing matter (vs only foreground-mean)?
56. What does the `gaps` degradation show, and why is it not a counterexample?
57. Why does clDice correctly drop for topology errors?
58. What is the difference between the width-coupling law and the mis-ranking result?
59. Why is the synthetic point off the curve in Figure A?
60. How were real datasets placed on the width axis (no controlled width)?
61. What does `w_fail ≈ 8δ` mean?
62. Why is a loss differentiable but a metric need not be?
63. What is soft skeletonisation and why is it memory-hungry?
64. Why is the controlled study reproducible on CPU?
65. What is the receptive-field tension in segmentation architectures?
66. Why is the law architecture-independent?
67. How would you measure `δ` for a given model?
68. Why is "the law is just IoU's definition" both true and not a refutation?
69. What three tests define the metric-sensitivity (mis-ranking) analysis?
70. Why is gradient accumulation used?
71. What does best-by-mIoU checkpointing do, and is it a problem given the thesis?
72. Why can a model with high clDice have low IoU but not vice-versa (for detected
    structures)?
73. What is the difference between Dice and IoU sensitivity?
74. What would falsify the law?
75. Why is SkyScapes the ideal but unavailable dataset?

## 13.4 Expert (76–100)

76. Derive the under-segmentation IoU `(w−2δ)/w` and show it is `1 − O(δ/w)`.
77. At what `δ/w` does under-segmentation erase the structure, and what regime does it
    enter?
78. Why does the power-law fit (`w^−0.61`) beat the inverse form on AIC, yet we prefer
    the inverse form?
79. Construct a concrete prediction (mask) that is in the safe zone yet a detection
    failure — what do mIoU and clDice each say?
80. Explain why resolution-invariance distinguishes "joint rescaling" from "real
    low-res inference," and what each does to the gap.
81. Derive the relative under-report `(clDice − IoU)/clDice` and its limit as `w → 0`.
82. Why is the boundary-fraction `≈ 2/w` and how does it connect to `δ`?
83. Propose a width-normalised IoU using an estimated `δ̂` and show it recovers ≈1 for
    a detected structure.
84. Why might curvature/branching shift the effective `δ` (Figure A synthetic outlier)?
85. Explain how a confusion matrix yields every mIoU variant and why that enabled the
    mis-ranking analysis.
86. Why is clDice's `w=1` degeneracy a scope limit rather than a flaw?
87. Give the AIC intuition for preferring a 1-parameter inverse over a 2-parameter
    rational at near-equal `R²`.
88. How would per-architecture `δ` turn the law into a model-selection tool?
89. Why does Tolerance-IoU's `τ` need to be tied to `δ` for a principled corrected
    metric?
90. Explain the epistemic value of the UAVid negative for the paper's credibility.
91. Why is out-of-sample dataset agreement stronger evidence than a within-dataset fit?
92. What is the difference between "a benchmark artifact" and "a geometric law," and
    which controls rule out the former?
93. Why does the mis-ranking result not generalise to binary tasks?
94. How does the law inform the choice between higher-resolution inference and better
    boundary localisation?
95. Why is reporting the CoRe null result scientifically valuable, not a weakness?
96. Derive the failure threshold width for `Gap = 0.2` in terms of `δ`.
97. Explain why two models with identical mIoU can have very different clDice, with a
    sketch.
98. What is the honest ceiling of publishability and exactly why (per the verdict)?
99. Design the single experiment that would most raise the contribution, and justify.
100. State, in one sentence each, the project's strongest result, weakest aspect, and
    most important next step.

## 13.5 Answer key (concise)

**Easy.** 1 per-pixel classification. 2 mean Intersection-over-Union. 3
`|P∩G|/|P∪G|`. 4 `2|P∩G|/(|P|+|G|)`. 5 marking/road (label 1). 6 <2%. 7 609:1. 8 its
1-px medial axis. 9 centerline (topology) overlap. 10 `Gap=clDice−mIoU≈2δ/(w+2δ)`. 11
structure width (px). 12 per-side boundary error (px). 13 `clDice−mIoU`. 14 1. 15 0.
16 mIoU. 17 clDice (and TolIoU). 18 U-Net (ResNet-34). 19 free features, few labels.
20 encoder→decoder high-res link. 21 per-pixel classification, punish confident wrong.
22 ~5 px. 23 synthetic, RLMD, LoveDA, MassRoads, UAVid. 24 UAVid. 25 Massachusetts
Roads.

**Medium.** 26 inter=`wL`, union=`(w+2δ)L`, ratio `w/(w+2δ)`. 27 skeleton invariant to
uniform boundary change. 28 `1−w/(w+2δ)=2δ/(w+2δ)`. 29 depends on `w/(2δ)`; rescaling
scales both. 30 `w=2δ` (~2 px), Gap 0.5. 31 roads 12–35 px (wide). 32 wide = safe
zone, law predicts ~0. 33 varies width, fixes all else. 34 rule out model/data
artifacts. 35 rejected linear/exp/log; inverse-family (power/rational/inverse) won. 36
0.98. 37 0.67. 38 0.49 / 0.76 / +0.27. 39 CoRe was "significant" on seed 42, vanished
over 3 seeds. 40 resample per-image scores → 95% interval, no normality. 41 IoU within
`τ` px; forgives boundary error. 42 boundary band = whole thin object. 43 measure local
width `2×EDT`. 44 soft-skeleton gradients underflow → NaN. 45 dense nested skip grid
holds many maps. 46 atrous spatial pyramid pooling; DeepLabV3+. 47
`softmax(QKᵀ/√d)V`. 48 CE + Dice + soft-clDice. 49 no reliable multi-seed gain. 50
~25 px, Gap 0.05.

**Hard.** 51 boundary fraction `≈2/w` → 100% at w=2. 52 divide by 2δ:
`1/(1+w/2δ)`. 53 dominated by background → can't separate fg quality. 54 Tversky,
PixelAcc ≈0.009. 55 refutes "foreground-averaging artifact." 56 clDice drops,
width-independent → detection failure, the law's precondition. 57 broken skeleton →
`T_sens` falls. 58 width law = geometric/binary; mis-ranking = imbalance/multi-class.
59 width-shift error = larger `δ`. 60 `2×EDT` mean width per image. 61 failure
threshold scales with `δ`. 62 loss needs gradients; metric reported only. 63 iterated
pooling retains tensors for autograd. 64 torch-free numpy/scipy metrics. 65 context
(downsample) vs resolution (detail). 66 needs only a `δ`; form independent of model.
67 fit `2δ/(w+2δ)` to its width-stratified gap. 68 yes it's the definition — made
explicit/parameterised/validated is the contribution. 69 top-floods? best-detector-#1?
foreground-sensitive? 70 simulate larger batch on 4 GB. 71 picks best-mIoU
checkpoint; acceptable since the law uses converged models and the *claim* is about
the metric, not the selection. 72 boundary error lowers IoU but not centerline overlap.
73 IoU stricter (penalises union). 74 a detected thin structure (clDice≥0.9) whose gap
doesn't fall with width. 75 aerial thin *markings*, the exact target; licence-gated.

**Expert.** 76 inter `(w−2δ)L`, union `wL` → `(w−2δ)/w = 1−2δ/w`. 77 `δ ≥ w/2` erases
it → detection-failure regime. 78 indistinguishable over range; inverse has the
mechanism + one parameter. 79 a broken/gappy wide road: mIoU may be moderate, clDice
low → both flag it; in safe zone the *boundary* gap is ~0 but topology failure shows in
clDice. 80 joint rescale preserves `w/δ` (gap fixed); real low-res keeps δ≈1 while w
shrinks → gap rises. 81 `(clDice−IoU)/clDice ≈ 1−w/(w+2δ)`; →1 as w→0. 82 perimeter
`≈2L`, area `wL` → fraction `2/w`; the rim that δ perturbs. 83 report
`IoU·(w+2δ̂)/w ≈ 1`. 84 skeleton stability/clDice baseline shift. 85 confusion matrix →
all per-class IoUs → any averaging variant. 86 1-px skeleton degenerate; law stated
w≥2. 87 fewer parameters, near-equal fit → lower AIC preference + mechanism. 88 quote
per-model failure thresholds in advance. 89 `τ` must match the error scale δ to be
principled, not arbitrary. 90 a documented contradiction-turned-confirmation signals
rigor, not cherry-picking. 91 the curve was fixed by controlled data, not the
datasets → genuine prediction. 92 artifact = data/impl-specific; controls = controlled
geometry + reference metrics + tests rule it out. 93 binary has no extreme multi-class
imbalance to exploit. 94 both raise `w/δ`: higher res raises w, better localisation
lowers δ. 95 reporting a null prevents a false-positive in the literature; signals
honesty. 96 `2δ/(w+2δ)=0.2 → w=8δ`. 97 same area overlap, different connectivity →
identical mIoU, different clDice (sketch: one continuous vs one dashed line). 98 ~78/100
— bounded underlying novelty + no aerial markings + compute. 99 the width-corrected
metric (cheap, turns critique into method) or SkyScapes (closes the data gap). 100
strongest: derived+validated law with thresholds; weakest: no aerial markings / bounded
novelty; next: build the width-corrected metric.

---

*End of monograph. You now have, in one document, everything needed to reproduce,
defend, teach, and extend the project.*
