# Visualization Guide

Qualitative analysis is mandatory for thin-structure segmentation — aggregate
mIoU hides *where* and *how* a model fails. This framework produces four figure
types.

## Generate everything from a checkpoint

```bash
python scripts/visualize.py --config configs/experiment/smoke_miniunet.yaml \
    --checkpoint outputs/smoke_miniunet/best.pth --split test \
    --out reports/qualitative -n 6
```

Outputs `panel_NN.png` (per sample) and `error_heatmaps.png` (dataset-level).

## Figure types

| Function (`uavroadmark.viz`) | What it shows | Use it to… |
|---|---|---|
| `ground_truth_overlay` | GT mask α-blended on image | sanity-check labels |
| `prediction_overlay` | prediction α-blended on image | see raw model output |
| `failure_overlay` | **green=TP, red=FP, blue=FN** | localise error *type* per pixel |
| `comparison_panel` | image \| GT \| pred \| TP/FP/FN | the standard paper figure |
| `error_heatmaps` | FP/FN/support frequency over the dataset | find *systematic spatial bias* |

## Reading a failure map

- **Blue (false negatives)** along thin lines → the model under-segments thin
  markings; try Tversky (β>α) or higher input resolution.
- **Red (false positives)** clustered near shadows/cracks → photometric
  confusion; add brightness/contrast augmentation or shadow-robust training.
- **Red at frame edges** in the heatmap → lens-distortion / context-starvation at
  borders; consider reflect-padding or multi-scale inference.

## Example (synthetic smoke run)

`reports/qualitative/panel_00.png` shows the model correctly recovering the stop
line (green) while producing false positives around it (red) and partly missing
a dashed lane (blue) — a faithful, real diagnostic produced by the pipeline.

## Embedding in reports

All viz functions return a Matplotlib `Figure` and optionally save a 150-DPI PNG,
so they drop straight into the EDA/final reports or a `tracker.log_figure(...)`
call for TensorBoard/W&B.
