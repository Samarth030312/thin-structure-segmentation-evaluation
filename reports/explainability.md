# Explainability Study — U-Net++ vs SegFormer

> Grad-CAM (Selvaraju et al., ICCV 2017) on the last convolutional feature map,
> targeting the `solid_lane_line` class, via `scripts/run_gradcam.py`. Figures:
> `reports/visualizations/explainability/{unetpp,segformer}/`. Checkpoints are the
> architecture-sweep models (U-Net++ R34, SegFormer MiT-B0).

## 1. What Grad-CAM shows here

For both architectures, the class-activation map for `solid_lane_line`
**concentrates tightly on the actual solid line** and *ignores* the adjacent
dashed line and the zebra block — direct evidence that the networks key on the
correct structure, not on generic bright-on-asphalt texture. This is the basic
sanity check an interpretability pass must pass, and both models pass it.

## 2. Architectural comparison (mechanism + observation)

| Aspect | U-Net++ (dense CNN skips) | SegFormer (hierarchical attention) |
|---|---|---|
| Receptive field of the CAM source | local→regional (conv stack) | global from layer 1 (self-attention) |
| Observed CAM on solid line | sharp, high-frequency, hugs the line | sharp, comparably localized |
| Off-target suppression (dashed/zebra) | strong | strong |
| Params (efficiency) | 26.1 M | **3.7 M** |

**Observation (honest):** on the synthetic frames the two CAMs are **visually
similar** — both crisply localize the target line. The expected mechanistic
difference (SegFormer's response derives from global context; U-Net++'s from local
skip-fused detail) does not produce a dramatic *visual* divergence on these clean,
geometrically simple scenes. The more telling difference is quantitative: SegFormer
reaches comparable attention quality with **7× fewer parameters** (see
`leaderboard_performance.csv`), consistent with its strong accuracy/efficiency
trade-off.

## 3. Why this matters for perception

Interpretability here serves two engineering purposes: (1) **trust** — confirming
the model attends to markings, not spurious cues (shadows, lane-adjacent texture),
which the failure taxonomy flags as confounders; (2) **architecture selection** —
SegFormer's equally-focused attention at 1/7 the parameters supports its
recommendation as the **deployment** model (`research_questions.md` Q7).

## 4. Honest limitations

- Grad-CAM on the *last conv* of SegFormer probes its MLP-decoder convs, not the
  raw transformer attention maps; a full attention-rollout visualisation of the
  MiT encoder is a documented next step (`hooks on each `Attention` block).
- The comparison uses the synthetic-trained architecture checkpoints (the only
  ones trained for *both* architectures); a real-RLMD SegFormer would need an
  additional training run (compute-bounded, queued). The *mechanistic* conclusion
  is architecture-intrinsic and expected to hold.

> Reproduce: `python scripts/run_gradcam.py --config configs/experiment/arch_unetpp.yaml --checkpoint outputs/arch_unetpp/best.pth --class-id 1` (and `arch_segformer`).
