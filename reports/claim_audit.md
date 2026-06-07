# Claim Audit

> **Historical / superseded.** This document is from the project's initial benchmark-building phase. The project's actual contribution and current narrative is the **width-coupling law** for thin-structure evaluation metrics — see `reports/width_coupling_theory.md` and `paper_package/final_ieee_paper.pdf`. The "target UAV dataset" referenced below was an aspirational road-marking set that was **never acquired**; the experiments actually used a synthetic generator and the public datasets RLMD, LoveDA, Massachusetts Roads, and UAVid. See `reports/repository_integrity_report.md`.


> Every non-trivial claim in the repository, with its supporting evidence (file +
> result) or a note that it was removed/softened. Claims without evidence are not
> permitted.

| # | Claim | Evidence | Status |
|---|---|---|---|
| C1 | mIoU under-measures thin markings | width study: train@4px, test@2px → mIoU 0.35 but TolIoU 0.97, clDice 1.0 (`width_study.json`, fig1) | ✅ supported (synthetic, controlled) |
| C2 | mIoU **mis-ranks** models/losses on real data | RLMD clean 6-loss ablation: rank-by-mIoU is ~inverse of rank-by-clDice (ρ=−0.31); Tversky/Dice top mIoU but PixelAcc 0.008 (`loss_ablation_clean.md`, fig2) | ✅ supported (real) |
| C3 | Recall-only losses (Tversky/Dice) flood the frame | PixelAcc 0.008–0.009, clRecall 1.0, clDice <0.09 on RLMD (`loss_ablation_clean.md`) | ✅ supported (real) |
| C4 | CE/Focal collapse to background under extreme imbalance | mIoU ~0, PixelAcc 0.98, clDice 0.06–0.09 (`loss_ablation_clean.md`) | ✅ supported (real) |
| C5 | CE+Dice and CoRe are **statistically tied** on real data (multi-seed) | 3-seed clDice 0.405 vs 0.406, Δ=−0.001 CI[−0.18,0.18] (`multiseed_results.md`) | ✅ supported; **single-seed "CE+Dice wins" retracted** |
| C6 | Tversky/Dice (recall-only) are the **worst** real losses | PixelAcc 0.008–0.009, clDice <0.09 (`loss_ablation_clean.md`) | ✅ supported (real) |
| C7 | CoRe ≥ CE+Dice on *synthetic* | synthetic ablation: CoRe mIoU 0.945 ≥ 0.938, clDice 0.999 (`loss_function_analysis.md`) | ✅ supported (synthetic only — scope stated) |
| C8 | U-Net++/U-Net (skip decoders) best for thin structures | arch sweep: BoundaryIoU 0.987/0.986 vs PSPNet 0.62 (`architecture_analysis.md`, fig?) | ✅ supported (synthetic) |
| C9 | DeepLabV3+↔SegFormer swap rank between mIoU and BoundaryIoU | arch table (`architecture_analysis.md`) | ✅ supported (synthetic) |
| C10 | SegFormer-B0 is the efficiency winner | 3.7 M params, 9.9 GFLOPs, 34.6 GPU FPS (`leaderboard_performance.csv`, fig3) | ✅ supported (measured) |
| C11 | ONNX Runtime 1.47× faster than PyTorch (CPU), bit-identical | parity 8.9e-8, 170→116 ms (`deployment_report.md`) | ✅ supported (measured) |
| C12 | Training is GPU-compute-bound on this HW | dataloader 72 imgs/s vs ~5 imgs/s training; conv=85% CUDA time (`performance_profiling.md`) | ✅ supported (measured) |
| C13 | Real road markings are severely imbalanced | RLMD EDA: 98% background, 609:1 fg ratio (`real_data_results.md`) | ✅ supported (measured) |
| C14 | No public India-UAV-marking dataset exists | dataset survey of 14 candidates (`dataset_survey.md`) | ✅ supported (search-based; "to our knowledge") |
| C15 | Failure modes dominated by thin + shadow | failure taxonomy worst-50: 56% thin, 44% shadow (`failure_taxonomy.md`) | ✅ supported (real) |
| C16 | Foundation models (SAM) infeasible to *train* here | VRAM math: ViT-H 636 M params > 4 GB (`foundation_model_study.md`) | ✅ supported (analysis) |
| C17 | Cross-dataset RLMD↔LoveDA transfer | `cross_dataset_generalization.md` | ✅ supported (see C17b) |
| C17b | Cross-dataset transfer collapses; mIoU under-reports it too | RLMD→LoveDA mIoU 0.0001 but clDice 0.46 (`cross_dataset_generalization.md`) | ✅ supported (real) |
| C18 | Multi-seed: CE+Dice≈CoRe (tied), CoRe higher-variance | 3 seeds (`multiseed_results.md`, fig4) | ✅ **done** |

## Claims removed / softened during the audit

- **"CoRe wins 3× on real data"** → **retracted** (confounded: different
  architecture *and* loss).
- **"CE+Dice significantly beats CoRe (p<0.001)"** → **retracted.** True at seed 42
  only; the 3-seed run shows the means are tied (0.405 vs 0.406, Δ=−0.001) — a
  single-seed artifact. All reports corrected (README, `real_data_results.md`,
  `research_questions.md`, `paper_draft.md`, `multiseed_results.md`).
- **"Results validated on real aerial UAV data"** → **softened.** RLMD is
  ground-view real road markings; aerial-UAV (SkyScapes) ingestion is built but
  not run (license/compute). Stated explicitly everywhere.
- **"Synthetic reproduces the target UAV dataset"** → **softened** to "reproduces the
  statistical *structure*", and synthetic is demoted to variable-isolation only.

## Audit rule applied

Any statement of the form "X is best / X improves Y" must cite a measured result
file. Mechanistic explanations (why) are labelled as interpretation. Synthetic vs
real scope is stated for every quantitative claim.
