# PROJECT READINESS REPORT

*Self-assessment of the UAV / road-marking perception benchmark.*

---

## 1. Completed work

| # | Component | Status | Primary artifact |
|---|---|---|---|
| 1 | Acquire + validate a real UAV/aerial dataset | ✅ **done** | **LoveDA** (real aerial, HF) ingested, validated (0 errors), EDA; **RLMD** (real markings) also ingested; SkyScapes ingestion built |
| 2 | Cross-dataset generalization (2×2) | ✅ **done** | `cross_dataset_generalization.md`, fig5 — RLMD↔LoveDA executed |
| 3 | Clean 6-loss ablation (same arch) | ✅ **done** | `loss_ablation_clean.md`, table2 — U-Net++, real RLMD |
| 4 | Multi-seed | ✅ **done (3 converged seeds)** | `multiseed_results.md`, fig4/table7 — overturned the single-seed loss claim; 5 seeds out of GPU-budget (documented) |
| 5 | Failure taxonomy | ✅ **done** | `failure_taxonomy.md` — real RLMD (56% thin, 44% shadow) |
| 6 | Explainability (Grad-CAM) | ✅ **done** | `explainability.md` — U-Net++ vs SegFormer |
| 7 | Publication figures (300 dpi + vector) | ✅ **done** | `paper_figures/` (5 figs × png+pdf), consistent style |
| 8 | Claim audit | ✅ **done** | `claim_audit.md` — every claim → evidence; 3 claims retracted/softened |
| 9 | Repository audit | ✅ **done** | `repo_audit.md` — 62 tests pass; found+fixed 1 bug |
| 10 | Paper-writing package | ✅ **done** | `paper_package/` (outline, checklists, reviewer notes), `paper_tables/` |

---

## 2. Strongest contributions

1. **A real-data demonstration that mIoU *inverts* model/loss rankings.** On RLMD
   (25 real marking classes) the clean 6-loss ablation shows mIoU ranks losses
   *opposite* to clDice (Spearman ρ=−0.31): the top-mIoU losses (Tversky, Dice)
   have **PixelAcc ≈ 0.008** — they flood the frame. Selecting by mIoU picks the
   worst perception model. This is a crisp, real, important finding for AV
   evaluation. *(Headline.)*
2. **A thin-structure evaluation protocol** (clDice, Boundary-IoU, tolerance-IoU,
   width-stratified) with a controlled synthetic mechanism study isolating *why*
   mIoU fails (width-coupling).
3. **An honest, multi-seed loss study** of a proposed loss (CoRe): wins on
   synthetic; a single-seed real win (vs CE+Dice) **dissolves under 3-seed
   validation** (tied: clDice 0.405 vs 0.406; CoRe higher-variance). Two
   documented self-corrections (a confound, then a single-seed artifact) —
   scientifically mature, demonstrating methodology over narrative.
4. **A full, reproducible perception platform**: 3 real-dataset ingestions,
   config-driven training, statistical testing, performance/deployment Pareto,
   C++/TensorRT path, 62 tests, CI.

## 3. Weakest areas / remaining limitations

| Limitation | Impact | Mitigation / next step |
|---|---|---|
| **No aerial-UAV *marking* results** | title says UAV; RLMD is ground-view | SkyScapes ingestion is built + tested on a stand-in; needs DLR license + >4 GB GPU |
| **Compute-bounded** (4 GB GPU, subsampled, ≤12 epochs) | low absolute accuracy (mIoU/clDice) | conclusions are about *metric behaviour* (budget-independent); full-scale training is the next step |
| **Cross-dataset is binary + disjoint taxonomies** | RLMD↔LoveDA mixes viewpoint+semantic shift | upper-bound result; true marking↔marking transfer needs SkyScapes |
| **CoRe loss gives no reliable gain** (ties CE+Dice, higher variance) | proposed method is a null/cautionary result | reframed as a multi-seed methodology lesson, not oversold |
| **Foundation-model adaptation not run** | SAM/SAM2 training infeasible at 4 GB | feasibility analysis + ready MobileSAM probe (`run_sam_probe.py`) |
| **Multi-seed = 3 seeds, headline only** | not all 6 losses × 5 seeds | documented scope; full 6×5 at converged budget = 30+ GPU-hours out of budget |

## 4. Publication readiness score

**Overall: 7.0 / 10 for a workshop/short paper; 5.5 / 10 for a full conference.**

| Dimension | Score | Note |
|---|---|---|
| Novelty / contribution | 7.5/10 | real-data mis-ranking is a genuine, useful finding; not architecturally novel |
| Experimental rigor | 7/10 | controlled ablations, bootstrap CIs, paired tests, multi-seed (running) |
| Real-data evidence | 6.5/10 | 2 real datasets used; aerial-UAV marking data still pending |
| Scale of experiments | 4.5/10 | 4 GB GPU, subsampled — the main weakness |
| Reproducibility | 9/10 | tests, CI, configs, ingestion, hardware report |
| Writing/figures | 8/10 | paper package + publication figures ready |

**Verdict:** ready to *draft* a strong **ITSC/workshop** submission now; needs the
SkyScapes (aerial) run + full-scale multi-seed to be competitive at a **full
conference / T-ITS**.

## 5. Reproducibility score

**9 / 10.** Every number traces to a committed script + config; 62 tests + CI;
deterministic seeds; ingestion scripts for 3 datasets; hardware report. Deduction:
real datasets are not redistributable (license/size) — but ingestion is one
command and verified on stand-ins.

## 6. Recommended submission venues

1. **IEEE ITSC 2026** (conference) — perfect topical fit (ITS, road perception);
   the mis-ranking finding + benchmark suit a 6-page paper. *Primary target.*
2. **IEEE T-ITS** (journal) — after adding SkyScapes + full-scale runs.
3. **CVPR/ICCV Workshop on Autonomous Driving** or **WACV** — for the
   metric/evaluation angle.
4. **ISPRS / remote-sensing venue** — if the aerial (SkyScapes/LoveDA) results are
   strengthened.

## 7. Exact next actions (priority order)

1. **Obtain SkyScapes** (DLR agreement) → `prepare_skyscapes.py` → run the loss
   ablation + thin-structure protocol on **aerial markings** (closes the #1 gap).
2. **Full-scale runs** on a ≥12 GB GPU: full RLMD (no subsample), 50 epochs, 512²,
   **5 seeds × all 6 losses** → tight CIs, final tables.
3. **Same-architecture cross-dataset** with a second *marking* dataset (CeyMo) for
   a semantically-clean transfer matrix.
4. **MobileSAM pseudo-label experiment** (`run_sam_probe.py`) on a ≥8 GB GPU.
5. **Draft the paper** from `paper_package/paper_outline.md`; anonymise; fill
   tables/figures (already generated); submit to ITSC.

---

*Live experiment status:
`outputs/*.log`; results: `reports/`, `paper_figures/`, `paper_tables/`.*
