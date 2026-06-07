# Part 5 — Datasets

Five data sources span the spectrum from fully-controlled synthetic to genuine
low-altitude UAV. Each was chosen for a specific scientific role. The honest theme:
**no freely available dataset has aerial road *markings*** (the ideal), so we
triangulate with synthetic markings and real thin *roads*.

## 5.1 Synthetic road markings (controlled)

- **Origin.** Generated in-repo (`src/uavroadmark/data/synthetic.py`-style generator;
  the width series lives in `datasets/width_series/`). A renderer paints lines/curves
  of a *chosen* width onto a canvas, with a pixel-perfect label.
- **Annotation style.** Exact, by construction — the GT is the rendering itself.
- **Resolution.** 256² (controlled experiments), configurable.
- **Why selected.** It is the only way to make **width an independent variable** with
  everything else fixed. The whole law rests on being able to say "same scene, only
  the width changed." You cannot do that with real data.
- **Limitations.** Not photorealistic; appearance gap to real imagery. But for an
  *evaluation-metric* study, appearance is irrelevant — geometry is what matters.
- **Role.** The controlled width study and the geometry-only robustness study
  (Part 8). Provides the dense `Gap(w)` curve.

## 5.2 RLMD — Road Line Marking Dataset (real, ground-view)

- **Origin.** Real dashcam road imagery, Hugging Face
  `veetinator/Road_Line_Marking_Dataset`; ingested via `scripts/prepare_real.py`.
- **Annotation style.** 25 marking classes (lane lines, arrows, stop lines, …),
  pixel-level.
- **Resolution.** Ingested at 384² for the multi-class runs.
- **Statistics.** Markings occupy **< 2 %** of pixels; class imbalance **609:1**
  between the most and least common marking.
- **Why selected.** The only *real road-marking* dataset that is freely available —
  genuinely thin structures with real appearance variation. Used for (a) the loss
  ablation and the **mIoU mis-ranking under imbalance** result, and (b) a converged
  **binary** marking model (clDice 0.64) rebutting "under-trained."
- **Limitations.** Ground-view (dashcam), not aerial/UAV. The 25-class models are
  under-trained on a 4 GB GPU (best clDice 0.37) — which is why the *binary* version
  (a well-posed task) is used for the convergence claim.
- **Role.** Real thin *markings*; the imbalance phenomenon.

## 5.3 LoveDA — aerial land-cover (real, aerial)

- **Origin.** Aerial/satellite imagery, HF `chloechia/loveda`; 7 land-cover classes
  including **road**.
- **Annotation style.** Semantic land-cover; we binarise to road vs background.
- **Resolution.** 1024² native, ingested/trained at 384².
- **Statistics.** Road ≈ 13 % of pixels; roads are often **thin** (rural/narrow),
  mean width < 6 px at the working resolution.
- **Why selected.** A real *aerial* viewpoint with thin road structures — a step
  toward UAV without the gating of marking datasets.
- **Limitations.** Satellite/aerial remote-sensing, not low-altitude UAV; land-cover
  road, not markings.
- **Role.** Real-aerial **validation** of the width-coupling law (gap +0.22).

## 5.4 Massachusetts Roads (real, aerial, thin) — the SkyScapes substitute

- **Origin.** Aerial imagery with road masks, HF
  `asolodin/massachusetts_roads_dataset_500` (parquet); ingested via
  `scripts/prepare_massroads.py`.
- **Annotation style.** Binary road masks; rural roads annotated as **thin lines**.
- **Resolution.** 500² native, trained at 512².
- **Statistics.** Road pixel share **3.6 %** (~3–6 px wide) — genuinely thin. 160
  train / 40 test (subset, for the 4 GB budget).
- **Why selected.** When SkyScapes (aerial *markings*) proved unreachable, this is the
  closest freely available real aerial dataset whose structures are *thin* — the
  property the law concerns. It substitutes for SkyScapes on **thinness**, not on
  marking semantics.
- **Limitations.** Roads, not markings; nearly-uniform thinness (all images < 6 px),
  so the *within-dataset* width gradient is flat — the evidence is the aggregate gap.
- **Role.** The decisive **real-aerial confirmation**: converged U-Net, 3 seeds,
  mIoU 0.49 vs clDice 0.76, gap **+0.27** (CI-tight). Lands on the geometric curve
  (Fig. A).

## 5.5 UAVid — genuine low-altitude UAV (real, the negative)

- **Origin.** Low-altitude oblique UAV video frames, HF
  `arakesh/uavid-15-hq-mixedres` (parquet); ingested via `scripts/prepare_uavid.py`.
  Road colour `(128,64,128)`.
- **Annotation style.** 8-class semantic (building, **road**, tree, vehicles, …);
  binarised to road.
- **Resolution.** 3840×2160 native, ingested at 768², trained at 512².
- **Statistics.** Road pixel share **11 %**; roads are **wide** (12–35 px) — road
  *surfaces*, not lines.
- **Why selected.** To test the law on *genuine UAV* imagery (the campaign's target
  viewpoint).
- **Limitations / the honest negative.** Roads are too wide to be "thin." The law
  predicts no gap there — and indeed mIoU ≈ clDice (gap ≈ 0). UAVid thus *bounds* the
  law (wide structures are in the safe zone) rather than confirming it. Documented in
  full (`reports/uav_claim_validation.md`).
- **Role.** Converged real-UAV model (mIoU 0.57, 3 seeds) **and** the wide-structure
  negative that fixes the right edge of Figure A.

## 5.6 Dataset comparison table

```
  Dataset      Real?  View       Structure   Width    Road/mark%  Role
  -----------------------------------------------------------------------------
  Synthetic    no     n/a        markings    2–8 px   controlled  derive the law
  RLMD         yes    ground     markings    2–8 px   <2%         imbalance + binary
  LoveDA       yes    aerial     roads(thin) <6 px    ~13%        aerial validation
  MassRoads    yes    aerial     roads(thin) 3–6 px   3.6%        aerial CONFIRM (+0.27)
  UAVid        yes    UAV        roads(wide) 12–35 px 11%         UAV negative (~0)
```

## 5.7 The honest data gap (stated plainly)

The *ideal* dataset — aerial, low-altitude, with thin **lane markings** — is
**SkyScapes** (DLR). It is licence-gated and its download portal was network-
unreachable from the working environment (HTTP 000). Every channel was tried (HF,
Kaggle, GitHub, DLR portal) and the failure is documented
(`reports/skyscapes_acquisition_attempt.md`). Rather than fabricate it, the project
validates the *structural* claim on real thin roads (LoveDA, MassRoads) and the
*marking* claim on synthetic + real ground markings (RLMD), and is explicit that the
aerial-marking confirmation remains future work. This triangulation is weaker than
SkyScapes would be, but it is *real* and *honest*.

---
