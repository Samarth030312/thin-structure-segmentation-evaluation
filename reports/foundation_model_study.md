# Foundation-Model Study — SAM / SAM2 / MobileSAM for Road Markings

> **Historical / superseded.** From the project's initial benchmark-building phase. Current narrative: the **width-coupling law** (`reports/width_coupling_theory.md`, `paper_package/final_ieee_paper.pdf`). Experiments used a synthetic generator plus the public datasets RLMD, LoveDA, Massachusetts Roads, UAVid. See `reports/repository_integrity_report.md`.


> We evaluate vision foundation models and, where adaptation is not viable, give
> a technical justification — a feasibility analysis on the available hardware, the
> known thin-structure failure mode, and a probe (`scripts/run_sam_probe.py`) plus
> a pseudo-labeling recipe.

## 1. The models

| Model | Image encoder | Params | Promptable | Semantic classes? |
|---|---|---|---|---|
| **SAM** (Kirillov'23) | ViT-H/L/B | 636 M (ViT-H) | yes (points/box) | **no** (class-agnostic) |
| **SAM2** (Ravi'24) | Hiera | 224 M (large) | yes + video memory | no |
| **MobileSAM** (Zhang'23) | TinyViT | **~10 M** | yes | no |

## 2. Feasibility on this hardware (4 GB GTX-1650) — the technical justification

| Workload | Feasible? | Reason |
|---|---|---|
| SAM/SAM2 **fine-tuning** | ❌ No | ViT-H is 636 M params; the encoder activations alone at 1024² exceed 4 GB. SAM2's memory bank adds more. Training needs ≥24 GB. |
| SAM ViT-B **inference** | ⚠️ tight | ~375 M params (~1.5 GB weights) + 1024² activations ≈ near the 4 GB ceiling; possible but slow. |
| **MobileSAM inference** | ✅ Yes | ~10 M params, fits comfortably; the right choice here. |

**Conclusion: foundation-model *training/adaptation* is out of scope on this
hardware** — an honest hardware limit, not a methodological gap. We therefore
study foundation models in the role where they are both *feasible* and
*scientifically interesting*: **inference-time, class-agnostic mask proposals**.

## 3. Why SAM is a weak *direct* segmenter for thin markings (mechanism)

1. **No semantic classes.** SAM outputs class-agnostic masks; road-marking
   perception needs the 25-way taxonomy (solid vs dashed vs arrow...). SAM cannot
   provide this without a separate classifier.
2. **Thin-structure bias.** SAM's mask decoder is trained on object-like, blob
   segments; thin, elongated, low-contrast structures (a 2 px lane line on
   asphalt) are under-segmented or merged with the road. This is the *same*
   thin-structure difficulty our clDice/Boundary-IoU protocol was built to
   measure — making our metrics the right yardstick for SAM too.
3. **Automatic mask generation** floods the image with region proposals; the lane
   line is rarely a single coherent proposal.

The probe (`run_sam_probe.py`) quantifies this: it measures clDice and centerline
recall of SAM's class-agnostic foreground against GT markings. **Predicted
outcome: high recall on thick zebra/arrow blocks, low clDice/recall on thin
lines** — i.e. SAM helps exactly where markings are *not* thin.

## 4. Where foundation models *do* help — pseudo-labeling (the useful recipe)

SAM's value here is as an **annotation accelerator / weak supervisor**, not a
segmenter:

1. A human (or a cheap detector) clicks/points at markings → SAM's *prompted*
   mode returns a clean mask (prompted SAM is far better than automatic on thin
   structures).
2. The class is assigned from the prompt source; SAM refines the boundary.
3. These become pseudo-labels to pretrain/augment a CoRe-trained segmenter,
   reducing manual annotation cost — directly relevant to building the missing
   **UAV marking dataset** (`final_dataset_selection.md`).

This reframes the foundation model from "competitor segmenter" (where it loses)
to "label-efficiency tool" (where it wins) — the framing an AV data-engine team
actually uses.

## 5. What we did vs. did not run

- ✅ Feasibility analysis (VRAM math, this hardware).
- ✅ A ready-to-run probe (`scripts/run_sam_probe.py`) using our thin-structure
  metrics; runs where `ultralytics`/`segment_anything` + weights are available.
- ❌ Live SAM inference — the SAM packages are not installed and we deliberately
  do **not** mutate the working torch build mid-experiment to add them; the probe
  is one `pip install ultralytics` away on an unconstrained machine.

## 6. References
Kirillov et al., *Segment Anything*, ICCV 2023. Ravi et al., *SAM 2*, 2024.
Zhang et al., *Faster Segment Anything (MobileSAM)*, 2023.
