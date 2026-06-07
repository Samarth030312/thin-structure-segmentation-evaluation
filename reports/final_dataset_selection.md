# Final Dataset Selection

> **Historical / superseded.** From the project's initial benchmark-building phase. Current narrative: the **width-coupling law** (`reports/width_coupling_theory.md`, `paper_package/final_ieee_paper.pdf`). Experiments used a synthetic generator plus the public datasets RLMD, LoveDA, Massachusetts Roads, UAVid. See `reports/repository_integrity_report.md`.


Selected, with justification, from the ranking in `dataset_ranking.md`. We choose
**three** datasets spanning the three roles a rigorous benchmark needs:
a controlled *causal* probe, a real *aerial-marking* benchmark, and a real
*domain-shift* probe toward the road-marking setting.

## Selected #1 — Controlled Synthetic (primary, for the causal claim)

**Role:** the controlled experiment that *proves* the thin-structure thesis.
**Why selected:** it is the only data source that provides **ground-truth marking
width as an independently controllable variable** (`width_scale ∈ {0.5,1,1.5,2}`,
identical scene seeds across widths). This lets us measure **IoU(width)** and
**clDice(width)** as clean functions of width — the instrument needed to show
that (a) all models degrade as width→thin and (b) the proposed CoRe loss flattens
that degradation. It is also fully reproducible (deterministic, ships with the
repo), so every committed number is real and re-runnable anywhere.
**Limitation (stated):** synthetic photometrics are simpler than real asphalt;
it validates *mechanisms and rankings*, and is complemented by the real datasets
below.

## Selected #2 — SkyScapes (real aerial markings, headline benchmark)

**Role:** the real-data headline benchmark for aerial road markings.
**Why selected:** highest-scoring real dataset (4.18); the only public release
with **fine-grained aerial *marking* classes** (lane lines, dashes, etc.) at the
nadir UAV-like viewpoint that defines the task. Strong annotation quality and
documented research use (ICCV'19). It is the dataset against which our
thin-structure metrics and CoRe loss should be validated in future work.
**Access note:** distributed by DLR under a research agreement; not redistributed
here. The repo's folder-contract + validator ingest it unchanged
(`configs/dataset/`), so headline numbers reproduce with identical commands.

## Selected #3 — IDD (India Driving Dataset) + CeyMo (domain-shift probes)

**Role:** quantify the **domain gap to the road-marking setting** (the project's stated
domain) and to South-Asian roads.
**Why selected:** IDD is the strongest *road-marking* signal (score 3.18, India=5) and
CeyMo the closest South-Asian *marking-rich* set. Both are ground-view, so they
are **not** training-primary; they are the held-out probes for the cross-domain
generalisation study (`cross_dataset_generalization.md`) — measuring how a model
trained on aerial/synthetic markings transfers to real road appearance
(paint wear, occlusion, traffic density, illumination).

## Rejections (with reasons)

| Rejected | Reason |
|---|---|
| BDD100K, Mapillary, ApolloScape | ground/dashcam viewpoint — non-transferable nadir geometry (fails the highest-weight criterion). |
| UAVid, Aeroscapes, Semantic-Drone | UAV viewpoint but **no marking-level classes** (road is one class). |
| DeepGlobe, LoveDA | aerial but **roads/land-cover, not markings**. |
| HighRPD | drone imagery but labels are **pavement distress**, not markings. |
| TRoM | excellent marking labels but **ground viewpoint** and not road-marking. |

## Resulting experimental matrix

| Dataset | Train? | Eval? | Purpose |
|---|:--:|:--:|---|
| Controlled Synthetic | ✅ | ✅ (+ width series) | causal thin-structure claim; loss ablation |
| SkyScapes | ✅ | ✅ | real aerial-marking headline numbers |
| IDD / CeyMo | – | ✅ (held-out) | road-marking/South-Asian domain-shift measurement |

This trio gives us **internal validity** (controlled synthetic), **external
validity** (SkyScapes real aerial), and **domain relevance** (IDD/CeyMo) — the
three legs a reviewer looks for.
