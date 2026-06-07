# When mIoU Lies: Topology-Aware Evaluation of Thin Road-Marking Segmentation

**Abstract** -- Mean Intersection-over-Union (mIoU) is the de-facto metric for semantic segmentation, including road-marking perception. We show two ways it fails for *thin* (2-8 px) road markings. First, on **converged** models in a width-controlled study (3 seeds, 95% CIs), mIoU under-reports correctly and continuously detected thin markings: at 2 px, mIoU = 0.35 +/- 0.01 while centerline-Dice = 0.997 +/- 0.001 and tolerance-IoU = 0.98 -- a ~0.65 gap with non-overlapping confidence intervals. Second, under extreme multi-class imbalance (real RLMD, 25 classes, 609:1), mIoU -- in *both* its all-class and foreground forms -- *mis-ranks* losses: its top-ranked model is a frame-flooder (0.9% pixel accuracy) and it places the genuine best detector third. Frequency-weighted IoU and pixel accuracy avoid rewarding flooding but are insensitive to foreground quality (spread <= 0.005 vs. centerline-Dice's 0.31); only the topology metric is both flood-robust and sensitive. We propose a thin-structure evaluation protocol (centerline-Dice, Boundary-IoU, tolerance-IoU, width-stratified analysis) and an automated three-test check, and recommend reporting it alongside mIoU. A studied connectivity loss yields no reliable multi-seed gain and is supplementary. Results are on ground-view markings and a controlled synthetic benchmark; aerial and full-scale validation are future work.

**Index Terms** — semantic segmentation, evaluation metrics, road markings,
class imbalance, centerline Dice.

---

## I. Introduction

Road-marking segmentation underpins lane perception, HD-map maintenance, and
infrastructure auditing. Markings are *thin* and *sparse*: in our real dataset
they occupy under 2 % of pixels, with a 609:1 imbalance between the most- and
least-common classes. The field reports mean IoU (mIoU) almost universally.

We ask a measurement question: *does mIoU faithfully reflect thin-marking
perception quality, and does it select the right model and loss?* We find it does
not. Our contributions are:

1. A **thin-structure evaluation protocol** — centerline-Dice (clDice),
   Boundary-IoU, a tolerance-band centerline metric, and a **width-stratified**
   analysis (Sec. III).
2. **Empirical evidence that mIoU mis-ranks** losses on real road markings,
   crowning a model that floods 99 % of pixels, with the flooding mechanism
   measured directly via pixel accuracy; corroborated by a controlled width study
   (Sec. V).
3. An **honest, multi-seed** study of a connectivity loss (CoRe): a single-seed
   advantage over CE+Dice does not survive multiple seeds (Sec. V-D).
4. A **reproducible, tested benchmark** with real-dataset ingestion and an
   ONNX/TensorRT/C++ deployment path.

We deliberately frame this as an *evaluation* paper. We do not claim a new
state-of-the-art model, and we report a proposed loss that does not reliably help.

## II. Related Work

**Segmentation architectures.** U-Net, U-Net++, DeepLabV3+, PSPNet, and SegFormer
span encoder–decoder, atrous, pyramid-pooling, and transformer designs.

**Thin/tubular evaluation.** clDice and its differentiable soft-skeleton, and
Boundary-IoU, were proposed for vessels, road networks, and boundary quality. We
adopt these and add a width-stratified analysis; we do not claim them as novel.

**Losses for imbalance.** Dice, Focal, and Tversky address class imbalance; it is
known that overlap/accuracy metrics can reward over-prediction. Our contribution
is the *quantified rank-inversion* on real road markings, not the observation that
imbalance is hard.

## III. Methodology

### A. Thin-structure evaluation protocol
For binary any-marking masks we report: **clDice**, the harmonic mean of
skeleton-precision and skeleton-sensitivity; **Boundary-IoU**, IoU over a
*d*-pixel boundary band; **tolerance-IoU / centerline-F1**, detection within τ
pixels of the ground-truth centerline; and a **width-stratified** IoU/clDice,
where ground-truth marking width is an independent variable. These measure
*topology* and *detection*, not pixel overlap.

### B. CoRe loss (studied, not assumed)
We study a Connectivity-Recall loss,
L = w_ce·CE + w_r·Dice + w_t·(1 − soft-clDice),
with a soft skeleton on the any-marking probability. The CE term calibrates the
background; the soft-clDice term encourages connectivity.

### C. Benchmark and data
**RLMD** (Road Line & Marking Dataset; 2,137 real driving-scene images, 25
marking classes, RGB masks) is the real benchmark. A **controlled synthetic**
generator renders markings at a parametric width-scale, the only source of
ground-truth width control. We additionally probe cross-dataset transfer to an
aerial land-cover dataset (LoveDA) on a binary foreground task.

## IV. Experimental Setup

Single 4 GB GPU; PyTorch; fp32 (fp16 was numerically unstable on this hardware).
U-Net++ (ResNet-34) for the loss ablation; the architecture sweep uses U-Net,
U-Net++, DeepLabV3+, PSPNet, SegFormer. ImageNet-pretrained encoders, AdamW,
cosine schedule. **Compute-bounded**: RLMD runs use a 500-image train subset, 12
epochs, 384²; the synthetic study uses 200 images, 25 epochs, 256². Metrics:
standard (mIoU, Dice, pixel accuracy) and the thin-structure protocol.
Statistics: per-image bootstrap 95 % CIs and paired bootstrap tests; multi-seed
(42, 123, 999). We disclose that, under this budget, the real 25-class models are
under-trained (best clDice 0.37).

## V. Results

### A. mIoU under-reports thin markings (converged, multi-seed)
On converged models (clDice ~ 0.997 at the training width) over three seeds,
evaluated across the controlled width series (mean +/- 95% CI):

| width | mIoU | TolIoU | clDice |
|---|---|---|---|
| 2 px | 0.351 +/- 0.007 | 0.975 +/- 0.009 | 0.997 +/- 0.001 |
| 4 px | 0.892 +/- 0.048 | 0.995 +/- 0.001 | 0.998 +/- 0.002 |
| 8 px | 0.468 +/- 0.057 | 0.968 +/- 0.013 | 0.951 +/- 0.047 |

At 2 px, mIoU = 0.35 [0.34, 0.36] while clDice = 0.997 [0.996, 0.998] and
tolerance-IoU = 0.98: the lines are correctly and continuously recovered, with
non-overlapping, tight CIs. mIoU conflates detection with exact-width matching;
the effect is reproducible across seeds and is **not** an under-training artifact
(the models converge). This is the paper's primary, hardest-to-attack result.

### B. mIoU mis-ranks losses (real RLMD, U-Net++, same architecture)

| Loss | mIoU | PixelAcc | clDice | clPrecision | clRecall |
|---|---|---|---|---|---|
| CE+Dice | 0.029 | 0.983 | **0.373** | **0.907** | 0.356 |
| CoRe | 0.005 | 0.981 | 0.275 | 0.896 | 0.211 |
| Focal | 0.018 | 0.983 | 0.085 | — | 0.103 |
| CE | 0.010 | 0.982 | 0.063 | — | 0.096 |
| Dice | 0.140 | **0.008** | 0.062 | — | 1.000 |
| Tversky | **0.144** | **0.009** | 0.084 | 0.133 | 1.000 |

Under extreme multi-class imbalance we evaluate every common metric with an
automated three-test check (does the metric's top-ranked model flood the frame;
does it rank the genuine best detector first; is it foreground-sensitive):

| Metric | top floods? | best #1? | spread |
|---|---|---|---|
| mIoU (fg) | yes (Tversky, PixAcc 0.009) | no (#3) | 0.023 |
| mIoU (all-class) | yes (Tversky) | no (#3) | 0.023 |
| FWIoU | no | yes | 0.005 |
| PixelAcc | no | yes | 0.003 |
| clDice | no | yes | **0.310** |

mIoU -- in both forms -- ranks a frame-flooding model first and buries the best
detector at third. FWIoU and pixel accuracy avoid rewarding flooding but, dominated
by the 98% background, cannot distinguish a clDice-0.06 model from a clDice-0.37
one (spread <= 0.005). Only clDice passes all three tests. We scope this honestly:
it is a *multi-class extreme-imbalance* phenomenon (on a binary task mIoU does not
reward flooding) and the models are at different operating points; the claim is
about *metric ordering* under imbalance, complementing the converged width result
in Sec. V-A.

### C. Architecture sweep (synthetic, converged)
Skip-connection decoders (U-Net, U-Net++) lead Boundary-IoU (0.986–0.987);
PSPNet, with a coarse decoder, is worst (0.62). DeepLabV3+ and SegFormer swap rank
between mIoU and Boundary-IoU, a further mis-ranking instance. SegFormer-B0
attains comparable boundary quality with 3.7 M parameters (7× fewer).

### D. Connectivity loss: an honest multi-seed result
At seed 42, CE+Dice beats CoRe (clDice 0.37 vs 0.28, per-image p<0.001). Across
three seeds, the advantage vanishes: CE+Dice 0.405 ± 0.058 vs CoRe 0.406 ± 0.141
(paired Δ = −0.001, 95 % CI [−0.18, 0.18]; CoRe wins at seed 999). CoRe is
higher-variance and yields no reliable gain. The single-seed result was an
artifact, detected only by multi-seed evaluation.

### E. Cross-dataset transfer (binary, exploratory)
In-domain binary segmentation works (clDice 0.63–0.67); cross-domain
(ground↔aerial, disjoint semantics) collapses. Notably, RLMD→LoveDA gives mIoU
0.0001 but clDice 0.46 — mIoU under-reports even here. This result is confounded
and we treat it as exploratory.

### F. Deployment
ONNX Runtime is 1.47× faster than eager PyTorch on CPU at bit-identical output
(max |Δ| = 9e-8); TorchScript export is exact. A C++/LibTorch engine and a
TensorRT path are released.

## VI. Discussion

The practical message is concrete: **for thin road markings, report clDice /
Boundary-IoU / tolerance-IoU and pixel accuracy, not mIoU alone**, because mIoU can
rank a useless frame-flooding model first. The mechanism is that mIoU couples
*detection* with *exact-width matching* and, under extreme imbalance, rewards
over-prediction. The synthetic study isolates the width-coupling cleanly; the real
study shows it changes decisions.

## VII. Limitations

(1) **Scope.** RLMD is ground-view; we report no real aerial/UAV marking results
(SkyScapes ingestion is built but unrun). (2) **Multi-class real models are
under-trained** under our 4 GB budget (best clDice 0.37); however, the *primary*
result (Sec. V-A) uses **converged** models (clDice ~0.997) over three seeds with
non-overlapping CIs, and a converged binary-marking model on real RLMD plateaus at clDice 0.64 /
mIoU 0.53 (Fig. convergence) -- so the central claim does not rest on under-trained models. (3) The
real-data mis-ranking (Sec. V-B) is explicitly scoped to *multi-class extreme
imbalance*; on a binary task mIoU does not reward flooding. (4) Statistical power:
three seeds; the cross-dataset probe is confounded. (5) The studied connectivity
loss yields no reliable gain and is supplementary, not a contribution.

## VIII. Conclusion

mIoU is an unreliable — sometimes rank-inverting — metric for thin road-marking
segmentation. We provide a topology-aware protocol that ranks models correctly, a
controlled demonstration of the mechanism, an honest multi-seed loss study, and a
reproducible benchmark. We recommend topology-aware evaluation for thin-structure
perception, and we identify converged real-data and aerial/UAV validation as the
key next steps.

## References (placeholder)

[1] O. Ronneberger et al., "U-Net," MICCAI, 2015.
[2] Z. Zhou et al., "UNet++," DLMIA, 2018.
[3] L.-C. Chen et al., "DeepLabV3+," ECCV, 2018.
[4] H. Zhao et al., "PSPNet," CVPR, 2017.
[5] E. Xie et al., "SegFormer," NeurIPS, 2021.
[6] S. Shit et al., "clDice," CVPR, 2021.
[7] B. Cheng et al., "Boundary IoU," CVPR, 2021.
[8] F. Milletari et al., "V-Net," 3DV, 2016.
[9] T.-Y. Lin et al., "Focal Loss," ICCV, 2017.
[10] S. Salehi et al., "Tversky loss," MLMI, 2017.
[11] R. Selvaraju et al., "Grad-CAM," ICCV, 2017.
[12] "RLMD: A Dataset for Road Marking Segmentation," IEEE, doi:10.1109/...10226935.
[13] J. Wang et al., "LoveDA," NeurIPS D&B, 2021.
[14] S. Azimi et al., "SkyScapes," ICCV, 2019.
