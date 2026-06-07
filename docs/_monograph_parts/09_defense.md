# Part 9 — Reviewer Defense Guide

100 questions you must be able to answer: 50 a professor (conceptual, teaching) and 50
a reviewer (critical, adversarial) would ask, with concise defensible answers,
counter-arguments, and the honest limitations.

## 9.1 Fifty professor questions (conceptual)

**P1. What is semantic segmentation?** Per-pixel classification: label every pixel
with a class, producing an `H×W` label map.

**P2. Why not use detection boxes for lane lines?** A box cannot represent a thin,
curved, diagonal structure; most of the box is not the line. Shape matters for lane
keeping/HD-maps.

**P3. What is IoU?** `|P∩G|/|P∪G|` — intersection over union of predicted and true
foreground; the area-overlap quality.

**P4. What is mIoU?** Per-class IoU averaged over classes (foreground-mean, all-class,
or frequency-weighted variants).

**P5. What is Dice and how does it relate to IoU?** `2|P∩G|/(|P|+|G|)`;
`IoU = Dice/(2−Dice)` — monotonically related, Dice is more lenient.

**P6. What is clDice?** Harmonic mean of topology precision and sensitivity computed on
*skeletons*; measures centerline overlap, blind to width.

**P7. What is a skeleton?** The 1-px medial axis of a shape — its central spine,
equidistant from the boundaries.

**P8. Why is clDice width-independent?** Uniform boundary changes do not move the
medial axis, so the skeleton (and its overlap) is unchanged.

**P9. State the width-coupling law.** `Gap = clDice − mIoU ≈ 2δ/(w+2δ)`.

**P10. Derive IoU = w/(w+2δ).** Over-seg: intersection `wL`, union `(w+2δ)L`; ratio
`w/(w+2δ)` after `L` cancels.

**P11. What is δ?** The model's per-side boundary-localisation error in pixels (~1 px).

**P12. Why does Gap → 1 as w → 0?** A fixed rim `2δ` overwhelms a vanishing width;
IoU → 0 while clDice → 1.

**P13. Why does Gap → 0 as w → ∞?** The rim is negligible relative to a large area;
IoU → 1, agreeing with clDice.

**P14. What is the crossover width?** `w = 2δ` (~2 px), where Gap = 0.5.

**P15. Why is the law resolution-invariant?** It depends only on the ratio `w/(2δ)`;
rescaling scales both, leaving the ratio fixed.

**P16. What is the failure threshold?** `w ≈ 5 px` (Gap > 0.2); below it mIoU is
misleading.

**P17. Why are road markings hard?** Tiny area (<2%), extreme imbalance (609:1),
thinness (boundary = whole object), appearance variation.

**P18. What is the boundary fraction of a thin structure?** ≈ `2/w`; for `w=2` it is
100%.

**P19. What is cross-entropy loss?** `−log p_t` after softmax; punishes confident
wrong predictions.

**P20. Why does CE struggle on thin structures?** Averaged over 98% background, it is
dominated by easy background pixels.

**P21. What does Dice loss add?** Region overlap focus that counteracts class
imbalance.

**P22. What is Tversky loss?** Dice generalised with FP/FN weights `α,β`; raising `β`
punishes misses.

**P23. What is Focal loss?** CE weighted by `(1−p_t)^γ` to focus on hard examples.

**P24. What is a convolution?** A sliding weighted window (kernel) summed over a local
patch — a shared-weight, local linear operator.

**P25. What is a receptive field?** The input region influencing one output pixel;
grows with depth/striding.

**P26. What is a skip connection?** A link carrying high-resolution encoder features to
the decoder for precise boundaries.

**P27. Why is U-Net good for thin structures?** Concatenated skips inject fine detail,
enabling precise boundary placement.

**P28. What does U-Net++ change?** Dense nested skips to bridge the encoder–decoder
semantic gap; more memory.

**P29. What is ASPP (DeepLab)?** Parallel dilated convs at multiple rates for
multi-scale context without downsampling.

**P30. What is self-attention (SegFormer)?** Each token attends to all others via
`softmax(QKᵀ/√d)V`, giving global context.

**P31. Why pre-train on ImageNet?** Free edge/texture detectors; essential with few
labelled images.

**P32. What is gradient descent?** `θ ← θ − η∇L`, stepping downhill on the loss.

**P33. What is backpropagation?** The chain rule applied right-to-left, reusing
sub-results — one backward pass.

**P34. Why fp32 not fp16 here?** Soft-skeleton gradients underflow in fp16 → NaN
divergence; fp32 is stable.

**P35. What is the Euclidean distance transform used for?** Measuring local structure
width (`2×EDT`) on real masks.

**P36. Why multi-seed?** Single-seed deep-learning results can be noise (CoRe looked
significant on one seed, vanished over three).

