# Dataset Licences and Attribution

This repository's **code** is MIT-licensed (`LICENSE`). It **does not redistribute
any dataset.** Ingestion scripts (`scripts/prepare_*.py`) fetch data from each
dataset's public source; you are responsible for complying with each dataset's
licence. Several are **non-commercial / research-only** — do not use them
commercially.

| Dataset | Used for | Source | Licence (verify at source) |
|---|---|---|---|
| **RLMD** (Road Line Marking Dataset) | real ground-view markings; imbalance study; converged binary model | Hugging Face `veetinator/Road_Line_Marking_Dataset` | research use — check the dataset card |
| **LoveDA** | real aerial roads; law validation | Hugging Face `chloechia/loveda` | **CC-BY-NC 4.0** (non-commercial) |
| **Massachusetts Roads** | real aerial thin roads; law validation | Hugging Face `asolodin/massachusetts_roads_dataset_500` | research/academic use — check the source |
| **UAVid** | real low-altitude UAV roads; safe-zone validation | Hugging Face `arakesh/uavid-15-hq-mixedres` (mirror of DLR/UAVid) | **research-only**; see the UAVid licence |
| **SkyScapes** (NOT acquired) | would-be aerial-marking validation | DLR EOC portal | DLR research agreement (licence-gated; unreachable here) |
| Synthetic generator | controlled width study | in-repo `src/uavroadmark/data/synthetic.py` | MIT (part of this repo) |

## Notes
- **Non-commercial restriction:** LoveDA (CC-BY-NC) and UAVid (research-only) may
  **not** be used commercially. The MIT licence applies to *this repository's code
  only*, not to any dataset.
- **No redistribution:** raw datasets and trained checkpoints are git-ignored
  (`.gitignore`) and are not part of any release.
- **Attribution:** when reporting results, cite the original dataset papers (RLMD,
  LoveDA, Massachusetts Roads / Mnih, UAVid) per their terms.
