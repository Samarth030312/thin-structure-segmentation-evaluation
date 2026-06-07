# Beyond mIoU: A Thin-Structure-Aware Benchmark and Connectivity Loss for UAV Road-Marking Segmentation

> **Historical / superseded.** From the project's initial benchmark-building phase. Current narrative: the **width-coupling law** (`reports/width_coupling_theory.md`, `paper_package/final_ieee_paper.pdf`). Experiments used a synthetic generator plus the public datasets RLMD, LoveDA, Massachusetts Roads, UAVid. See `reports/repository_integrity_report.md`.


*Draft for IEEE ITSC / T-ITS submission. All quantitative results are produced by
the accompanying open-source framework on a single GTX-1650 GPU and are
reproducible via the cited scripts.*

---

## Abstract

Road markings in unmanned-aerial-vehicle (UAV) imagery are **thin** (2-8 px) and
**sparse** (<5 % of pixels), yet the field evaluates them with mean
Intersection-over-Union (mIoU) — a region-overlap metric we show is **ill-suited
and actively misleading** for thin structures. We make three contributions.
**(i)** A *thin-structure evaluation protocol* (centerline-Dice, Boundary-IoU,
tolerance-IoU, and a width-stratified analysis) that measures *topology* and
*detection* rather than pixel overlap. **(ii)** Empirical evidence on **real data**
(RLMD, 25 marking classes) that mIoU does not merely under-measure thin structures
but **inverts model rankings**: in a controlled loss ablation, mIoU ranks a
frame-flooding model (PixelAcc 0.009) *first*, while the genuinely best perception
model has 5× lower mIoU — corroborated on a width-controlled synthetic benchmark
where mIoU drops to 0.35 on 2-px markings that are in fact correctly recovered
(tolerance-IoU 0.97). **(iii)** A study of connectivity-aware losses, including a
proposed Connectivity-Recall (*CoRe*) loss: CoRe improves topology on the
controlled synthetic benchmark but, across **3 seeds** on real data, **ties
CE+Dice** (clDice 0.405 vs 0.406; a single-seed CE+Dice advantage does not survive
multi-seed) — an honest result that controlled-benchmark loss wins must be
multi-seed-validated, while recall-only Tversky destroys topology. Code, real-data
ingestion, and a C++/TensorRT deployment path are released.

## 1. Introduction

UAV-based road-marking perception supports HD-map maintenance, infrastructure
auditing, and lane-level localisation. The nadir/oblique viewpoint makes markings
*thin and sparse*, and the dominant intra-domain shift is **altitude → marking
width in pixels**. Despite this, the literature reports mIoU/Dice — metrics
dominated by interior pixels and blind to connectivity. We ask: *does mIoU
faithfully measure thin-marking quality, and does it select the right model and
loss?* We find it does not, and we provide the metrics and loss that do.

**Contributions.** (1) a thin-structure evaluation protocol; (2) the finding —
on **real data** and a controlled synthetic benchmark — that mIoU mis-measures
and *mis-ranks* thin-marking perception; (3) a connectivity-loss study with the
proposed CoRe loss and an honest multi-seed analysis (CoRe ties CE+Dice on real
data; a single-seed win does not survive);
(4) an open, reproducible framework with real-data ingestion + a C++ deploy path.

## 2. Related Work

