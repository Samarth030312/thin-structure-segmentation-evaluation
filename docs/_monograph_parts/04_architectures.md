# Part 4 — Computer-Vision Architectures

Every segmentation network is an answer to one tension: you must **see a lot of
context** (big receptive field, achieved by downsampling) yet **output a precise,
full-resolution label map** (which downsampling destroys). The architectures below
are five different bargains between those goals. We treat each with: history, the
problem it solved, a diagram, encoder/decoder/skips/attention, complexity, pros/cons,
why it was used here, and how it fared.

## 4.0 The shared skeleton: encoder–decoder

```
  INPUT  ─► [ENCODER: conv + downsample ×4]  ─► bottleneck (small, deep)
            high-res, shallow ──────────────┐        │
                                            skips     ▼
  OUTPUT ◄─ [DECODER: conv + upsample ×4] ◄──────────┘
            recovers resolution, fuses skips
```

- **Encoder (backbone):** a classification network (e.g. ResNet-34) stripped of its
  final classifier; it downsamples `H×W → H/32×W/32` while deepening channels. It is
  usually **pre-trained on ImageNet**, giving the model edge/texture detectors for
  free — crucial when you have few labelled images.
- **Decoder:** upsamples back to full resolution, producing the label map.
- **Skip connections:** carry high-resolution detail from encoder to decoder so the
  decoder can place boundaries precisely — *the* feature that matters for thin
  structures.

## 4.1 U-Net (2015) — the project's workhorse

**History.** Introduced for biomedical segmentation (Ronneberger et al., MICCAI
2015), where data is scarce and structures are thin (cells, membranes). Named for its
U-shaped diagram.

**Problem solved.** Produce precise, full-resolution masks from few images, recovering
fine detail lost during downsampling.

**Diagram.**
```
   x ─►C─►C─┐(skip 1)                         ┌─►C─►C─► y
            ▼                                 │
           ↓2 C─►C─┐(skip 2)         ┌─►up─cat┘
                   ▼                 │
                  ↓2 C─►C─┐  ┌─►up─cat┘(skip 2)
                         ▼  │
                        ↓2 C─►C  (bottleneck)
                         └─►up─cat (skip 1)
```

- **Encoder:** repeated `conv→conv→downsample`. Here the encoder is **ResNet-34**
  (ImageNet-pretrained) for stronger features.
- **Decoder:** repeated `upsample→concatenate-skip→conv→conv`.
- **Skip connections:** *concatenate* encoder features with decoder features at each
  scale — directly injecting high-res detail. This is why U-Net is excellent at thin
  structures.
- **Attention:** none in the classic form.

**Complexity.** With a ResNet-34 encoder, ~24 M parameters; compute dominated by the
high-resolution early/late convolutions. Memory is dominated by the large early
feature maps.

**Pros:** superb detail recovery, data-efficient, simple, reliable. **Cons:** limited
global context (receptive field grows only with depth); concatenated skips are
memory-heavy.

**Why used here.** Thin markings need exactly U-Net's strength — high-resolution
boundary precision with few labels. It is the **primary** architecture for the
controlled and real-data experiments (UAVid mIoU 0.57, MassRoads mIoU 0.49, the
converged binary RLMD model).

**How it fared.** It converged reliably on every binary task and is the backbone of
the width-validation results. It is the safe default when data and compute are
limited.

## 4.2 U-Net++ (2018) — denser skips

**History.** Zhou et al. (DLMIA 2018) redesigned U-Net's skips, hypothesising that
directly concatenating shallow encoder features with deep decoder features fuses
*semantically dissimilar* maps.

**Problem solved.** Reduce the "semantic gap" across skips with **nested, dense skip
pathways**: a grid of intermediate conv blocks that progressively bridge encoder and
decoder at every scale, plus deep supervision.

**Diagram (nested grid).**
```
  X0,0 ─► X0,1 ─► X0,2 ─► X0,3 ─► X0,4   (each Xi,j fuses all shallower+upsampled deeper)
    ↓        ↑        ↑        ↑
  X1,0 ─► X1,1 ─► X1,2 ─► X1,3
    ↓        ↑        ↑
  X2,0 ─► X2,1 ─► X2,2
    ↓        ↑
  X3,0 ─► X3,1
    ↓
  X4,0
```

**Encoder/decoder:** same downsampling backbone; the decoder is the dense grid of
`Xi,j` blocks. **Skips:** many, nested. **Attention:** none (in the base form).

**Complexity.** More parameters and **much more memory** than U-Net (the grid holds
many intermediate maps). On a 4 GB GPU it **out-of-memoried at batch 8**, forcing
batch 2–4 + gradient accumulation.

**Pros:** can improve accuracy on some tasks; flexible depth via deep supervision.
**Cons:** memory- and compute-hungry; marginal gains for the extra cost on this
project.

**Why used here.** It is the backbone of the **loss ablation** on RLMD (all six
losses, same architecture) — a controlled comparison where only the loss varies.

**How it fared.** Functional but memory-constrained; the loss-ablation result (mIoU
mis-ranking under imbalance) was produced with it. Not worth its memory premium over
U-Net for the thin-structure question.

## 4.3 DeepLabV3+ (2018) — dilated convolutions + ASPP

