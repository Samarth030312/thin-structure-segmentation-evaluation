# Professor Defense Guide (Phase 6)

50 hardest questions (as Prof. Amol Gedam / Prof. Sanjay Chaudhary), answered with
repository evidence only. Where evidence is absent: "NOT VERIFIED".

## Mathematics & geometry
1. **Derive `IoU=w/(w+2δ)`.** Over-seg: intersection `wL`, union `(w+2δ)L`, ratio after
   `L` cancels (`reports/first_principles_width_analysis.md` §7.3).
2. **Why `clDice≈1` independent of width?** Skeleton is invariant to uniform boundary
   change (`thin_structure.py:cl_dice` skeletonises both masks).
3. **Combine to the law.** `1−w/(w+2δ)=2δ/(w+2δ)` (`width_coupling_theory.md`).
4. **Is the law dimensionless?** Yes: `1/(1+w/2δ)` depends only on `w/δ`
   (`first_principles_width_analysis.md` §7.5.1).
5. **What is δ numerically?** 0.67 (controlled fit, `reports/controlled/law_fit.json`).
6. **Under-segmentation form?** `(w−2δ)/w=1−2δ/w` — same `1−O(δ/w)` order.
7. **When does the structure vanish?** `δ≥w/2` → detection-failure regime (out of scope).
8. **Crossover width?** `w=2δ`, Gap=0.5.
9. **Why inverse-width not exponential?** Fit: linear R²=0.626, exp 0.892, inverse-family
   ≥0.977 (`fit_width_law.py` output, `width_coupling_theory.md` §1).
10. **Power (w^−0.61) beat the inverse on AIC — why prefer inverse?** Indistinguishable
   over range; inverse has the mechanism + 1 parameter (`width_coupling_theory.md` §1).

## Statistics
11. **How many seeds?** 3 (42/123/999) for the validation runs.
12. **CIs method?** Bootstrap (`src/uavroadmark/metrics/stats.py`).
13. **CoRe vs baseline CI?** Prose says Δ≈−0.001, [−0.18,0.18]; **but
    `paper_tables/table7_multiseed.md` shows `ci95=nan`** → the printed CI is **NOT
    VERIFIED from the table**; only the means (0.4045 vs 0.4056) support the tie.
14. **n=3 — adequate power?** For the tight width-study CIs yes (mIoU 0.351±0.007); for
    the CoRe comparison the variance is large (core clDice std 0.141) — underpowered;
    disclosed.
15. **Multiple-comparison correction?** NOT VERIFIED — not applied; the loss-rank
    Spearman is noted non-significant in the paper.
16. **Is the controlled R²=0.98 meaningful or circular?** Partly circular — δ is injected
    then recovered; disclosed (`final_release_audit.md` M1). Independent test = real data.
17. **Real-data n?** 4 datasets; 3 used to test the curve. Small; disclosed.
18. **Width measured how on real data?** `2×distance_transform_edt`, mean per image
    (`run_width_validation.py`).
19. **Are the real points hand-placed?** No longer — `measured_mean_width_px` loaded from
    JSONs (`FIGURE_PROVENANCE_REPORT.md`).
20. **UAVid residual −0.06 — does it break the fit?** No; within tolerance and in the safe
    zone (`width_coupling_theory.md` §2).

## Segmentation / metrics / topology
21. **Why is mIoU bad for thin structures?** Area-ratio pays a fixed boundary rim;
    boundary fraction ≈2/w (`02_segmentation` / monograph).
22. **Why clDice over Boundary-IoU?** Boundary-IoU also drops (it is an area metric on a
    band); clDice/TolIoU are width-stable (`03b_losses_metrics`).
23. **clDice degeneracy?** At w=1 the skeleton is degenerate (clDice 0.88); law stated
    w≥2 (`07_theory` §7.7).
24. **Soft-skeleton differentiability?** `losses/topology.py:SoftSkeletonize` (iterated
    soft-open); memory-heavy → batch 2 + grad-accum.
25. **Does the law hold for topology errors?** No — clDice correctly drops, gap≈0
    width-independent (`controlled_robustness_study.md`); precondition, not failure.
26. **mIoU all-class vs fg — both fail?** Yes (`metric_sensitivity_analysis.md`),
    refuting the fg-averaging-artifact rebuttal.
27. **Is clDice prior work?** Yes — Shit CVPR'21, cited `\bibitem{cldice}`.
28. **Boundary-IoU prior work?** Cheng CVPR'21, cited `\bibitem{biou}`.
29. **What is your metric contribution then?** Not the metrics — the *law* relating their
    disagreement to width, plus thresholds.
30. **TolIoU τ value?** τ=3 px (`thin_structure.py:tolerance_scores`).

## Novelty / assumptions / limitations
31. **Isn't the law just IoU's definition?** Essentially yes — made explicit,
    parameterised, thresholded, validated (`law_assessment.md`). Bounded novelty,
    disclosed.
32. **Strongest contribution?** Derived+validated law with failure thresholds (Fig A).
33. **Biggest limitation?** No aerial road-*markings*; SkyScapes gated
    (`reports/skyscapes_acquisition_attempt.md`).
34. **Is δ universal?** No — model-dependent; thresholds scale as `8δ`/`38δ`.
35. **Why thresholds 5/25 px?** δ=1 px convention; cutoffs Gap=0.2/0.05 are conventions
    (`failure_thresholds.md`) — illustrative, not constants.
36. **Why synthetic at all?** Only way to make width a controlled variable
    (`06_experimental_design`).
37. **Realism of synthetic?** Irrelevant for a geometry claim; real data confirms.
38. **UAVid contradicts you?** It confirms the safe-zone prediction (wide roads, gap≈0).
39. **Did CoRe work?** No — null result, reported (`table7`, prose).
40. **Cross-dataset evidence?** Confounded; excluded from claims (`FIGURE_PROVENANCE`).

## Engineering / reproducibility
41. **Why fp32 not AMP?** Soft-skeleton gradients underflow → NaN (engineering notes).
42. **Why batch 2 for CoRe?** Soft-skeleton autograd memory on 4 GB.
43. **Can I reproduce the law on CPU?** Yes — 3 scripts, **after** adding the missing
    `scikit-image`/`scipy` deps (`REPRODUCIBILITY_AUDIT.md` — current blocker).
44. **Tests?** 62 pass in-env; would fail to import on a clean env missing skimage.
45. **Are checkpoints shipped?** No — git-ignored.
46. **Are real datasets shipped?** No — ingestion scripts fetch from public mirrors
    (authorization NOT VERIFIED — `LICENSING_AUDIT.md`).
47. **Hardware for the numbers?** 4 GB GPU; timings machine-specific (`table4` NOT
    VERIFIED across hardware).
48. **Determinism?** Seeded (`utils/seed.py`); metrics torch-free/deterministic.
49. **Is the figure pipeline reproducible?** Yes — `make_law_figures.py` loads JSONs
    (no manual constants) post-reconstruction.
50. **What would change your mind about the law?** A detected thin structure (clDice≥0.9)
    whose gap does not fall with width — none found across the datasets tested.

## Honest residual weaknesses a professor will still raise
- The controlled validation is **partly circular** (16).
- The CoRe **CI is `nan` in the table** (13).
- **scikit-image** is an **undeclared dependency** (43).
- Novelty is **bounded** (31). All are disclosed in the audit reports.
