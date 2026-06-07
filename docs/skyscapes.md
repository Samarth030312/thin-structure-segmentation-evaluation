# SkyScapes-Lane — Drop-in Guide

This is the real-aerial-marking benchmark (DLR SkyScapes-Lane, 13 classes). The
framework is ready; you only need to **drop in the data** and run two commands.

## 0. Get the data

SkyScapes is distributed by DLR under a research agreement (not redistributable
here): <https://www.dlr.de/en/eoc/.../dlr-skyscapes>. Download the **SkyScapes-Lane**
labels + images.

## 1. Drop it here

Put the raw files under `datasets/skyscapes_raw/` (any internal structure works;
override the two folder names with flags if needed):

```
datasets/skyscapes_raw/
├── images/            # the large aerial RGB images (.tif/.png/.jpg)
└── labels/            # lane-marking masks (grayscale-id OR RGB colour)
```
Image and label must share a filename **stem** (a label suffix like `_label` is
fine — pass `--label-suffix _label`).

## 2. Inspect (confirm the label format)

```bash
python scripts/prepare_skyscapes.py inspect --raw datasets/skyscapes_raw
```
This tells you whether masks are **grayscale-id** (ids 0..12) or **RGB colour**,
prints the unique ids/colours, and tells you the next flag to use.

- **Grayscale ids** → use `--label-mode id` (default). If the id ordering differs
  from `configs/dataset/skyscapes.yaml`, set `dataset.class_map` there (a simple
  `{src_id: dst_id}` map; no re-tiling needed).
- **RGB colour** → copy the printed colours into `configs/skyscapes_colormap.json`
  (or use SkyScapes' shipped class-dictionary CSV) and use
  `--label-mode rgb --colormap configs/skyscapes_colormap.json`.

## 3. Prepare (tile + remap + split)

The aerial images are huge; we tile them to 512² and write the framework's folder
contract. Markings are sparse, so we keep only a fraction of all-background tiles.

```bash
# grayscale-id masks:
python scripts/prepare_skyscapes.py prepare --raw datasets/skyscapes_raw \
    --out datasets/skyscapes --label-mode id \
    --tile 512 --stride 512 --keep-empty-frac 0.1

# RGB masks:
python scripts/prepare_skyscapes.py prepare --raw datasets/skyscapes_raw \
    --out datasets/skyscapes --label-mode rgb \
    --colormap configs/skyscapes_colormap.json --tile 512
```
Output: `datasets/skyscapes/{images,masks}/{train,val,test}/*.png`. Use
`--split-file split.json` to honour SkyScapes' official splits instead of the
deterministic 80/10/10 hash split.

## 4. Validate + explore

```bash
python scripts/dataset_validator.py --root datasets/skyscapes --num-classes 13 \
    --ignore-index 255
python scripts/explore_dataset.py --root datasets/skyscapes --num-classes 13
```
Fix any errors the validator reports before training.

## 5. Train + evaluate (identical commands to the synthetic study)

```bash
uavrm-train --config configs/experiment/skyscapes_unetpp_core.yaml
uavrm-eval  --config configs/experiment/skyscapes_unetpp_core.yaml \
    --checkpoint outputs/skyscapes_unetpp_core/best.pth --split test
```
Evaluation reports the **standard + thin-structure** metrics and appends to
`reports/leaderboard.csv`. Run the loss ablation / architecture sweep by swapping
the config, exactly as in the synthetic study.

## 6. Notes for the 4 GB card

- Configs use `batch_size: 4`, `grad_accum: 2` (effective 8), AMP on (pretrained
  encoders are fp16-stable). If you OOM, drop to `--tile 384` at prepare time, or
  `--opt train.batch_size=2 train.grad_accum=4`.
- First run downloads ImageNet encoder weights (needs network); set
  `model.pretrained: false` for fully offline runs.

That's it — the thin-structure protocol, CoRe loss, leaderboard, visualisations,
and C++ export all work unchanged on the real data.
