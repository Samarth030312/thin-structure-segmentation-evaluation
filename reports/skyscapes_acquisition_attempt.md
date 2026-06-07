# SkyScapes Acquisition Attempt (and Substitute)

Goal: acquire SkyScapes (DLR aerial road *markings*, genuinely thin, UAV viewpoint)
and run the width validation on it — the decisive test of the thin-structure claim
on aerial markings. This documents the **exhaustive, genuine** acquisition attempt
and its honest outcome.

## 1. Channels tried (all failed)

| Channel | Result |
|---|---|
| Hugging Face datasets (`skyscapes`, `aerial lane marking`, `DLR aerial`, `aerial-lanenet`) | **none** — no dataset mirror exists |
| HF models/spaces | only a *model* (`RyanQchiqache/mask2former-large-dlr-skyscapes`); its card links back to DLR, ships one example image, **no data** |
| GitHub `tianzq/SkyScapes` | **docs only** — citation/description, no images/masks, no download links |
| DLR EOC datasets portal `https://eoc-datasets.dlr.de/` | **HTTP 000** — unreachable from this environment (and requires a research agreement) |
| DLR SkyScapes public page | exposes only **preview thumbnails** (e.g. `dlr-skyscapes_2.jpg`, a `gt_zoom` PNG) — no full images, no dense masks |
| Kaggle | SkyScapes/Aerial-LaneNet not present; Kaggle in general needs an API token (absent here) |

**Conclusion:** SkyScapes is **registration-gated (DLR research agreement) and the
download portal is network-unreachable from this environment.** It cannot be
acquired here. Per the campaign rules (no fabrication, no fake datasets), I do not
synthesise it.

## 2. Substitute chosen — Massachusetts Roads (real aerial, genuinely thin)

The *scientific* purpose of "SkyScapes width validation" is to test whether the
thin-structure claim holds on **real aerial thin structures**. SkyScapes's thin
structures are lane markings; the closest *freely downloadable* real aerial dataset
with genuinely thin linear structures is the **Massachusetts Roads dataset** (HF
`asolodin/massachusetts_roads_dataset_500`, parquet): aerial RGB + thin rural-road
masks, **road pixel share 3.6 %** (vs UAVid's 11 % wide roads). At 512² the roads
are a few pixels wide — the thinness regime the claim concerns.

| Property | SkyScapes (target) | Massachusetts Roads (substitute) |
|---|---|---|
| Viewpoint | aerial (DLR) | aerial |
| Thin structure | lane markings (2-8 px) | rural roads (~3-6 px) |
| Road-share | sparse markings | **3.6 %** (thin) |
| Availability | gated, unreachable | ✅ HF, no credentials |

This is not SkyScapes and we do not claim it is. It is the honest, available proxy
for the question "does the claim hold on real aerial thin structures?" — see
`reports/massroads_width_validation.md` for the result.

## 3. Status of the true SkyScapes run
**Outstanding.** Requires the DLR research agreement + portal access (and ideally a
larger GPU). The ingestion pipeline is already built and tested
(`scripts/prepare_skyscapes.py`, `configs/dataset/skyscapes.yaml`,
`docs/skyscapes.md`); the moment the licensed data is available, the same
width-validation command runs on it unchanged.