**P37. What is a bootstrap CI?** Resampling per-image scores to estimate a metric's
sampling distribution and 95% interval without normality assumptions.

**P38. Why is the synthetic experiment essential?** It makes width a controlled
variable, isolating causation.

**P39. Why does the controlled study use no model?** To rule out model/dataset
artifacts — pure geometry reproduces the law.

**P40. What is TolIoU?** IoU that forgives errors within `τ` px; stays high for
detected thin structures.

**P41. What is Boundary-IoU?** IoU over a boundary band; diagnoses boundary
sensitivity (also drops for thin structures).

**P42. Which metric should you report for markings?** clDice and/or TolIoU alongside
mIoU — never mIoU alone.

**P43. What is the difference between a loss and a metric?** Loss is optimised (must be
differentiable); metric is reported (need not be).

**P44. What is soft skeletonisation?** Differentiable morphology approximating the
skeleton, enabling a clDice *loss* term.

**P45. Why did CoRe fail?** No reliable multi-seed gain; soft-clDice loss did not
improve detection over CE+Dice.

**P46. What does the UAVid negative teach?** Wide structures are in the safe zone; the
law predicts (correctly) no gap there.

**P47. Is the law universal?** No — it is the area-vs-centerline disagreement for
*detected* thin structures under boundary error.

**P48. When does clDice correctly drop?** When the prediction breaks topology
(gaps/misses) — a detection failure.

**P49. What is the practical δ-rule?** mIoU is misleading below ~5× the model's
boundary error.

**P50. One-sentence contribution?** A derived, validated geometric law for when and by
how much mIoU under-reports thin structures, with actionable thresholds.

## 9.2 Fifty reviewer questions (adversarial)

**R1. Isn't "IoU is bad for thin things" already known?** Yes as folk wisdom; we
contribute the *derived functional form*, its validation, and thresholds — not the
qualitative observation.

**R2. Isn't the law just IoU's definition rewritten?** Essentially yes — and that is
the point: we make it explicit, parameterise it by δ, threshold it, and validate it
out-of-sample. That is a contribution, not a tautology.

**R3. Only four real datasets — too few to claim a law.** The law is fixed by the
*controlled* experiment (13 widths × 5 seeds); the datasets are out-of-sample checks,
not the fit. Three of four land within 0.06.

**R4. The synthetic point is off the curve — doesn't that falsify it?** No; it reflects
a larger error regime (width-shift), i.e. a different `δ`, not a different form. The
three boundary-error datasets fit.

**R5. clDice could be the wrong reference.** clDice is independently motivated (prior
work) and *correctly drops* for topology errors (shown). It is not tuned to produce the
gap.

**R6. Could this be a clDice implementation bug?** No — the numeric gap matches the
*analytic* derivation (R²=0.98), and the metrics pass 62 unit tests.

**R7. Resolution changes should break it.** Tested: gap is invariant under joint
rescaling because it depends on `w/δ`. This *confirms* rather than breaks it.

**R8. Annotation noise could explain it.** Tested (`boundary_noise`): gap persists,
weaker; the trend holds until noise breaks topology.

**R9. It's a class-imbalance effect.** No — the width law is per-structure and binary;
imbalance plays no role. The mis-ranking is a *separate*, clearly labelled result.

**R10. Skeletonisation artifacts drive it.** Only at `w=1` (degenerate); the law is
stated for `w ≥ 2`.

**R11. Crop size confounds it.** Width is a local (per-pixel EDT) property; cropping
changes field of view, not local width.

**R12. δ is model-dependent — so the law isn't universal.** The *form* is universal;
the *scale* (δ) is model-specific. We say so explicitly and give the dimensionless
form.

**R13. Your real models are under-trained.** The 25-class ones are; the *law* uses
converged synthetic (clDice 0.997) and converged binary models, so under-training
cannot explain it.

**R14. Compute is tiny (4 GB).** Yes; the law rests on controlled geometry and
converged binary models, which 4 GB supports. The broader benchmark is admittedly
small-scale.

**R15. No aerial markings — your target domain is missing.** True and stated;
SkyScapes is gated/unreachable (documented). We validate the *structural* claim on real
thin roads instead.

**R16. UAVid contradicts you.** It confirms the safe-zone prediction (wide roads, no
gap). We present it as supporting, not contradicting.

**R17. Power law fit beats your inverse form.** Marginally, and indistinguishable over
the range; we prefer the mechanistic inverse form and disclose the power fit.

**R18. Over-segmentation assumption is arbitrary.** Under-seg gives `(w−2δ)/w`, same
`1 − O(δ/w)` behaviour; the controlled study averages real degradations and matches.

