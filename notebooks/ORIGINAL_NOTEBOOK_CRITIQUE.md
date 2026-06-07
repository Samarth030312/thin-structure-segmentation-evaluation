# Critique of the Original Notebook (`ComputerVisionFinalProject.ipynb`)

> **Historical / superseded.** This document is from the project's initial benchmark-building phase. The project's actual contribution and current narrative is the **width-coupling law** for thin-structure evaluation metrics — see `reports/width_coupling_theory.md` and `paper_package/final_ieee_paper.pdf`. The "target UAV dataset" referenced below was an aspirational road-marking set that was **never acquired**; the experiments actually used a synthetic generator and the public datasets RLMD, LoveDA, Massachusetts Roads, and UAVid. See `reports/repository_integrity_report.md`.


The original notebook is preserved for provenance. This is the engineering
review that motivated the rebuild. Each issue links to how the framework fixes
it.

| # | Location | Issue | Severity | Fix in framework |
|---|---|---|---|---|
| 1 | `train_one_epoch` | `preds = torch.sigmoid(preds)...; loss = BCELoss(preds, ...)` — applying sigmoid **then** `BCELoss` is numerically unstable (should be `BCEWithLogitsLoss` on logits; double-activation kills gradients). | **Critical** | All losses consume **raw logits**; CE/Dice/Focal/Tversky/Combo in `losses/functional.py`. |
| 2 | `SegmentationDataset` | Pairs `sorted(glob(images))` with `sorted(glob(masks))` positionally — one missing/extra file silently shifts every pair. | **Critical** | Stem-matched pairing that **fails loudly** on any unpaired file (`data/dataset.py`). |
| 3 | `train_one_epoch` | `imgs, masks = imgs.cuda(), masks.cuda()` hardcoded — crashes on CPU-only machines. | High | `device: auto` resolved everywhere; CPU path tested. |
| 4 | `train_one_epoch` | `global preds, masks` — leaks hidden state, error-prone. | Medium | Pure functions; typed batch dicts. |
| 5 | model | Binary (`classes=1`) — cannot distinguish lane vs zebra vs arrow. | High | 7-class taxonomy. |
| 6 | training loop | No checkpointing, AMP, scheduler, early stopping, or config — not reproducible, wastes compute. | High | Full config-driven engine (`engine/trainer.py`). |
| 7 | whole notebook | Hardcoded Google-Drive paths; Colab-only. | Medium | Portable folder contract + YAML configs. |
| 8 | evaluation | Ad-hoc Dice only; no IoU/precision/recall, no per-class, per-image averaging. | High | Confusion-matrix suite, foreground-aware (`metrics/segmentation.py`). |
| 9 | data | No validation, no EDA — silent data bugs surface as bad metrics days later. | High | Validator (8 checks) + automated EDA. |
| 10 | project | No tests, no docs, no leaderboard. | Medium | 32 tests, docs/, auto-leaderboard. |

**Net:** the notebook is a reasonable first exploration but not reproducible,
not robust, and not analysable. The rebuild keeps the sensible core (DeepLabV3+
on the target UAV dataset, smp, albumentations) and turns it into a maintainable benchmark.
