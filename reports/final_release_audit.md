# Final Repository Release Audit

Adversarial pre-release review (hostile CVPR/ITSC reviewer + skeptical professor +
research-integrity auditor + OSS maintainer). The mandate was to *find damage*, not to
fix it. Findings are evidence-linked (`file:line`). **The science core (the
width-coupling law, honestly scoped) is defensible; the *packaging* is not, and would
destroy credibility on first contact.**

---

## CRITICAL ISSUES (block release; credibility-destroying)

### C1 — Phantom "AU-Drone" dataset presented as real (22 files)
`grep -rli au-drone` matches **22 files** (README, `reports/final_report.md`,
`docs/{training,evaluation}_guide.md`, `docs/architecture.md`,
`configs/dataset/audrone.yaml`, five `*_audrone` experiment configs,
`src/uavroadmark/data/synthetic.py`, multiple reports). **No such dataset exists** —
there is no `datasets/audrone/`, no source URL, no citation. Yet:
- `README.md:15` — *"The **real AU-Drone dataset** is not redistributable…"*
- `README.md:20` — *"Point the config at AU-Drone and the **same commands produce the
  headline results**."*
- `docs/evaluation_guide.md:50` — *"On real AU-Drone with a pretrained DeepLabV3+…"*

This asserts the existence of a real dataset and real headline results that **do not
exist**. To a research-integrity auditor this is **fabrication-adjacent**; to a
professor it is an instant trust-killer. Even if "AU-Drone" was an aspirational target,
the public-facing language ("the real AU-Drone dataset… produces the headline
results") is false as written. **This single issue is sufficient to fail the release.**

### C2 — README misrepresents the entire project
`README.md` (the landing page) is built around the **discredited** framing
(`README.md:3`: *"Indian road-marking semantic segmentation from UAV imagery"*;
`README.md:224`: *"what architecture is best for Indian UAV…"*). It centres a phantom
dataset and a model-zoo benchmark, and **barely mentions the actual contribution** —
the width-coupling law (`Gap = 2δ/(w+2δ)`), clDice, or the real datasets actually used
(UAVid, LoveDA, MassRoads, RLMD). A recruiter/professor forms a wrong, partly-fabricated
impression in the first 30 seconds.

### C3 — `reports/final_report.md` contradicts the paper and monograph
Its title is *"An Evaluation Framework for Indian Road-Marking Detection from UAV
Imagery"* with an *"Indian-road domain"* abstract and AU-Drone references — directly
contradicting `paper_package/final_ieee_paper` (*"When mIoU Lies"*) and the monograph.
**Two top-level documents tell incompatible stories.** A reviewer who opens
`final_report.md` first gets a discredited project.

### C4 — Figure A (the "killer figure") real-data x-positions are hand-picked, not measured
`scripts/make_law_figures.py:26`:
`REAL = [("Synthetic",2.0,0.65),("MassRoads",4.0,0.265),("LoveDA",5.0,0.22),("UAVid",20.0,0.007)]`
— the **widths (2,4,5,20 px) and gaps are hardcoded literals**, *not* loaded from the
validation outputs. The validation JSONs
(`reports/visualizations/uav_validation/*_width_val.json`) store only **categorical
width bins** (`<6`, `6–12`, …) and a thin-tertile gap — **no measured mean width**.
Consequences:
- The central claim "three real datasets land on the geometric curve" rests on
  **eyeballed x-coordinates**. A hostile reviewer's one-line kill: *"you placed the
  points to fit your curve."*
- LoveDA and UAVid span **multiple** width bins, yet are plotted as a **single point** at
  one representative width using a **dataset-aggregate** gap — a methodological mismatch
  (aggregate y at a hand-chosen x).
- This also **directly contradicts** `README.md:19` ("nothing is mocked or
  **hard-coded**").

The law may still be correct, but **the figure used to claim real-world validation is
not rigorously constructed**, and that is exactly what an integrity-minded reviewer
hunts for.

---

## MAJOR ISSUES (must address before submission)

### M1 — The controlled experiment is partly circular
`scripts/run_controlled_robustness.py` manufactures the "prediction" by dilating the GT
by δ pixels, then `fit_width_law.py` recovers `Gap ≈ 2δ/(w+2δ)` with R²=0.98. But
`IoU = w/(w+2δ)` is **algebraically exact** for a uniform δ-dilation — so the "fit" is
**fitting algebra to algebra**. It confirms the geometry is self-consistent; it does
**not** independently show that *real model errors* obey the law. The only non-circular
evidence is the real datasets — whose figure has problem **C4**. The empirical chain has
a weak link at both ends.

### M2 — "Not a git repository"
`git rev-parse` reports **NOT A GIT REPO**. For "GitHub publication" this is a blocker:
no history, no commits, and the 38-line `.gitignore` (which correctly lists
`outputs/`, `*.pth`, `datasets/*/`) is **unverified** until `git init` — meaning the
27 GB of outputs and 102 checkpoints are one careless `git add -A` from being committed.

### M3 — Novelty ceiling (self-admitted)
The law is, at core, IoU's definition made explicit. The project's own
`reports/final_paper_positioning.md` and `FINAL_RESEARCH_VERDICT.md` concede a reviewer
will call it incremental ("a re-expression of IoU's definition"). Honest, but it caps
the work at workshop/ITSC level — do not let any document imply otherwise.

### M4 — Dataset-license obligations not surfaced
Ingestion pulls **LoveDA (CC-BY-NC)**, **UAVid (research-only)**, **Massachusetts Roads**,
and **RLMD** — non-commercial/research licences — while the repo ships an **MIT**
`LICENSE` with no `NOTICE`/`DATA_LICENSES` file or per-dataset attribution. Not
redistributing the data mitigates, but the scripts *fetch* it, and a clean OSS release
needs explicit data-licence attribution and a non-commercial caveat.

### M5 — Stale, unrunnable docs
`docs/training_guide.md`, `docs/evaluation_guide.md`, `docs/architecture.md` give
commands against `audrone` configs/data that **cannot run** (no data). A researcher
following the README's pointers hits dead ends.

---

## MINOR ISSUES

- **m1** — "Claude" appears literally in `reports/github_release_audit.md:7,12,20`
  (describing the search terms). A naive `grep Claude` hits it; launder the wording.
- **m2** — 27 GB `outputs/` + 1.8 GB `datasets/` + **102 `.pth`** + `*.log` files in
  `outputs/` sit in the working tree (gitignored, but heavy and one mistake from
  inclusion).
- **m3** — `configs/dataset/audrone.yaml` + 5 `*_audrone` experiment configs reference
  non-existent data and should be removed or clearly marked hypothetical.
- **m4** — README synthetic stats ("94.6% background") are from the old framing and are
  not the headline result.
- **m5** — `reports/cross_dataset_generalization.md` is the **confounded** RLMD↔LoveDA
  transfer (disjoint taxonomies, binary, tiny test set). It is honestly caveated, but
  remains weak evidence and should stay clearly labelled exploratory.

---

## PROFESSOR REVIEW SIMULATION

**"What is the strongest criticism of this work?"** The packaging undermines the
science: a phantom "real" dataset (AU-Drone) in the README and a killer figure whose
real-data x-axis is hand-placed (C1, C4). An integrity-minded professor stops trusting
the numbers after finding either.

**"What is the strongest criticism of the width-coupling theory specifically?"** It is
algebraically IoU's own definition (`w/(w+2δ)`), and the controlled "validation" is
circular (inject δ, recover δ; M1). The only non-circular test is the real datasets,
whose placement on the curve is not rigorously measured (C4). Verdict: *true but
near-trivial, and under-validated where it counts.*

**"What would make me reject this paper?"** Phantom-dataset language anywhere near the
submission; a figure with a non-measured x-axis presented as empirical validation;
bounded novelty without a width-corrected *method* (the cure, not just the diagnosis).

**"What evidence is still missing?"** (1) Measured per-dataset width *distributions* with
**per-bin** gaps (not single hand-placed points); (2) non-circular evidence that *real
model* boundary errors follow `2δ/(w+2δ)` with an *independently measured* δ; (3) aerial
road *markings* (SkyScapes); (4) a width-corrected metric that turns the critique into a
method.

---

## GITHUB LANDING-PAGE AUDIT

| Question | Verdict | Why |
|---|---|---|
| Recruiter understands in 2 min? | **NO** | README sells a phantom "Indian UAV / AU-Drone" project, not the law |
| Professor understands in 5 min? | **NO** | README + `final_report.md` contradict the paper; phantom dataset |
| Researcher reproduces in 30 min? | **PARTIAL** | the *law* scripts run (`run_controlled_robustness`→`fit_width_law`→`make_law_figures`); but README points at unrunnable AU-Drone commands |

**Proposed fixes (not executed — audit only):** rewrite README around the
width-coupling law and the *real* datasets; delete or mark `final_report.md` superseded;
regenerate Fig A from **measured** per-image widths (emit mean width from
`run_width_validation.py`) or replot each real dataset as a width-binned curve; purge or
hypotheticalise AU-Drone across the 22 files; `git init` + verify `.gitignore`; add a
`DATA_LICENSES`/`NOTICE`; drop the "nothing hard-coded" claim.

---

## ISSUE COUNT
- Critical: **4** (C1 phantom dataset, C2 README, C3 contradictory final_report, C4
  hand-placed figure axis)
- Major: **5** (circular controlled study, no git, novelty ceiling, data-licence
  attribution, stale docs)
- Minor: **5**

## RELEASE RECOMMENDATION

### **NOT READY**

The width-coupling law itself is honest, derived, and reasonably validated — and the
paper/monograph/law-reports are internally consistent and candid. But the **repository
as a public artifact is not releasable**: it advertises a **non-existent dataset as
real** (C1), its **landing page and a top-level report push a discredited framing that
contradicts the paper** (C2, C3), and its **headline figure's real-data axis is
hand-placed** (C4). Any one of these, found by a hostile reviewer or skeptical
professor, would discredit the entire repository regardless of the law's correctness.

These are **packaging and integrity** defects, not scientific ones — fixable without new
experiments — but until they are fixed the honest verdict is **NOT READY** for
professor review, GitHub publication, or paper submission. After C1–C4 and M1–M5 are
resolved, the realistic ceiling (per `FINAL_RESEARCH_VERDICT.md`) is **READY WITH FIXES
→ workshop/ITSC**, not top-tier.
