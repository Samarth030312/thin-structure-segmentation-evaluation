# UAV Data Acquisition

Real datasets acquired for the UAV validation campaign, with provenance,
checksums, download/preprocessing scripts, and statistics. Nothing fabricated.

## 1. Acquired datasets

| Dataset | Source | Download | Preprocess | Ingested |
|---|---|---|---|---|
| **UAVid** | HF `arakesh/uavid-15-hq-mixedres` (parquet) | `huggingface_hub.snapshot_download` (no creds) | `scripts/prepare_uavid.py` | 101 train / 24 test, binary road |
| **LoveDA** | HF `chloechia/loveda` | `huggingface_hub` (no creds) | `scripts/prepare_real.py` (id mode) | 136 train / 41 test, binary road |

## 2. Checksums (acquired UAVid parquet shards, md5 prefix)

```
4ae5b108446b  test-00000-of-00003.parquet
a41892892bde  train-00000-of-00006.parquet
a281093c6b0b  train-00001-of-00006.parquet
958f6332ba6a  train-00002-of-00006.parquet
```
(3 of 6 train + 1 of 3 test shards downloaded = ~125 labelled UAV frames; the
remaining shards download with the same one-line command if more data is wanted.)

## 3. Download + preprocess commands (reproducible)

```bash
# UAVid (true low-altitude UAV)
python - <<'PY'
from huggingface_hub import snapshot_download
snapshot_download("arakesh/uavid-15-hq-mixedres", repo_type="dataset",
  local_dir="datasets/_real_raw/uavid_pq",
  allow_patterns=["data/train-0000[0-2]-of-00006.parquet","data/test-00000-of-00003.parquet"])
PY
python scripts/prepare_uavid.py --raw datasets/_real_raw/uavid_pq/data --out datasets/uavid --size 768
python scripts/dataset_validator.py --root datasets/uavid --num-classes 2

# LoveDA (aerial) — see scripts/prepare_real.py (already ingested in datasets/loveda)
```

## 4. Statistics

| | UAVid | LoveDA |
|---|---|---|
| Viewpoint | low-altitude UAV (oblique) | aerial / satellite |
| Native resolution | 3840×2160 | 1024² |
| Ingested resolution | 768² (train at 512²) | 384² |
| Train / test frames | 101 / 24 | 136 / 41 |
| Road pixel share | **11.3 %** | ~13 % |
| Task | binary road vs background | binary road vs background |
| Validation | PASSED (0 errors) | PASSED (0 errors) |

## 5. Honest limitations of the acquisition
- Both datasets label **road surface**, not road *markings* (the marking-specific
  aerial sets are access-gated; see `uav_dataset_survey.md`). The thin-structure
  claim is validated on the road class (thin/distant roads in the oblique UAV
  view), not on markings.
- UAVid is genuine low-altitude UAV; LoveDA is aerial/satellite — together they
  cover two real viewpoints. A subset of shards was used for compute reasons; the
  full set is one command away.
