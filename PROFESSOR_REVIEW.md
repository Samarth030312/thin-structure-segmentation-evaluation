# Advisor Review

*An internal, critical review of this repository as a candidate research
contribution. Written to identify weaknesses, not to defend the work.*

## Scores (0–10)

| Dimension | Score | One-line justification |
|---|---|---|
| Research quality | 5.5 | Honest, well-scoped evaluation study, but the central finding is incremental and the real-data models are under-trained. |
| Engineering quality | 8.5 | Clean package, 62 tests, CI, config system, 3 real-dataset ingestions, deployment path. Genuinely strong. |
| Novelty | 4.0 | Metrics (clDice, Boundary-IoU) are prior work; the "mIoU mis-ranks" phenomenon is known. The specific demonstration is a modest contribution. |
| Experimental rigor | 5.5 | Good practices (bootstrap CIs, paired tests, multi-seed, self-corrections) applied to **under-powered** experiments (4 GB GPU, subsampled, non-converged models). |
| Reproducibility | 9.0 | Seeds, configs, ingestion scripts, tests, CI, hardware report. Among the strongest aspects. |
| Writing quality | 7.0 | Clear, honest, evidence-linked; some reports are verbose; framing overclaims "UAV". |
| Publication potential | 4.5 | Workshop-plausible after fixes; not competitive at a main venue as-is. |

**Composite: ~6.0 / 10 as a portfolio/engineering artifact; ~4.5 / 10 as a
publishable research contribution.**

## Major strengths

1. **Engineering and reproducibility are excellent.** Installable package, 62
   passing tests, CI, deterministic configs, real-dataset ingestion (RLMD,
   LoveDA, SkyScapes), performance/deployment benchmarking, C++/ONNX path. This is
   the work of a capable engineer and would impress in a portfolio/interview.
2. **Scientific honesty is exemplary.** The repo documents *two* self-corrections
   — a confounded comparison and a single-seed artifact overturned by multi-seed.
   This is rare and admirable; it is the strongest *scientific* signal here.
3. **The metric phenomenon is real and cleanly shown in the synthetic study.**
   The width-stratified experiment (mIoU 0.35 vs clDice 1.0 at 2 px) is a tidy,
   controlled demonstration.

## Major weaknesses

1. **The real-data models are under-trained, undermining the real-data claims.**
   On RLMD the best model (CE+Dice) reaches clDice 0.37 and centerline recall
   0.36 — it *misses ~64 % of markings*. mIoU is 0.03. Conclusions drawn from
   models this weak are fragile; a skeptic will ask whether the mIoU mis-ranking
   persists for well-trained models. (Counter: flooding is flooding, and the
   synthetic study has converged models — but the real leg is weak.)
2. **Scope/title mismatch.** The work is framed around *UAV* road markings, yet
   there are **no real UAV-marking results**: RLMD is ground-view dashcam; LoveDA
   is aerial *land-cover*, not markings. The honest paper is about *thin-structure
   segmentation evaluation*, demonstrated on (ground-view) road markings. The UAV
   framing is currently unsupported and would be flagged immediately.
3. **Modest novelty.** clDice and Boundary-IoU are existing; that mIoU/PixelAcc
   reward majority/over-prediction under imbalance is known. The contribution is a
   careful *demonstration and protocol*, not a new method or metric. CoRe, the one
   proposed method, is a **null result** (ties CE+Dice, higher variance).
4. **Small-n statistics.** 3 seeds; Spearman over 6 losses (ρ=−0.31, p=0.54, not
   significant); LoveDA test = 41 images. The headline "ranking inversion" rests
   on a non-significant rank correlation plus a directly-measured flooding
   mechanism (the latter is the stronger evidence).
5. **Cross-dataset experiment is confounded** (binary foreground; disjoint
   taxonomies; ground↔aerial). It measures combined viewpoint+semantic shift and
   is near-uninterpretable as a clean transfer result (the repo says so).

## Missing experiments / validations

- **Converged training** on real data (full RLMD, more epochs, ≥12 GB GPU) to show
  the mis-ranking holds for *usable* models — the single most important missing run.
- **Real UAV-viewpoint marking results** (SkyScapes) — required to justify the title.
- **A larger loss set × more seeds** for a statistically significant ranking
  correlation (current n=6 losses is too few for Spearman significance).
- **Human/established baseline** comparison (e.g., a published RLMD number) to
  contextualise the absolute scores.
- **Ablation of the metric claim against well-known confounds** (does foreground
  mIoU vs micro-mIoU vs per-class mIoU change the mis-ranking? partially shown,
  not exhaustive).

## Paper risks

- **Reviewer rejects on novelty** ("known phenomenon, existing metrics").
- **Reviewer rejects on scope** ("UAV in title, no UAV results").
- **Reviewer distrusts conclusions from non-converged models.**
- **The proposed method (CoRe) doesn't work**, which weakens a method-paper framing
  (mitigated by reframing as an evaluation paper).

## Top-5 highest-impact improvements (impact × feasibility)

| # | Improvement | Impact | Effort | P(success) | Note |
|---|---|---|---|---|---|
| 1 | Converged full-RLMD runs (≥12 GB GPU, 50 ep) | **High** | ~1–2 GPU-days | 0.9 | makes real-data claims credible; numbers exist via same configs |
| 2 | Reframe as **thin-structure evaluation** paper; drop UAV-method overclaims | **High** | ~1 day writing | 0.95 | fixes the fatal scope mismatch at zero compute |
| 3 | Real UAV markings (SkyScapes) loss ablation | High | license + ~1 GPU-day | 0.5 | justifies a UAV framing if kept |
| 4 | Expand loss/architecture set ×5 seeds for significant rank-inversion stats | Moderate-High | ~2 GPU-days | 0.8 | turns ρ=−0.31 (n.s.) into a defensible claim |
| 5 | Drop or de-emphasise cross-dataset; or add a 2nd *marking* dataset (CeyMo) | Moderate | ~1 GPU-day | 0.7 | removes a weak, confounded result |

**Advisor's bottom line:** strong engineering and exemplary honesty wrapped around
an *under-powered, modestly-novel* evaluation study with a *scope-mismatched* title
and a *non-working* proposed method. With converged experiments and an honest
reframing to "topology-aware evaluation of thin-structure segmentation," this is a
credible workshop paper. As-is, it is a strong portfolio project, not a publication.
