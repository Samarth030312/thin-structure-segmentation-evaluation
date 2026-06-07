# Reviewer Panel Report (Phase 7)

Four simulated reviews of *"When mIoU Lies"* (CVPR/ITSC perspective), plus the
strongest honest positioning. Evidence-cited.

---

## REJECT (hostile CVPR reviewer)
**Summary:** An evaluation note that re-derives the definition of IoU and calls it a
law. **Contribution (−):** `Gap=2δ/(w+2δ)` is algebraically `IoU=w/(w+2δ)` rearranged
(`first_principles_width_analysis.md`); the metrics (clDice, Boundary-IoU) are prior
work (`\bibitem{cldice,biou}`). **Validation (−):** the controlled "R²=0.98" is
circular — δ is injected then recovered (`final_release_audit.md` M1); the only
independent test is 4 datasets, one of which (UAVid) *contradicts* the effect and is
re-spun as "confirmation." **Rigor (−):** the headline CoRe CI prints as `nan`
(`paper_tables/table7_multiseed.md`); thresholds rest on an arbitrary 0.2 gap cutoff
(`FIGURE_PROVENANCE_REPORT.md`). **No new method, no SOTA.** *Recommendation: reject.*

## WEAK REJECT (ITSC reviewer)
**Summary:** Useful, honest, but thin. The width-coupling observation is real and the
failure thresholds are handy for AV evaluation, but the novelty is bounded (it
formalises folk wisdom) and there is **no aerial road-marking evidence** — the target
domain — because SkyScapes is gated (`skyscapes_acquisition_attempt.md`). Real models
on the 25-class task are under-trained (clDice 0.37). With a width-corrected *metric*
(a fix, not just a diagnosis) this would clear the bar. *Recommendation: weak reject,
resubmit.*

## WEAK ACCEPT (fair reviewer)
**Summary:** A crisp, well-scoped evaluation result. The law is derived from geometry,
fit on a controlled experiment (`fit_width_law.py`, inverse-family R²≥0.977 vs linear
0.626), and — post-correction — validated on three real datasets at **measured** widths
(`figA`, validation JSONs), with a clean wide-road negative (UAVid) that the law
predicts. The honesty (null CoRe result, documented scope) is above average. Bounded
novelty keeps it from a strong accept. *Recommendation: weak accept (workshop/ITSC).*

## ACCEPT (champion)
**Summary:** This converts a universally-known annoyance ("IoU is bad for thin things")
into a **predictive, parameterised, validated law with operational thresholds** —
exactly what perception-evaluation practice lacks. Figure A (controlled geometry +
three independent real datasets on one curve) is compelling and now fully reproducible
from measured data. The scope is honestly delimited (topology-error regime excluded;
δ-dependence stated). For an evaluation/benchmarks track this is a clean, useful,
honest contribution. *Recommendation: accept.*

---

## Strongest honest positioning
Lead with the **law + failure thresholds** as an *evaluation-methodology* contribution
for thin-structure (road-marking, lane, vessel, crack) segmentation; target a
**workshop or IEEE ITSC/IV** (~50–70%, `FINAL_RESEARCH_VERDICT.md`), **not** a top-tier
main track. To raise it: (1) add a **width-corrected metric** (diagnosis → cure),
(2) acquire **SkyScapes** for aerial-marking confirmation, (3) fix the **`nan` CoRe CI**
and the **`scikit-image` dependency**. Frame the controlled study as *mechanism
confirmation* (acknowledging its self-consistency) and the **real datasets** as the
independent test.

## Net expected outcome
At an appropriate venue with the three fixes: **borderline accept.** As-is, with the
`nan` CI, the dependency failure, and the circularity unaddressed in the text: **weak
reject** is the realistic modal outcome.
