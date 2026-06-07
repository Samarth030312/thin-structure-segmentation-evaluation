# Literature Review — Semantic Segmentation Architectures for UAV Road-Marking Detection

> Scope: this review evaluates eight segmentation architectures **specifically
> for the task of detecting thin, sparse road markings in nadir/oblique UAV
> imagery**. For each model we cover architecture, strengths, weaknesses,
> compute cost, and — the part most reviews omit — *suitability for this exact
> task*. The task constraints (Section 1) drive every judgement.

---

## 1. Task constraints that shape architecture choice

UAV road-marking segmentation is **not** generic semantic segmentation. Four
properties dominate the design space:

| Property | Consequence for architecture |
|---|---|
| **Extreme class imbalance** — markings occupy ~1–5 % of pixels (our synthetic EDA: background = 94.6 %, foreground imbalance ratio ≈ 4.2). | Need strong multi-scale context **and** loss/architecture that preserves recall on tiny structures. Pixel accuracy is useless; mIoU over *foreground* classes is the honest metric. |
| **Thin, high-frequency structures** — a lane line is 2–8 px wide. | Aggressive downsampling (stride-32 backbones) destroys the signal. Decoders must recover full resolution; high-resolution-preserving designs (HRNet) or dense skips (U-Net++) help. |
| **Nadir / oblique viewpoint, no canonical "up".** | Rotation/flip augmentation is *safe and valuable* (unlike dashcam imagery). Models do not need a learned vertical prior. |
| **Large GSD variation & high input resolution** (UAV frames are 2–20 MP). | Multi-scale context (ASPP, PPM, hierarchical transformers) matters; memory/throughput of the architecture is a hard constraint. |

These constraints are the lens for every model below.

```
   Road-marking segmentation = (thin structures) × (severe imbalance) × (multi-scale context)
                                      │                    │                      │
                          full-res decoder        recall-oriented loss     ASPP / PPM / hierarchical
                          + dense skips            + foreground mIoU        attention
```

---

## 2. Architecture-by-architecture analysis

### 2.1 U-Net (Ronneberger et al., MICCAI 2015)

**Architecture.** Symmetric encoder–decoder. The encoder downsamples while
doubling channels; the decoder upsamples while halving them. The defining idea
is **skip connections** that concatenate encoder feature maps into the matching
decoder stage, letting the decoder recover spatial detail lost to pooling.

```
  enc1 ─────────────skip────────────► dec1 ─► head
    └─pool─ enc2 ──────skip──────► dec2
              └─pool─ enc3 ──skip► dec3
                        └─pool─ bottleneck
```

- **Strengths.** Excellent localisation of fine structures (it was built for
  thin cell membranes — *structurally analogous to lane lines*). Trains well on
  small datasets. Simple, fast, easy to modify. With an ImageNet encoder
  (ResNet/EfficientNet) it is a very strong baseline.
- **Weaknesses.** Limited global context (receptive field grows only with
  depth); plain skip-concat can fuse semantically mismatched features; no
  explicit multi-scale module.
- **Compute.** Low–moderate. ResNet-34 U-Net ≈ 24 M params, real-time at 512².
- **UAV suitability.** ★★★★☆ — full-res decoder + skips are ideal for thin
  markings; main gap is global context for large arrows / zebra blocks.
- **Road-marking suitability.** ★★★★☆ — the canonical strong baseline; our
  default encoder is ResNet-34.

### 2.2 U-Net++ (Zhou et al., DLMIA 2018)

**Architecture.** Re-designs U-Net's skip pathway as a **dense grid of nested,
densely-connected decoder blocks** with deep supervision. Instead of one skip
per scale, intermediate nodes progressively bridge the semantic gap between
encoder and decoder features.

- **Strengths.** Better fine-grained segmentation than U-Net; deep supervision
  enables accuracy/speed trade-off via pruning; the dense skips help recover
  very thin structures.
- **Weaknesses.** More parameters, more memory, slower; gains over a
  well-tuned U-Net are often modest and dataset-dependent.
- **Compute.** Moderate. ~9–35 M params depending on encoder; notably higher
  activation memory than U-Net.
- **UAV / road-marking suitability.** ★★★★☆ — the dense skips are theoretically
  well-matched to thin markings; worth benchmarking against U-Net to see if the
  extra cost pays off (a natural **ablation**, see final report).

### 2.3 DeepLabV3+ (Chen et al., ECCV 2018)

**Architecture.** Dilated/atrous convolution backbone + **Atrous Spatial
Pyramid Pooling (ASPP)** (parallel atrous convs at multiple rates + image-level
pooling) for multi-scale context, followed by a simple decoder that fuses a
low-level feature for boundary refinement.

```
  backbone ─► ASPP {rate 6,12,18 + img-pool} ─► 1×1 ─┐
       └─ low-level feat ─► 1×1 ──────────────────► concat ─► 3×3 ─► up ×4 ─► head
```