**R19. Long-structure assumption (L≫w) may fail.** For markings/roads it holds; for
blobs the law does not apply (and they are not thin structures).

**R20. clDice vs TolIoU — which is the claim?** Either; both are width-stable. We lead
with clDice and report TolIoU as corroboration.

**R21. Is δ measurable?** Yes — fit `2δ/(w+2δ)` to a model's width-stratified gap, or
estimate edge error directly. δ ≈ 0.67–1 px here.

**R22. Bootstrap CIs assume independence across images.** Standard caveat;
per-image resampling is the conventional choice and our CIs are tight.

**R23. Only U-Net used for real validation.** The law is architecture-independent (it
needs only a δ); U-Net suffices to produce predictions. Breadth was compute-bounded.

**R24. The mis-ranking result uses extreme imbalance — cherry-picked.** It is scoped
explicitly to extreme multi-class imbalance; we do not generalise it to binary.

**R25. Synthetic data isn't realistic.** Irrelevant for a *geometry* claim; appearance
does not enter the derivation, and real datasets confirm it.

**R26. Could augmentations create the effect?** No — the controlled study uses none;
masks and degradations are deterministic geometry.

**R27. Does it hold for non-road thin structures?** The derivation is generic (vessels,
cracks) but we only validate roads/markings; we do not overclaim.

**R28. Is clDice expensive/unstable?** Skeletonisation has cost and a `w=1` edge case;
TolIoU is a cheaper stand-in. Both are reported.

**R29. The gap could come from label thickness mismatch in GT.** That *is* a width
effect and is consistent; we manipulate width directly to test it.

**R30. Why should a reviewer trust a 4-point dataset curve?** They shouldn't — they
should trust the 13-point controlled curve + derivation; the 4 points are corroboration.

**R31. Isn't TolIoU just hiding errors?** It forgives *localisation* within τ, which is
exactly the boundary error the law concerns; it does not forgive missed detections.

**R32. Boundary-IoU also drops — so topology metrics aren't special.** Boundary-IoU is
an *area* metric on a band; it drops *because* of the same effect. clDice/TolIoU are
the width-stable ones.

**R33. Does the law predict *direction* (over vs under-seg)?** It predicts magnitude;
sign of the boundary error doesn't change the gap's leading behaviour.

**R34. Reproducibility?** Three scripts (`run_controlled_robustness`, `fit_width_law`,
`make_law_figures`) regenerate everything; 62 tests pass.

**R35. Could a different reference metric (e.g. centerline-only) erase the gap?** Any
width-stable reference yields the gap; that is the point — area metrics are the
outliers.

**R36. Is the effect just low-resolution rendering?** No — it persists at every
resolution (invariant) and is derived analytically.

**R37. What about anti-aliased/soft labels?** The derivation uses hard masks; soft
labels shift `δ` slightly, not the form.

**R38. Multi-class mIoU mis-ranking — is clDice the only fix?** Among tested metrics,
yes (only one passing all three tests); we don't claim no other metric could.

**R39. Is the failure threshold (5 px) universal?** No — it scales with δ (`w_fail ≈
8δ`). 5 px assumes δ≈1.

**R40. Does training at higher resolution remove the problem?** Yes in pixels — higher
res raises `w`, lowering the gap. That is a stated implication.

**R41. The CoRe negative — did you tune it enough?** We report a fair comparison; we do
not claim CoRe *cannot* work, only that our version gave no reliable gain.

**R42. Statistical power with n=3 seeds?** Adequate for tight CIs here; more seeds
would tighten further; disclosed as a limitation.

**R43. Is this ITS-relevant or generic CV?** Both; the application is road markings
(ITS), the mechanism is generic.

**R44. Why not just always report clDice?** We recommend exactly that for thin
structures; the contribution is knowing *when* (the thresholds) and *why* (the law).

**R45. Does the law hold under domain shift?** It is geometric, not appearance-based,
so domain shift changes δ (model quality), not the form.

**R46. Could ensembling change δ?** Yes — better localisation lowers δ and shrinks the
gap; consistent with the law.

**R47. Are the datasets licence-clean for release?** Yes; ingestion scripts + sources
documented; large data git-ignored.

**R48. Isn't the whole thing negative (mIoU bad, CoRe bad, UAVid no effect)?** The
*positive* core is a derived, validated law with thresholds; the negatives bound and
strengthen it.

**R49. Top-venue worthiness?** Workshop/ITSC level honestly (≈70%/50%); not CVPR-main —
the underlying novelty is bounded. Stated in `FINAL_RESEARCH_VERDICT.md`.

**R50. What would change your mind?** A *detected* thin structure (clDice ≥ 0.9) whose
mIoU–clDice gap does not fall with width, or a real thin dataset far off the curve.
None was found.

---
