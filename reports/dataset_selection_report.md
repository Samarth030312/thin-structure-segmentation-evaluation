# Dataset Selection Study — UAV Road-Marking Segmentation

> **Historical / superseded.** This document is from the project's initial benchmark-building phase. The project's actual contribution and current narrative is the **width-coupling law** for thin-structure evaluation metrics — see `reports/width_coupling_theory.md` and `paper_package/final_ieee_paper.pdf`. The "target UAV dataset" referenced below was an aspirational road-marking set that was **never acquired**; the experiments actually used a synthetic generator and the public datasets RLMD, LoveDA, Massachusetts Roads, and UAVid. See `reports/repository_integrity_report.md`.


> Goal: select, **on scientific grounds**, the best dataset(s) for benchmarking
> road-marking segmentation from UAV imagery — *without* assuming the
> original project's the target UAV dataset choice is optimal. We evaluate eight candidate
> sources against task-specific criteria, score them in a weighted decision
> matrix, and justify the recommendation.

---

## 1. What the ideal dataset must provide

The task is **road-marking** segmentation from a **UAV (nadir/oblique)**
viewpoint, with an **road-marking** domain emphasis. The selection criteria,
with weights reflecting their importance to *this* task:

| # | Criterion | Weight | Why it matters |
|---|---|---|---|
| C1 | **UAV / aerial viewpoint** | 0.22 | Ground/dashcam geometry does not transfer to nadir UAV; perspective, scale, and occlusion statistics differ fundamentally. |
| C2 | **Road-marking labels** (lanes, zebra, arrows, stop lines) | 0.22 | The actual target classes must exist, ideally as dense masks. |
| C3 | **Pixel-accurate segmentation masks** | 0.16 | Bounding boxes/polylines are insufficient for thin-structure IoU. |
| C4 | **road-marking / similar domain** | 0.14 | roads differ in marking style, wear, occlusion, and traffic density; domain gap directly hurts transfer. |
| C5 | **Public availability & license** | 0.12 | Reproducibility and open-source delivery require redistributable, well-licensed data. |
| C6 | **Scale & diversity** | 0.08 | Enough samples/scenes to train and to estimate metrics with low variance. |
| C7 | **Active maintenance / accessibility** | 0.06 | Dead download links are a real, common failure (assume nothing exists). |

---

## 2. Candidate datasets