- **Strengths.** ASPP captures multi-scale context **without losing
  resolution** — directly addresses GSD variation and large markings. The most
  battle-tested driving-scene segmentation model. Strong with ResNet-50/101.
- **Weaknesses.** Decoder is comparatively shallow (single skip) so the finest
  boundaries can be softer than U-Net's; ASPP at high resolution is
  memory-hungry.
- **Compute.** Moderate–high. ResNet-50 ≈ 26 M params; ResNet-101 heavier.
- **UAV / road-marking suitability.** ★★★★★ — the original notebook's choice,
  and a defensible one: ASPP's multi-scale context suits mixed marking
  scales. We keep it as the **primary CNN benchmark** (ResNet-50 encoder).

### 2.4 PSPNet (Zhao et al., CVPR 2017)

**Architecture.** **Pyramid Pooling Module (PPM)**: pool the backbone feature
map to 1×1, 2×2, 3×3, 6×6 grids, convolve each, upsample, and concatenate —
injecting global + regional context.

- **Strengths.** Strong global context aggregation; excellent on large,
  contextual classes; simple and robust.
- **Weaknesses.** Coarse output stride and no detail-recovery decoder → **soft
  boundaries**, the weakest property for thin markings. Heavy global pooling.
- **Compute.** High. ResNet-50/101 backbones; large activation memory.
- **UAV / road-marking suitability.** ★★★☆☆ — great context, poor thin-structure
  localisation. Included precisely to **demonstrate the boundary-vs-context
  trade-off** in the benchmark.

### 2.5 SegFormer (Xie et al., NeurIPS 2021)

**Architecture.** Hierarchical **Mix Transformer (MiT)** encoder producing
multi-scale features with efficient (sequence-reduced) self-attention and **no
positional encodings** (uses overlapping patch merging + a conv in the FFN),
plus an extremely lightweight all-MLP decoder that fuses the 4 stages.

- **Strengths.** Global receptive field from layer 1; strong accuracy/efficiency
  Pareto front; **robust to resolution/scale shifts** (no fixed positional
  encoding) — valuable for variable-altitude UAV data; MiT-B0 is tiny (~3.7 M).
- **Weaknesses.** Transformers are data-hungry; with a small road-marking
  dataset, pretrained weights and transfer learning are essential. The MLP
  decoder can under-resolve very thin edges relative to a heavy CNN decoder.
- **Compute.** B0 very low (~3.7 M params, ~8 GFLOPs @512²) up to B5 (~85 M).
  Attention memory scales with resolution despite sequence reduction.
- **UAV / road-marking suitability.** ★★★★☆ — the most promising *modern*
  baseline; scale-robustness is a real UAV advantage. We benchmark **MiT-B0/B2**
  with transfer learning.

### 2.6 Mask2Former (Cheng et al., CVPR 2022)

**Architecture.** Unifies semantic/instance/panoptic segmentation as **mask
classification** via a Transformer decoder with **masked attention** over
learnable object queries on multi-scale pixel-decoder features.

- **Strengths.** SOTA accuracy across segmentation tasks; naturally yields
  **instance** masks — relevant if individual dashes/arrows must be counted,
  not just labelled.
- **Weaknesses.** Heavy and complex; slow to train and infer; needs substantial
  data; overkill for pure semantic masks; query-based mask resolution can miss
  hair-thin lines.
- **Compute.** High. 40–100 M+ params; high training cost.
- **UAV / road-marking suitability.** ★★★☆☆ — high ceiling but poor
  cost/benefit unless the deliverable requires per-instance markings. Reviewed,
  **not in the default zoo** (documented as future work; deferring it is itself
  a defensible engineering decision).

### 2.7 HRNet (Wang et al., TPAMI 2020)

**Architecture.** Maintains **high-resolution representations throughout** the
network via parallel multi-resolution streams with repeated cross-resolution
fusion — instead of recovering resolution late, it never throws it away.

- **Strengths.** Best-in-class for tasks needing precise spatial detail
  (pose, fine segmentation) — **structurally ideal for thin markings**. Strong
  multi-scale fusion.
- **Weaknesses.** Memory- and compute-heavy from keeping high-res streams alive;
  more complex to implement/tune.
- **Compute.** High. HRNet-W18 (~9.6 M) to W48 (~65 M) with large activations.
- **UAV / road-marking suitability.** ★★★★☆ — excellent for detail; cost is the
  trade-off. A strong candidate for a follow-up "accuracy-first" benchmark.

### 2.8 BiSeNet / BiSeNetV2 (Yu et al., ECCV 2018 / IJCV 2021)

**Architecture.** Two-branch design: a shallow, wide **Spatial Path** preserves
detail; a deep, fast **Context Path** captures semantics; a Feature Fusion
Module merges them. Built for **real-time** segmentation.

- **Strengths.** Very fast, low latency — the natural choice for **on-board /
  edge UAV inference** (e.g. a Jetson). Decent accuracy for its speed.
