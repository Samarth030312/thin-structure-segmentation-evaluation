# Training Guide

## 1. Data layout (the folder contract)

```
datasets/<name>/
├── images/{train,val,test}/<stem>.{png,jpg,...}
└── masks/{train,val,test}/<stem>.png      # single-channel class-id PNG, values 0..C-1
```
Image ↔ mask are matched by **filename stem**. Masks are read as raw class ids
(no interpolation). Use `class_map` in the dataset config to remap arbitrary
mask values onto contiguous ids; use `ignore_index` (e.g. 255) for void pixels.

## 2. Always validate first

```bash
python scripts/dataset_validator.py --root datasets/custom_dataset --num-classes 7 \
    --ignore-index 255 \
    --class-names background solid_lane_line dashed_lane_line zebra_crossing \
                  road_arrow stop_line yellow_line
```
Open `validation_report.html`. **Fix every error** (missing pairs, bad class ids,
resolution mismatches) before spending GPU time.

## 3. Configure

Experiments compose fragments:
```yaml
# configs/experiment/uav_uavid.yaml
_base_:
  - ../dataset/custom_dataset.yaml
  - ../model/deeplabv3plus.yaml
  - ../loss/ce_dice.yaml
  - ../train/default.yaml
run_name: uav_uavid
```

## 4. Train

```bash
# editable install:        uavrm-train --config <cfg>
# or via the entry-point script:    python training/train.py --config <cfg>
uavrm-train --config configs/experiment/uav_uavid.yaml
```

Override anything from the CLI (no file edits):
```bash
uavrm-train --config configs/experiment/uav_uavid.yaml \
    --opt train.lr=3e-4 train.epochs=80 train.batch_size=12 \
          loss.name=tversky model.encoder=resnet101
```

## 5. Training features (all config-driven)

| Feature | Config key | Notes |
|---|---|---|
| Mixed precision | `train.amp: true` | auto-disabled on CPU |
| Gradient accumulation | `train.grad_accum: 4` | larger effective batch on small GPUs |
| Gradient clipping | `train.grad_clip: 1.0` | 0 disables |
| Scheduler | `train.scheduler.name` | `cosine` / `step` / `plateau` / `none` |
| Optimizer | `train.optimizer.name` | `adamw` / `adam` / `sgd` |
| Early stopping | `train.patience: 12` | on `train.monitor` (default `miou`) |
| Checkpoint metric | `train.monitor: miou` | `best.pth` saved on improvement |
| Device | `train.device: auto` | `auto`/`cuda`/`cpu` |

## 6. Artefacts

```
outputs/<run_name>/
├── best.pth          # best-on-monitor checkpoint (+ stored metrics)
├── last.pth          # latest (resumable: model+optimizer+scaler+epoch)
├── history.json      # per-epoch losses & metrics
├── config.json       # the fully-resolved config (reproducibility)
├── metrics.csv       # always-on CSV log
└── tb/               # TensorBoard event files (if available)
```

## 7. GPU memory tips (e.g. a 4–8 GB card)

- reduce `train.image_size` to `[384,384]` or `[256,256]`,
- `train.batch_size: 2` + `train.grad_accum: 4` (effective batch 8),
- prefer light encoders (`resnet34`, `mit_b0`),
- keep `train.amp: true`.

## 8. Transfer learning / pretraining

smp encoders default to ImageNet weights (`model.pretrained: true`). For the
domain-transfer ablation, first fine-tune on UAVid/Mapillary, then load that
checkpoint and continue on the target UAV dataset (`--checkpoint` path support in the engine's
resumable checkpoints).