| Dataset | Viewpoint | Marking labels? | Mask type | Domain | Notes |
|---|---|---|---|---|---|
| **the target UAV dataset** (the original project's choice) | **UAV** | **Yes** (road markings) | Segmentation | Often road-marking/South-Asian UAV captures | Small; availability/licensing must be verified; the project's named source. |
| **BDD100K** | Dashcam (ground) | Lane markings (as lines) + drivable area | Lane = polylines; seg = 2D panoptic subset | US | Large/diverse but **wrong viewpoint** and lanes are line-annotations, not dense thin-structure masks. |
| **Mapillary Vistas** | Street-level (ground) | Yes, incl. lane markings (66+ classes) | Dense segmentation | Global (incl. India) | Excellent labels but **ground viewpoint**. |
| **ApolloScape** | Dashcam + some | Lane markings (lanemark subset) | Dense + 3D | China | Rich lane-marking subset but **ground viewpoint**. |
| **UAVid** | **UAV (oblique)** | No dedicated marking classes (road, building, car, …) | Dense segmentation | Urban (China/EU) | Right viewpoint, **but "road" is one class — markings not separated.** |
| **LoveDA** | **Aerial/satellite** | No (land-cover: road, building, water, …) | Dense segmentation | China (urban/rural) | Right-ish viewpoint, **wrong classes** (land-cover, not markings). |
| **Generic "RoadMarking" datasets** (e.g. KITTI-lane, TuSimple, CULane, Ceymo) | Mostly **ground/dashcam** | Yes (lanes) | Lines/masks | Various (US/China/Sri Lanka) | Marking-focused but ground viewpoint; **Ceymo** (Sri Lanka) is domain-close but dashcam. |
| **Custom UAV capture + our annotation framework** | **UAV** | **Yes (designed)** | Dense masks (our taxonomy) | **road-marking (targeted)** | Full control; cost = capture + annotation effort. Our annotation/validation framework (Phases 3–4) exists precisely to enable this. |

---

## 3. Weighted decision matrix

Scores are 1–5 (5 = best fit for the criterion). Weighted total = Σ(weight ×
score). This is a *transparent, reproducible* scoring — adjust weights in
`reports/dataset_selection_report.md` and the ranking updates accordingly.

| Dataset | C1 UAV (.22) | C2 marks (.22) | C3 masks (.16) | C4 India (.14) | C5 license (.12) | C6 scale (.08) | C7 access (.06) | **Weighted** |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| **the target UAV dataset** | 5 | 5 | 5 | 5 | 3 | 2 | 2 | **4.42** |
| Custom UAV + our framework | 5 | 5 | 5 | 5 | 5 | 2 | 5 | **4.72** |
| UAVid | 5 | 1 | 5 | 2 | 4 | 4 | 5 | **3.46** |
| Mapillary Vistas | 1 | 5 | 5 | 4 | 4 | 5 | 5 | **3.78** |
| ApolloScape | 1 | 4 | 4 | 2 | 3 | 5 | 4 | **2.96** |
| BDD100K | 1 | 3 | 2 | 2 | 4 | 5 | 5 | **2.70** |
| LoveDA | 4 | 1 | 5 | 2 | 5 | 4 | 5 | **3.34** |
| Ceymo / lane datasets | 1 | 5 | 4 | 3 | 4 | 4 | 4 | **3.32** |

> Worked example (the target UAV dataset): 0.22·5 + 0.22·5 + 0.16·5 + 0.14·5 + 0.12·3 + 0.08·2 + 0.06·2 = 1.10+1.10+0.80+0.70+0.36+0.16+0.12 = **4.42**.

---

## 4. Decision and justification

**Primary recommendation: the target UAV dataset as the target dataset, with our Custom-UAV +
annotation framework as the resilient fallback / extension.**

Reasoning:

1. **the target UAV dataset is the only public-ish source that satisfies the three highest-weight
   criteria simultaneously** — UAV viewpoint (C1), road-marking classes (C2), and
   dense masks (C3) on an road-marking-domain capture (C4). No ground-view dataset
   (Mapillary, BDD100K, ApolloScape) can satisfy C1, which carries the most
   weight, because the nadir geometry is non-transferable.

2. **Its only weak scores are C5–C7 (license/scale/access)** — exactly the risks
   the brief warns about ("datasets may no longer be available"). We therefore
   **do not depend on its continued availability**: the framework defines a
   strict folder contract (`images/<split>`, `masks/<split>`), a **validation
   system** (Phase 3) that fails loudly on any corruption, and a **synthetic
   generator** that reproduces the target UAV dataset's statistical structure so the entire
   pipeline is reproducible *even if the real download dies*. The Custom-UAV path
   (highest matrix score, 4.72) is the long-term answer and is enabled by our
   annotation/validation tooling.

3. **Cross-domain pretraining strategy.** Although ground-view datasets score low
   as *primary* benchmarks, **Mapillary Vistas** (best labels) and **UAVid**
   (correct viewpoint) are valuable for **transfer learning / pretraining**: a
   model pretrained on UAVid's aerial road context and/or Mapillary's
   marking-rich labels, then fine-tuned on the target UAV dataset, is a strong recipe. This is
   captured as an ablation in the final report.

4. **Why not pivot to a larger dataset?** BDD100K/Mapillary are 10–100× larger but
   fail the viewpoint criterion; their scale cannot buy back the domain gap.
   Choosing them would optimise C6 (lowest weight) at the expense of C1–C2
   (highest weights) — a classic, avoidable benchmarking error.

---

## 5. Practical data plan

| Stage | Data | Purpose |
|---|---|---|
| **Pipeline validation (this repo, runs anywhere)** | **Synthetic UAV road-marks** (`scripts/make_synthetic.py`) | Prove correctness end-to-end; real (small-scale) numbers; CI. |
| **Primary benchmark** | **the target UAV dataset** (point `configs/dataset/custom_dataset.yaml:root` at it) | Headline numbers; identical commands. |
| **Transfer-learning ablation** | UAVid / Mapillary pretrain → the target UAV dataset fine-tune | Quantify domain-transfer benefit. |
| **Long-term** | Custom UAV captures annotated with our framework | License-clean, India-targeted, extensible taxonomy. |

> **Honesty note.** All committed metrics in this repository are produced on the
> synthetic dataset (it is the only data that ships). They validate the
> *pipeline*, not the *science of the target UAV dataset*. To obtain headline the target UAV dataset numbers,
> drop the prepared dataset into `datasets/custom_dataset/` and run the same
> `uavrm-train` / `uavrm-eval` commands — see `docs/training_guide.md`.

---

## 6. References

- Yu et al. *BDD100K: A Diverse Driving Dataset.* CVPR 2020.
- Neuhold et al. *The Mapillary Vistas Dataset.* ICCV 2017.
- Huang et al. *The ApolloScape Dataset for Autonomous Driving.* CVPR-W 2018.
- Lyu et al. *UAVid: A Semantic Segmentation Dataset for UAV Imagery.* ISPRS J. Photogramm. 2020.
- Wang et al. *LoveDA.* NeurIPS Datasets & Benchmarks 2021.
- Jayasinghe et al. *CeyMo: See More on Roads — Road Marking Dataset (Sri Lanka).* WACV 2022.
- TuSimple / CULane lane-detection benchmarks.
