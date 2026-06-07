# Figure and Table Audit

Independent review of every figure/table for the paper. "Main" = belongs in the
paper; "Supp" = supplementary; "Cut" = weak/redundant.

## Figures (`paper_figures/`)

| Figure | Content | Verdict | Notes / fix |
|---|---|---|---|
| **fig1_width_study** | mIoU/clDice/TolIoU vs marking width (synthetic) | **Main (teaser)** | The cleanest evidence; converged models. Strong. Minor: relabel "width" axis units; add a vertical line at the training width. |
| **fig2_rlmd_loss_ablation** | mIoU vs clDice vs PixelAcc per loss (real) | **Main (key)** | The headline mis-ranking. Good. Fix: the embedded caption note is informal; move to the figure caption. Sort bars by clDice and annotate the flooders. |
| **fig3_perf_pareto** | GFLOPs vs FPS, marker∝params | **Supp** | Useful but tangential to the metric thesis; deployment is a side story. Keep in supplementary. |
| **fig4_stats_ci** | CE+Dice vs CoRe, 3-seed mean±CI | **Main** | Supports the honest multi-seed result; the wide CoRe CI is the point. Good. Fix: show individual seed points (n=3) over the bars for transparency. |
| **fig5_cross_dataset** | 2×2 transfer heatmap (clDice) | **Cut or Supp** | The cross-dataset result is confounded and weak; if kept, label it "exploratory" and move to supplementary. |

## Tables (`paper_tables/`)

| Table | Content | Verdict | Notes |
|---|---|---|---|
| **table2_rlmd_loss_ablation** | real loss ablation | **Main** | The core evidence table. Add clPrecision column (currently dropped). |
| **table3_arch_sweep** | architecture sweep (synthetic) | **Main/Supp** | Supports the architecture mis-ranking; converged. Keep, but it is synthetic-only. |
| **table4_performance** | params/FLOPs/FPS/VRAM | **Supp** | Deployment Pareto; supplementary. |
| **table6_cross_dataset** | 2×2 transfer | **Supp** | Exploratory; supplementary. |
| **table7_multiseed** | per-loss multi-seed CIs | **Main** | Authoritative loss result; pair with fig4. |

## Weak figures / regeneration needed

- **fig2** and **fig4** carry an informal `fig.text(...)` note baked into the
  image; for the final version, remove it from the raster and put the statement in the
  LaTeX caption.
- **fig5** should either be cut or clearly marked exploratory.
- A **missing figure** worth adding: a *qualitative panel* (image | GT | a flooding
  prediction | clDice-good prediction) to make the mis-ranking visceral. The
  `reports/visualizations/failure_taxonomy_rlmd/` and `gradcam/` panels exist and
  could be assembled into one figure.

## Recommended paper figure set (4 main + supplementary)

1. **fig1** (teaser: width study).
2. **fig2** (headline: real loss mis-ranking).
3. **fig4** (honest multi-seed CIs).
4. **new qualitative panel** (flooding vs. good prediction).
Supplementary: fig3, fig5, table4, table6, architecture details.

## General quality

All figures are 300 DPI with vector PDF and a colour-blind-safe palette, no
top/right spines — production-adequate. The weaknesses are *editorial* (baked-in
notes, a confounded fig5), not rendering quality.