*Architectures:* U-Net [Ronneberger'15], U-Net++ [Zhou'18], DeepLabV3+
[Chen'18], PSPNet [Zhao'17], SegFormer [Xie'21]. *Thin/tubular structures:*
clDice and the soft-skeleton [Shit'21] for vessels/road networks; Boundary-IoU
[Cheng'21]. *Losses:* Dice [Milletari'16], Focal [Lin'17], Tversky [Salehi'17].
*Aerial markings:* SkyScapes [Azimi'19], Aerial-LaneNet [Azimi'19]. To our
knowledge, **topology-aware metrics and losses have not been brought to UAV
road-marking segmentation, nor has the width-dependence of mIoU been quantified**
for this task. (Full review: `literature_review.md`.)

## 3. Method

### 3.1 Thin-structure evaluation protocol
For binary any-marking masks we report: **clDice** (harmonic mean of skeleton
precision/sensitivity); **Boundary-IoU** (IoU on a d-px boundary band);
**tolerance-IoU / centerline-F1** (detection within τ px of the GT centerline);
and **width-stratified IoU/clDice**, where the controlled GT width is the
independent variable. (`src/uavroadmark/metrics/thin_structure.py`.)

### 3.2 CoRe loss
$$\mathcal{L}_{CoRe}=w_{ce}\mathcal{L}_{CE}+w_{r}\mathcal{L}_{Dice}+w_{t}(1-\text{softClDice}),$$
with a soft skeleton from iterative soft erosion/dilation [Shit'21] on the
any-marking probability $1-\text{softmax}_0$. The CE term **calibrates**
background (preventing the over-prediction of recall-only losses); the Dice term
drives overlap; the clDice term enforces *connectivity*. A warm-up ramps $w_t$
from 0 so meaningless early skeletons do not destabilise training.
(`src/uavroadmark/losses/topology.py`.)

### 3.3 Benchmark
A deterministic generator renders UAV-like asphalt with the 7-class road-marking
marking taxonomy at controllable width-scale, producing identical scenes at
multiple widths — enabling a clean controlled study where real width-labelled
UAV data does not exist (`dataset_ranking.md`). Real-data protocol (SkyScapes,
IDD, CeyMo) in `final_dataset_selection.md`.

## 4. Experiments

U-Net/U-Net++/DeepLabV3+/PSPNet/SegFormer, ResNet/MiT encoders; 256², 25 epochs,
AdamW, cosine, seed 42; one GTX-1650. Metrics: standard + thin-structure.

### 4.1 mIoU mis-measures thin markings (headline)
Training at 4 px and testing across widths (Fig. `width_study.png`):

| width | mIoU | TolIoU | clDice |
|---|---|---|---|
| 2 px | **0.35** | **0.97** | **1.00** |
| 4 px | 0.94 | 1.00 | 1.00 |
| 8 px | 0.47 | 0.98 | 0.98 |

At 2 px, **mIoU=0.35 suggests failure while TolIoU=0.97/clDice=1.0 show the lines
are correctly and continuously detected.** mIoU conflates *detection* with
*exact width matching*; the thin-structure protocol separates them.

### 4.2 Architecture mis-ranking

| Arch | params | mIoU | BoundaryIoU |
|---|---|---|---|
| U-Net | 24.4M | 0.938 | 0.986 |
| U-Net++ | 26.1M | 0.933 | **0.987** |
| DeepLabV3+ | 26.7M | 0.878 | 0.898 |
| SegFormer | **3.7M** | 0.847 | 0.918 |
| PSPNet | 46.7M | 0.634 | 0.620 |

DeepLabV3+ and SegFormer **swap** rank between mIoU and BoundaryIoU; mIoU alone
would pick the wrong model. PSPNet's coarse decoder is decisively worst on
boundaries.

### 4.3 Loss ablation — synthetic (U-Net)

| Loss | mIoU | PixelAcc | clDice | BoundaryIoU |
|---|---|---|---|---|
| **CoRe (ours)** | **0.945** | 0.999 | **0.999** | **0.986** |
| CE+Dice | 0.938 | 0.999 | 0.998 | 0.986 |
| Tversky (β=.7) | 0.787 | 0.512 | 0.219 | 0.055 |
| clDice-only | 0.032 | 0.111 | 0.450 | 0.291 |

On the *controlled synthetic* benchmark CoRe ≥ CE+Dice everywhere; recall-only
Tversky **floods the frame** (PixelAcc 0.51); clDice-only is degenerate.

### 4.4 Loss ablation — REAL data (RLMD, U-Net++, clean same-architecture)

| Loss | mIoU | **PixelAcc** | clDice | clPrecision | clRecall |
|---|---|---|---|---|---|
| **CE+Dice** | 0.029 | 0.983 | **0.373** | **0.907** | **0.356** |
| CoRe (ours) | 0.005 | 0.981 | 0.275 | 0.896 | 0.211 |
| Tversky (β=.7) | **0.144** | **0.009** | 0.084 | 0.133 | 1.000 |

Two real-data findings. **(a) mIoU inverts the ranking:** it crowns Tversky
(0.144) — a model that floods 99 % of pixels (PixelAcc 0.009, clPrecision 0.13) —
while the best perception model (CE+Dice) scores 5× lower mIoU. **(b) CoRe and
CE+Dice are tied across seeds:** a single-seed CE+Dice advantage (clDice 0.37 vs
0.28, seed 42, p<0.001) **does not survive multi-seed** — over seeds 42/123/999,
CE+Dice 0.405±0.058 vs CoRe 0.406±0.141 (Δ=−0.001, CI [−0.18,0.18]; CoRe wins at
seed 999). CoRe adds variance, not reliable gain. *(We document two
self-corrections: an early confound, then a single-seed artifact — the value of
controlled, multi-seed validation.)*

## 5. Discussion & Limitations

The **metric thesis is validated on real data** (the mIoU mis-ranking is RLMD, not
synthetic) and the *mechanism* is isolated synthetically (mIoU couples detection
with exact-width matching). The **CoRe loss ties CE+Dice across seeds** (higher
variance) — a reminder that controlled-benchmark loss wins must be multi-seed-
validated in the wild before being claimed.
**Limitations:** real runs are compute-bounded (500-img subset, 12 epochs, 384²,
4 GB GPU) — absolute numbers will rise, but the mis-ranking and CoRe-tie
conclusions are budget-independent; RLMD is ground-view (real markings), and the
UAV-viewpoint confirmation (SkyScapes) is built and drop-in ready.

## 6. Conclusion

For UAV/road-marking perception, **report topology/boundary metrics (clDice,
clPrecision), not mIoU alone** — on real data mIoU can rank the worst model first;
use a **skip-connection decoder** (U-Net++ for accuracy, SegFormer-B0 for
deployment) with the **CE+Dice** loss (CoRe ties it across seeds, with higher
variance); and deploy via ONNX/TensorRT. The released framework, real-data
ingestion, benchmark, and C++ path make every result reproducible and deployable.

## Reproducibility
`bash scripts/run_loss_ablation.sh`, `bash scripts/run_arch_sweep.sh`,
`python scripts/run_width_study.py …`, `python scripts/run_failure_analysis.py …`,
`python scripts/run_hpo.py …`. Hardware: `reports/system_report.md`.

## References
Abbreviated; see `literature_review.md` and `dataset_ranking.md` for full lists.
Ronneberger'15; Zhou'18; Chen'18; Zhao'17; Xie'21; Shit'21 (clDice);
Cheng'21 (Boundary-IoU); Milletari'16; Lin'17; Salehi'17; Azimi'19 (SkyScapes,
Aerial-LaneNet); Varma'19 (IDD); Jayasinghe'22 (CeyMo).
