# Model Comparison & Benchmark Results

> **Historical / superseded.** This document is from the project's initial benchmark-building phase. The project's actual contribution and current narrative is the **width-coupling law** for thin-structure evaluation metrics — see `reports/width_coupling_theory.md` and `paper_package/final_ieee_paper.pdf`. The "target UAV dataset" referenced below was an aspirational road-marking set that was **never acquired**; the experiments actually used a synthetic generator and the public datasets RLMD, LoveDA, Massachusetts Roads, and UAVid. See `reports/repository_integrity_report.md`.


> **Read this first.** Every number below is **really computed** by the pipeline
> on the **synthetic** dataset (CPU, 3 epochs, 24 train images, from-scratch
> weights). They validate the *benchmark machinery* and illustrate the
> analysis methodology — they are **not** the target UAV dataset headline science. To produce
> headline numbers, point the config at the target UAV dataset, enable pretrained encoders,
> and run the full schedule (`configs/train/default.yaml`, 60 epochs). The
> commands and tables are identical; only the data and budget change.

## 1. Benchmark leaderboard (synthetic, auto-generated)

Source: `reports/leaderboard.csv`, ranked by foreground **mIoU**. Reproduce with
`uavrm-eval` (Phase 8).

| run_name | model | loss | mIoU | mDice | mPrecision | mRecall | PixelAcc | params (M) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| smoke_miniunet | MiniUNet (native) | ce_dice | **0.184** | 0.207 | 0.191 | 0.326 | 0.912 | 7.8 |
| synthetic_unet | U-Net (R34, smp) | ce_dice | 0.167 | 0.265 | **0.396** | 0.293 | **0.944** | 24.4 |
| synthetic_segformer | SegFormer (MiT-B0) | ce_dice | 0.108 | 0.179 | 0.322 | 0.269 | 0.321 | **3.7** |

## 2. Scientific analysis (Phase 11)

**Q: Why does the tiny MiniUNet top this particular table?**
It does *not* mean MiniUNet is the better architecture. Under a 3-epoch,
24-image, **from-scratch** budget, the heavier ImageNet-shaped backbones
(ResNet-34 in U-Net, MiT-B0 in SegFormer) are **starved of both data and
training steps** — their inductive priors only pay off with pretraining and more
iterations. The small MiniUNet has fewer parameters to fit and converges faster
in this micro-budget. This is a textbook **capacity-vs-data** effect and is
*expected*: it is precisely why the real protocol uses pretrained encoders and a
60-epoch schedule.

**Q: Why does SegFormer collapse (PixelAcc 0.32)?**
This is the most instructive result. The literature review (§2.5) flagged that
**transformers are data-hungry and require pretrained weights**. Here SegFormer
is trained **from scratch** (`pretrained=false`) for 3 epochs on 24 images — the
worst case for a ViT-style encoder. Its validation mIoU oscillates
(0.098 → 0.005 → 0.028) and pixel accuracy stays low: the model has not yet
learned a stable background prior. The framework *surfaced the predicted failure
mode*, which is exactly what a benchmark should do. With ImageNet-pretrained
MiT weights and a normal schedule, SegFormer is expected to be among the
strongest models (its real-world Pareto front is excellent).

**Q: Precision vs recall trade-off.**
U-Net shows the highest precision (0.396) but middling recall (0.293) — it is
conservative, predicting markings only where confident, hence high PixelAcc
(0.944). MiniUNet has the highest recall (0.326) — it over-predicts foreground,
catching more markings at the cost of precision. For **safety-critical lane
keeping, recall usually matters more**, which is the motivation for the Tversky
(β>α) loss in the loss study.

**Q: What does the failure-map visualisation add?**
`reports/qualitative/panel_00.png` shows U-Net/MiniUNet recovering the stop line
(green TP) while emitting false positives around it (red) and missing parts of
thin dashed lanes (blue FN). The aggregate mIoU cannot show *that the errors are
concentrated on the thinnest structures* — the failure maps can, and they point
directly at the fix (higher input resolution + recall-oriented loss).

## 3. Expected ordering on a real target UAV road-marking dataset (hypothesis to test)

Based on the literature analysis and the constraints (thin structures + severe
imbalance + multi-scale), with **pretrained encoders + full schedule**, the
*a priori* hypothesis is:

```
DeepLabV3+ (R50) ≈ SegFormer (B2) ≳ U-Net++ ≳ U-Net (R34) > PSPNet
                                                  └ recall↑ with Tversky/CE+Dice
```
with SegFormer winning on the accuracy/params Pareto front and PSPNet trailing
on thin-structure boundaries (its coarse decoder). This is stated as a
**falsifiable prediction**; the framework exists to test it — see the final
report's ablation plan.

## 4. How to regenerate this table

```bash
for cfg in unet unetpp deeplabv3plus pspnet segformer; do
  uavrm-train --config configs/experiment/${cfg}_custom.yaml
  uavrm-eval  --config configs/experiment/${cfg}_custom.yaml \
              --checkpoint outputs/${cfg}_custom/best.pth --split test
done
python -c "from uavroadmark.report.leaderboard import render_markdown; \
           print(render_markdown('reports/leaderboard.csv'))"
```
