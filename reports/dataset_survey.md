# Dataset Survey — Road/Lane-Marking & Aerial Segmentation

> **Historical / superseded.** From the project's initial benchmark-building phase. Current narrative: the **width-coupling law** (`reports/width_coupling_theory.md`, `paper_package/final_ieee_paper.pdf`). Experiments used a synthetic generator plus the public datasets RLMD, LoveDA, Massachusetts Roads, UAVid. See `reports/repository_integrity_report.md`.


> Comprehensive search across Hugging Face, Kaggle, Papers-with-Code, GitHub, and
> academic repositories. 14 candidates scored on 9 criteria. **Datasets actually
> downloaded and ingested in this repo are marked ✅ REAL.** This supersedes the
> earlier `dataset_ranking.md` with verified availability.

## 1. Scoring (1-5 per criterion; weighted toward task relevance)

| # | Dataset | View | Marking labels | Relev | AnnoQ | Res | ClassRich | UAV | India | Maint/Lic | Adopt | **Score** | Access |
|---|---|---|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|---|
| 1 | **RLMD** (veetinator/Road_Line_Marking) | Ground | **Yes (25 cls)** | 5 | 4 | 5 | **5** | 1 | 2 | 5 (MIT) | 3 | **4.05** | ✅ **REAL (HF, 1.36 GB, ingested)** |
| 2 | **SkyScapes-Lane** (DLR) | **Aerial** | **Yes (13 cls)** | 5 | 5 | 5 | 4 | 5 | 1 | 3 (agree.) | 4 | **4.30** | ingestion ready; needs DLR agreement |
| 3 | **LandCover.ai Aerial** (MortenTabaka) | **Aerial** | No (road class) | 3 | 4 | 5 | 2 | 5 | 1 | 4 (CC) | 4 | 3.20 | ✅ REAL-available (HF, 2.5 GB) |
| 4 | gymprathap Aerial Semantic | Aerial | No | 3 | 3 | 4 | 3 | 5 | 1 | 4 | 2 | 2.80 | ✅ REAL-available (HF, 31 MB) |
| 5 | AerialLanes18 / Aerial-LaneNet | Aerial | **Yes (lane)** | 5 | 4 | 5 | 3 | 5 | 1 | 3 | 3 | 3.74 | request (DLR) |
| 6 | CeyMo (Sri Lanka) | Ground | **Yes (11 cls)** | 4 | 4 | 4 | 4 | 1 | 3 | 4 | 3 | 3.10 | GitHub |
| 7 | TRoM (Tsinghua) | Ground | **Yes (19 cls)** | 4 | 4 | 4 | 4 | 1 | 2 | 3 | 3 | 2.90 | request |
| 8 | IDD (India Driving) | Ground | Partial (lane/road) | 3 | 4 | 4 | 2 | 1 | **5** | 4 | 4 | 3.18 | registration |
| 9 | UAVid | **Aerial** | No (road=1) | 3 | 4 | 5 | 1 | 5 | 1 | 4 | 5 | 2.94 | registration |
| 10 | DeepGlobe Road | Aerial/sat | No (binary road) | 3 | 4 | 4 | 1 | 4 | 1 | 5 | 5 | 3.06 | Kaggle |
| 11 | BDD100K | Ground | Lane (lines) | 3 | 4 | 4 | 2 | 1 | 1 | 5 | 5 | 2.70 | registration |
| 12 | Mapillary Vistas | Ground | **Yes (markings)** | 4 | 5 | 5 | 4 | 1 | 3 | 5 | 5 | 3.34 | registration |
| 13 | KITTI-Road / TuSimple / CULane | Ground | Lane | 3 | 4 | 4 | 2 | 1 | 1 | 5 | 5 | 2.7-2.9 | open |
| 14 | hf-vision road-pothole-seg | Ground | No (pothole) | 2 | 3 | 4 | 1 | 1 | 1 | 3 | 2 | 1.9 | ✅ HF |

## 2. The hard finding (research motivation)

**No public dataset combines all three of {UAV viewpoint, dense marking labels,
road-marking domain}.** The space splits into:
- **on-task markings, ground view** (RLMD ✅, CeyMo, TRoM, Mapillary, IDD),
- **aerial view, no marking classes** (UAVid, LandCover ✅, DeepGlobe),
- **aerial + markings, non-road-marking** (SkyScapes, AerialLanes18).

This gap is itself a contribution and shapes our 3-dataset strategy.

## 3. Selected real datasets (what we actually use)

| Role | Dataset | Status | Why |
|---|---|---|---|
| **Primary, on-task** | **RLMD** (25 marking classes) | ✅ **ingested & trained** | the only freely-downloadable, dense, multi-class *road-marking* dataset; real driving scenes; markings are thin → directly tests the thesis |
| **Aerial / UAV-centric** | SkyScapes-Lane (13 cls) | ingestion built+tested | correct viewpoint + marking classes; drop-in ready (`docs/skyscapes.md`) |
| **Large-scale aerial** | LandCover.ai (MortenTabaka) | available (HF) | real large aerial benchmark for the cross-view generalization probe |
| **road-marking domain probe** | IDD | documented | the strongest road-marking signal (held-out domain-shift eval) |

## 4. Controlled synthetic (supporting, not primary)

The width-controlled synthetic benchmark remains, but **only to isolate variables**
(it is the sole source of ground-truth marking-*width* control). Per the study objective,
**all major conclusions are validated on RLMD (real data)**; synthetic experiments
support the mechanism.

## 5. Sources
RLMD: Road Line & Marking Dataset, IEEE (doi 10.1109/...10226935), HF
`veetinator/Road_Line_Marking_Dataset` (MIT). SkyScapes: Azimi et al., ICCV 2019.
Aerial-LaneNet: Azimi et al., TGRS 2019. CeyMo: Jayasinghe et al., WACV 2022.
IDD: Varma et al., WACV 2019. LandCover.ai: Boguszewski et al., 2021.
UAVid: Lyu et al., 2020. Mapillary: Neuhold et al., 2017.
