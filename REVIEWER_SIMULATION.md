# Reviewer Simulation

Simulated peer review for a generic IEEE-ITSC-class submission built from this
repository. Three independent reviewers. Scores: 1 (strong reject) – 6 (strong
accept); confidence 1–5.

---

## Reviewer A — supportive but rigorous

**Summary.** The paper studies how mean IoU evaluates thin road markings and
argues it can mis-rank models; it proposes a thin-structure protocol (clDice,
Boundary-IoU, tolerance-IoU) and a connectivity loss, and reports controlled
synthetic and real (RLMD) experiments with bootstrap CIs and multi-seed analysis.

**Strengths.** (1) Unusually honest — documents two self-corrections including a
multi-seed reversal of its own claim. (2) Strong, reproducible engineering and
released ingestion for real datasets. (3) The controlled width study cleanly
isolates the mechanism (mIoU couples detection with width matching).

**Weaknesses.** (1) Real-data models are weak (clDice ≤0.37, recall ≤0.36) — the
real-data conclusions would be more convincing with converged models. (2) Novelty
is incremental: the metrics are prior work and the failure mode is known. (3) The
proposed CoRe loss yields no reliable gain.

**Questions.** Does the mIoU mis-ranking persist when models are trained to
convergence? How sensitive is the inversion to micro- vs macro- vs foreground-
mIoU? Can you report a published RLMD baseline for calibration?

**Recommendation:** 4 (weak accept) at a *workshop*; 3 (borderline) at the main
conference. **Confidence: 4.**

---

## Reviewer B — neutral

**Summary.** An evaluation/benchmark paper claiming mIoU is inadequate for thin
road markings, with a protocol of topology-aware metrics and a software framework.

**Strengths.** Reproducible; honest scoping; sensible metric choices; a clear
synthetic ablation.

**Weaknesses.** (1) Title/scope says UAV, but experiments use ground-view RLMD and
aerial land-cover (LoveDA) — no UAV marking data. (2) Statistical claims rest on
small n (3 seeds; 6-loss Spearman ρ=−0.31 is not significant). (3) The cross-
dataset transfer is confounded (binary, disjoint taxonomies, viewpoint shift) and
adds little. (4) Contribution is mostly a re-application of existing metrics.

**Questions.** Why is the paper framed as UAV? What is the absolute SOTA on RLMD,
and how far are these models from it? Is the "inversion" an artifact of 25-class
foreground averaging?

**Recommendation:** 3 (borderline reject) at conference; 4 at workshop.
**Confidence: 4.**

---

## Reviewer C — extremely skeptical

**Summary.** The paper re-packages the well-known fact that overlap/accuracy
metrics reward over-prediction under class imbalance, applies off-the-shelf
metrics (clDice, Boundary-IoU), and proposes a loss that does not work.

**Strengths.** The code is clean and the authors are candid about limitations.
That candor is the paper's best feature.

**Weaknesses.** (1) **No genuine novelty.** clDice/Boundary-IoU are cited prior
art; "mIoU rewards flooding under imbalance" is textbook. (2) **Under-powered to
the point of unreliability.** The best real model detects ~36 % of marking
centerlines (clDice 0.37); drawing metric conclusions from models that barely
function is unsound. The headline "Tversky tops mIoU" is comparing two broken
models. (3) **Scope misrepresentation:** "UAV road-marking" with zero UAV marking
results. (4) **Null method:** CoRe ties the baseline. (5) **Statistics are thin:**
ρ=−0.31 (p=0.54); n=3 seeds; one of the two real datasets has 41 test images.
(6) The "novel" width-stratified metric is an analysis convenience, not a method.

**Questions.** What does this tell a practitioner that "report precision/recall and
don't trust accuracy on imbalanced data" did not already? Where is a single result
on a model that actually works?

**Recommendation:** 2 (reject). **Confidence: 5.**

---

## Meta-review (area-chair synthesis)

Consensus: **reject at a competitive main conference; borderline-acceptable at a
workshop.** All three reviewers credit the engineering and honesty; all three flag
**low novelty**, **under-powered/non-converged experiments**, and a **UAV scope
mismatch**. The decisive issues are not fixable by rebuttal alone — they require
(a) converged real-data runs, (b) honest reframing to "thin-structure evaluation,"
and (c) either real UAV data or dropping UAV from the claim. The candor that makes
this a pleasant read does not substitute for experimental power or novelty.

**Aggregate: 2.7 / 6 (conference), 4.0 / 6 (workshop). Average confidence 4.3.**