- **Weaknesses.** Lower accuracy ceiling than DeepLab/HRNet/SegFormer; the thin
  Spatial Path can still under-segment the finest markings.
- **Compute.** Very low. ~5–15 M params; real-time at high resolution.
- **UAV / road-marking suitability.** ★★★★☆ **for deployment**, ★★★☆☆ for peak
  accuracy. Important as the **efficiency anchor** of the benchmark (it frames
  the accuracy–latency Pareto front that AV teams actually care about).

---

## 3. Comparative summary

| Model | Year | Params (typical) | Context mechanism | Detail recovery | Speed | Road-marking fit |
|---|---|---|---|---|---|---|
| U-Net | 2015 | ~24 M (R34) | depth only | **High** (skips) | Fast | ★★★★☆ |
| U-Net++ | 2018 | ~9–35 M | dense skips | **High** | Med | ★★★★☆ |
| DeepLabV3+ | 2018 | ~26 M (R50) | **ASPP** | Med–High | Med | ★★★★★ |
| PSPNet | 2017 | ~46 M (R50) | **PPM** | Low–Med | Med | ★★★☆☆ |
| SegFormer | 2021 | 3.7–85 M | **hier. attention** | Med | Fast (B0) | ★★★★☆ |
| Mask2Former | 2022 | 40–100 M+ | masked attention | Med | Slow | ★★★☆☆ |
| HRNet | 2020 | 9.6–65 M | **parallel hi-res** | **Very High** | Slow | ★★★★☆ |
| BiSeNetV2 | 2021 | 5–15 M | two-branch | Med | **Real-time** | ★★★★☆ (deploy) |

*Speed/params are order-of-magnitude at 512² with standard encoders; exact
numbers depend on encoder and implementation.*

### 3.1 Selection for the benchmark zoo

We implement **U-Net, U-Net++, DeepLabV3+, PSPNet, SegFormer** (Phase 5) because
together they span the design axes that matter here:

- **detail-first** (U-Net, U-Net++) vs **context-first** (PSPNet),
- **balanced CNN SOTA** (DeepLabV3+),
- **modern transformer** (SegFormer),

giving an honest, *controlled* comparison. HRNet, Mask2Former, BiSeNetV2 are
documented as principled extensions (accuracy-first, instance-aware, and
edge-deployment axes respectively) in the final report's Future Work.

---

## 4. The loss function is as important as the architecture

A recurring finding in the road-marking / thin-structure literature is that for
this degree of imbalance, **the loss choice can move foreground mIoU more than
the architecture choice.** Region losses (Dice/Tversky) and hard-example losses
(Focal) are designed for exactly this regime. This motivates the dedicated loss
study (Phase 7, `reports/loss_function_study.md`), which is treated as a
first-class experimental variable, not an afterthought.

---

## 5. References

1. Ronneberger, Fischer, Brox. *U-Net: Convolutional Networks for Biomedical Image Segmentation.* MICCAI 2015.
2. Zhou et al. *UNet++: A Nested U-Net Architecture for Medical Image Segmentation.* DLMIA 2018.
3. Chen, Zhu, Papandreou, Schroff, Adam. *Encoder-Decoder with Atrous Separable Convolution (DeepLabV3+).* ECCV 2018.
4. Zhao, Shi, Qi, Wang, Jia. *Pyramid Scene Parsing Network (PSPNet).* CVPR 2017.
5. Xie, Wang, Yu, Anandkumar, Alvarez, Luo. *SegFormer: Simple and Efficient Design for Semantic Segmentation with Transformers.* NeurIPS 2021.
6. Cheng, Misra, Schwing, Kirillov, Girdhar. *Masked-attention Mask Transformer for Universal Image Segmentation (Mask2Former).* CVPR 2022.
7. Wang et al. *Deep High-Resolution Representation Learning for Visual Recognition (HRNet).* TPAMI 2020.
8. Yu, Gao, Wang, Yu, Sang. *BiSeNet V2: Bilateral Network with Guided Aggregation for Real-time Semantic Segmentation.* IJCV 2021.
9. Lin, Goyal, Girshick, He, Dollár. *Focal Loss for Dense Object Detection.* ICCV 2017.
10. Milletari, Navab, Ahmadi. *V-Net / Dice loss for volumetric segmentation.* 3DV 2016.
11. Salehi, Erdogmus, Gholipour. *Tversky loss function for image segmentation.* MLMI 2017.
12. Iglovikov, Shvets. *TernausNet: U-Net with VGG11 encoder pretrained on ImageNet.* 2018 (encoder-pretraining for segmentation).
13. Lyu et al. *UAVid: A Semantic Segmentation Dataset for UAV Imagery.* ISPRS J. 2020.
14. Wang et al. *LoveDA: A Remote Sensing Land-Cover Dataset for Domain Adaptive Semantic Segmentation.* NeurIPS Datasets 2021.

*(Citations are to the canonical works; see `dataset_selection_report.md` for dataset-specific references.)*
