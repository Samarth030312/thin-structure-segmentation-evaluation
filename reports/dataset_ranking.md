# Dataset Ranking — UAV / Aerial Road-Marking Segmentation

> **Historical / superseded.** This document is from the project's initial benchmark-building phase. The project's actual contribution and current narrative is the **width-coupling law** for thin-structure evaluation metrics — see `reports/width_coupling_theory.md` and `paper_package/final_ieee_paper.pdf`. The "target UAV dataset" referenced below was an aspirational road-marking set that was **never acquired**; the experiments actually used a synthetic generator and the public datasets RLMD, LoveDA, Massachusetts Roads, and UAVid. See `reports/repository_integrity_report.md`.


> Research-phase update to `dataset_selection_report.md`. We searched Hugging
> Face, Kaggle, Papers-with-Code, GitHub, and academic repositories for datasets
> relevant to **UAV/aerial road- and lane-marking segmentation**, with an
> road-marking-domain emphasis, and scored them on eight criteria.

## 1. Key finding (a publishable motivation)

**There is no public, redistributable, India-specific UAV road-*marking*
segmentation dataset with dense masks.** The originally-named "the target UAV dataset" source
is not locatable as an open release. India *driving* data exists (IDD) but is
ground-level dashcam; UAV data with *marking-level* labels exists only for other
domains (Germany/China). **This domain-and-viewpoint gap is itself a research
contribution**: it motivates (a) a controlled study and (b) a cross-domain
generalisation analysis, and it is the honest reason our controlled experiments
use a width-parametrised synthetic benchmark.

## 2. Scoring framework

Each dataset scored 1–5 on: **AnnoQ** (annotation quality), **Size**,
**Res** (resolution), **UAV** (UAV/aerial relevance), **India** (road-marking
relevance), **Balance** (class balance for *markings*), **Docs** (documentation),
**Adopt** (research adoption). Weighted total uses the task weights from
`dataset_selection_report.md` (UAV and marking-labels dominate).

| Dataset | View | Marking labels | AnnoQ | Size | Res | UAV | India | Balance | Docs | Adopt | **Score/5** |
|---|---|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| **SkyScapes** (DLR) | Aerial (nadir) | **Yes, fine-grained (lane markings, 31 cls inc. 12 marking cls)** | 5 | 3 | 5 | 5 | 1 | 3 | 4 | 4 | **4.18** |
| **AerialLanes18 / Aerial-LaneNet** | Aerial | **Yes (lane markings)** | 4 | 2 | 5 | 5 | 1 | 3 | 3 | 3 | **3.74** |
| **Controlled Synthetic** (this work) | UAV-like (nadir) | **Yes (7 cls, width-controlled)** | 4 | 5 | 4 | 4 | 3* | 4 | 5 | 1 | **3.86** |
| UAVid | UAV (oblique) | No (road = 1 class) | 4 | 3 | 5 | 5 | 1 | 1 | 4 | 5 | 2.94 |
| Aeroscapes | UAV | No marking classes | 3 | 3 | 4 | 5 | 1 | 1 | 3 | 3 | 2.66 |
| CeyMo | Dashcam | **Yes (11 marking cls)** | 4 | 3 | 4 | 1 | 3** | 4 | 4 | 3 | 3.10 |
| TRoM (Tsinghua) | Ground | **Yes (19 cls)** | 4 | 2 | 4 | 1 | 2 | 4 | 3 | 3 | 2.74 |
| IDD (India Driving) | Dashcam | Partial (road, lane) | 4 | 5 | 4 | 1 | **5** | 2 | 4 | 4 | 3.18 |
| DeepGlobe Road Extr. | Aerial/sat | No (road binary) | 4 | 5 | 4 | 4 | 1 | 1 | 5 | 5 | 3.06 |
| LoveDA | Aerial/sat | No (land-cover) | 4 | 5 | 4 | 4 | 1 | 1 | 5 | 4 | 3.02 |
| Semantic Drone (Kaggle) | Aerial | No marking class | 3 | 2 | 5 | 5 | 1 | 1 | 2 | 3 | 2.58 |
| HighRPD | Drone | No (pavement *distress*) | 4 | 4 | 5 | 5 | 1 | 1 | 3 | 2 | 2.92 |
| BDD100K | Dashcam | Lane (lines) | 4 | 5 | 4 | 1 | 1 | 2 | 5 | 5 | 2.70 |
| Mapillary Vistas | Ground | Yes (markings) | 5 | 5 | 5 | 1 | 3 | 4 | 5 | 5 | 3.34 |

\* synthetic can be *styled* toward road-marking statistics (wear, occlusion, density); \*\* CeyMo (Sri Lanka) is the closest public South-Asian marking domain.

## 3. Observations

- **For the UAV viewpoint + marking labels intersection, the field is essentially
  SkyScapes and AerialLanes18.** Everything else fails one of the two
  highest-weight criteria.
- **CeyMo and IDD are the best *road-marking/South-Asian* signals**, but both are
  ground-view — useful only as **domain-shift probes**, not primary training.
- **The controlled synthetic benchmark scores competitively** *for this thesis*
  because it uniquely provides **ground-truth marking width as a controlled
  variable** — the exact instrument the thin-structure study needs. No real
  dataset offers per-pixel width control.

## 4. Sources

- SkyScapes (DLR): Azimi et al., *SkyScapes: Fine-Grained Semantic Understanding of Aerial Scenes*, ICCV 2019.
- Aerial-LaneNet / AerialLanes18: Azimi et al., *Aerial LaneNet: Lane-Marking Semantic Segmentation in Aerial Imagery*, IEEE TGRS 2019 (arXiv:1803.06904).
- CeyMo: Jayasinghe et al., WACV 2022 (arXiv:2110.11867).
- UAVid: Lyu et al., ISPRS J. 2020. · IDD: Varma et al., WACV 2019.
- DeepGlobe: Demir et al., CVPR-W 2018. · LoveDA: Wang et al., NeurIPS D&B 2021.
- HighRPD: PMC11872502. · Mapillary Vistas: Neuhold et al., ICCV 2017.

[SkyScapes/Aerial-LaneNet](https://arxiv.org/pdf/1803.06904) ·
[CeyMo](https://arxiv.org/pdf/2110.11867) ·
[Aerial road 3D modeling survey](https://www.tandfonline.com/doi/full/10.1080/17538947.2024.2365970) ·
[HighRPD](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11872502/)