**History.** Chen et al. (Google). The DeepLab line tackled the
resolution-vs-context tension with **dilated (atrous) convolutions** that enlarge the
receptive field *without* downsampling.

**Problem solved.** Get large context and keep resolution. A dilated conv inserts
gaps of size `r` between kernel taps, so a `3×3` kernel with dilation `r` sees a
`(2r+1)×(2r+1)` region using the same 9 weights.

**ASPP (Atrous Spatial Pyramid Pooling).** Run several dilated convs with different
rates in parallel and fuse them, capturing objects at multiple scales. The `+` in
V3+ adds a light decoder for sharper boundaries.

**Diagram.**
```
  encoder ─► [ASPP: dilations 1,6,12,18 + global pool] ─► fuse ─► decoder ─► y
```

**Encoder:** ResNet/Xception. **Decoder:** light upsampling that fuses a low-level
skip. **Attention:** none core (global pooling gives image-level context).

**Complexity.** Moderate-heavy; ASPP adds parallel branches. Inference memory was
modest in profiling (~0.56 GB at 512²).

**Pros:** strong multi-scale context; good on wide/large objects. **Cons:** dilated
convs can miss the finest detail; ASPP is overkill for tiny thin structures.

**Why used here.** Part of the **architecture sweep** on synthetic data, to test
whether mIoU mis-ranks *architectures* (not just losses).

**How it fared.** Competent, but its multi-scale machinery is aimed at wide objects;
for 2-px markings it offers little over U-Net. Included for breadth.

## 4.4 PSPNet (2017) — pyramid pooling

**History.** Zhao et al. (CVPR 2017). Introduced the **Pyramid Pooling Module
(PPM)**: pool the feature map at several grid scales (1×1, 2×2, 3×3, 6×6), upsample,
and concatenate — injecting global and regional context.

**Problem solved.** Lack of global context causing classes to be confused (a boat
labelled "car" because the surrounding water was ignored).

**Diagram.**
```
  encoder ─► [pool 1×1 | 2×2 | 3×3 | 6×6] ─► upsample+concat ─► conv ─► y
```

**Encoder:** ResNet. **Decoder:** simple upsample after PPM. **Skips/attention:**
minimal.

**Complexity.** Moderate. **Pros:** strong scene-level context. **Cons:** coarse
output; weak at fine boundaries — a poor match for thin structures.

**Why used here.** Breadth in the architecture comparison; a contrast to U-Net's
detail focus.

**How it fared.** As expected, context-strong but detail-weak; not a thin-structure
champion.

## 4.5 SegFormer (2021) — transformers for segmentation

**History.** Xie et al. (NeurIPS 2021). Replaced the convolutional encoder with a
**hierarchical Vision Transformer** and paired it with an all-MLP decoder.

**Problem solved.** Convolutions have a fixed local receptive field; **self-attention**
lets every patch attend to every other, giving global context from layer one, while a
hierarchical design keeps multiple resolutions.

**Self-attention (the core idea).** Each token (image patch) emits a query `q`, key
`k`, value `v`. The output for a token is a weighted sum of all values, weighted by
query–key similarity:
$$\text{Attention}(Q,K,V) = \text{softmax}\!\left(\frac{QK^\top}{\sqrt{d}}\right)V.$$
"Attend to whatever is relevant, anywhere in the image." SegFormer uses an *efficient*
attention to keep this affordable at high resolution.

**Diagram.**
```
  patches ─► [Transformer stages ×4 (attention), decreasing resolution] ─► MLP decoder ─► y
```

**Encoder:** hierarchical transformer (MiT). **Decoder:** lightweight MLP that fuses
multi-scale tokens. **Attention:** the whole point.

**Complexity.** Variants from tiny (MiT-B0) to large; attention is the cost driver.
Heavier to train; benefits most from large data.

**Pros:** excellent global context, strong on large/contextual scenes, scalable.
**Cons:** data- and compute-hungry; on tiny datasets and a 4 GB GPU it is hard to
realise its advantage; fine thin-structure detail relies on the decoder's fusion.

**Why used here.** The modern, transformer contrast point in the architecture sweep,
and a test of whether the mis-ranking effect is architecture-specific (it is not — it
is a *metric* property).

**How it fared.** Included for breadth; on this compute budget it is not the
thin-structure leader. Its presence shows the law is **architecture-independent** —
the metric disagreement is geometric, not a quirk of one model family.

## 4.6 Choosing among them (the project's logic)

```
  Need                          Best choice here
  -----------------------------------------------
  Thin-structure detail, few    U-Net (primary)
  images, tiny GPU
  Controlled loss comparison    U-Net++ (loss ablation)
  Multi-scale wide objects      DeepLabV3+ / PSPNet
  Global context, big data      SegFormer
```

The decisive point for the monograph: **the width-coupling law does not depend on the
architecture.** Whatever model produces the prediction, a fixed boundary error `δ`
on a width-`w` structure yields the same `2δ/(w+2δ)` gap. Architectures change `δ`
(how well a model localises), not the *form* of the law. That is why the controlled
experiment (Part 8) uses *no model at all* — pure geometry — and still reproduces what
every architecture exhibits.

---
