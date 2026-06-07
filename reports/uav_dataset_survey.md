# UAV Dataset Survey

Exhaustive search for UAV/aerial road and road-marking segmentation datasets,
with **verified** availability (we attempted to acquire each). Sources: Hugging
Face, Kaggle, Papers-with-Code, GitHub, DLR, academic releases.

## 1. Catalogue

| Dataset | View | Road / marking labels | Res | License | Acquired here? | Notes |
|---|---|---|---|---|---|---|
| **UAVid** (HF `arakesh/uavid-15-hq-mixedres`) | **low-altitude UAV (oblique)** | **road** (8-class semantic) | 3840×2160 | research | ✅ **YES** (HF parquet, no creds) | the canonical UAV semantic benchmark; road = (128,64,128) |
| **LoveDA** (HF `chloechia/loveda`) | aerial/satellite | road (7-class land-cover) | 1024² | CC-BY-NC | ✅ **YES** (HF, no creds) | remote-sensing, not low-altitude UAV |
| **LandCover.ai** (HF `MortenTabaka/...`) | aerial | road (5-class) | ~9000² tiles | CC-BY-NC-SA | available (2.5 GB, HF) | aerial; not yet ingested (optional 3rd) |
| UAVid-RIS (HF `lironui/UAVid-RIS`) | UAV | per-class masks incl. Road | 1024² | research | ⚠️ masks only | **no RGB images** in the release → unusable for training |
| Aeroscapes (Kaggle) | UAV | road (11-class) | ~1280×720 | research | ❌ Kaggle token req. | true UAV; gated |
| Semantic Drone (Kaggle `bulentsiyah`) | aerial drone | paved-area (24-class) | 6000×4000 | research | ❌ Kaggle token req. | no token available here |
| **SkyScapes** / **Aerial-LaneNet** (DLR) | aerial | **lane markings** (12/31-class) | high | DLR agreement | ❌ registration | the *ideal* aerial-marking sets; access-gated |
| DroneDeploy (`dd-ml-segmentation`) | aerial | road (7-class) | high | research | ❌ S3 download script | not pursued (LoveDA/UAVid suffice) |
| DeepGlobe Road (Kaggle) | aerial/sat | road (binary) | 1024² | research | ❌ Kaggle token | road extraction, no markings |
| Traffic-Aerial / Drone-UAV (Kaggle) | UAV | vehicles (detection) | var | open | ❌ not segmentation | object detection, not road seg |

## 2. The honest gap (unchanged, now documented with download attempts)

**No freely-downloadable dataset provides low-altitude UAV imagery with dense
road-*marking* masks.** The aerial-*marking* sets (SkyScapes, Aerial-LaneNet) are
DLR-registration-gated; the true-UAV sets with road markings (Aeroscapes, Semantic
Drone) are Kaggle-token-gated and **no token is available in this environment**.
What *is* freely available is **UAV/aerial road-*surface* segmentation** (UAVid,
LoveDA, LandCover.ai). We therefore validate the thin-structure claim on the
**road class** of real UAV/aerial data (roads, especially distant/rural ones in an
oblique UAV view, are thin in pixels), via a width-stratified analysis — a
legitimate test of the same mechanism without fabricating marking data.

## 3. Ranking

By **publication value × road-marking suitability × UAV authenticity × ease of
acquisition**:

| Rank | Dataset | Pub | Marking | UAV-auth | Ease | Use |
|---|---|:--:|:--:|:--:|:--:|---|
| 1 | **UAVid** | ★★★★ | ★★ (road only) | ★★★★★ | ★★★★ (HF) | **primary UAV validation** |
| 2 | **LoveDA** | ★★★ | ★★ (road only) | ★★★ (aerial) | ★★★★★ (have it) | **second aerial dataset** |
| 3 | SkyScapes | ★★★★★ | ★★★★★ (markings) | ★★★★ | ★ (gated) | ideal; future work (ingestion built) |
| 4 | LandCover.ai | ★★★ | ★★ (road) | ★★★ | ★★★★ (HF) | optional 3rd aerial |
| 5 | Aeroscapes | ★★★ | ★★ | ★★★★★ | ★ (Kaggle token) | future work |

**Selected for this campaign:** UAVid (genuine UAV) + LoveDA (aerial), both real,
both acquired and validated, road as the thin-structure target. SkyScapes remains
the ideal next acquisition (ingestion already built, `docs/skyscapes.md`).
