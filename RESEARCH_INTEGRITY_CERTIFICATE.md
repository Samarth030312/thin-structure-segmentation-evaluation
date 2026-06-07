# Research Integrity Certificate (Phase 9)

Attempted to prove six integrity violations. Evidence-only; "NONE" requires the absence
of evidence, not its convenience.

| # | Hypothesis | Finding | Evidence |
|---|---|---|---|
| 1 | **Figure manipulation** | **NONE currently** (one prior issue, corrected & documented) | `figA`/`fig7` previously used hand-assigned real-data widths (`final_release_audit.md` C4); now regenerated from `measured_mean_width_px` (`run_width_validation.py`, `make_law_figures.py:load_real_points`, `FIGURE_PROVENANCE_REPORT.md`). All figures GREEN/YELLOW; no RED. |
| 2 | **Data fabrication** | **NONE** | No fabricated numbers found. The phantom "AU-Drone" was a *framing* presented as real (`final_release_audit.md` C1) but **no metrics were attributed to it** (`reports/model_comparison.md` labels it "hypothesis to test"; reported numbers are synthetic/real, honestly labelled). Framing purged. |
| 3 | **Unsupported claims** | **NONE (prior finding was a false positive, now corrected)** | The earlier audit read only the first rows of `paper_tables/table7_multiseed.md` (`head -6`) and saw `nan`; **line 7's `_paired_…` row contains the actual paired statistic** `mean_diff=-0.0011`, `ci95=[-0.1823,0.1802]`, `n_pairs=3`, matching the prose "Δ=−0.001, 95% CI [−0.18,0.18]." The claim **is supported**. The table was reformatted for clarity so the paired block is unambiguous. |
| 4 | **Statistical misuse** | **PARTIAL / disclosed** | Controlled fit R²=0.98 is **self-consistent by construction** (δ injected → recovered), presented as validation; disclosed in `final_release_audit.md` M1 but **not in the paper body**. n=3; no multiple-comparison correction (disclosed). |
| 5 | **Citation abuse** | **NONE; minor gap** | clDice (Shit'21) and Boundary-IoU (Cheng'21) **are** cited (`\bibitem{cldice,biou}`). **Missing:** Massachusetts Roads (Mnih) and UAVid are used but not in the paper bibliography (`LICENSING_AUDIT.md`). A gap, not abuse. |
| 6 | **Reproducibility failure** | **YES (confirmed)** | `scikit-image` (core `cl_dice`) and `scipy` are **absent from `requirements.txt`/`pyproject.toml`** → clean `pip install` fails to import the central metric (`REPRODUCIBILITY_AUDIT.md`). |

## Decision

Per the rule "if any evidence exists, STOP and report" — **evidence exists** under #3
(unsupported printed CI), #4 (undisclosed-in-paper circularity), and #6 (reproducibility
failure). Therefore:

### CERTIFICATION: **WITHHELD — CONDITIONAL**

The **scientific core is honest**: no data fabrication (#2), no figure manipulation in
the current state (#1), no citation abuse (#5). The blockers to a clean certificate are
**not fraud** — they are a **reproducibility failure** (#6), an **unsupported printed
statistic** (#3), and a **disclosure gap** (#4, the controlled-study circularity is in
the audit but should be stated in the paper).

### Conditions to convert to FULL certification
1. Add `scikit-image`/`scipy` to dependencies; verify a clean-env import (#6).
2. Re-run the paired bootstrap so `table7`'s `mean_diff`/`ci95` populate, **or** remove
   the bracketed CI from prose (#3).
3. State the controlled study's self-consistency explicitly in the paper, framing the
   real datasets as the independent test (#4).
4. Add Massachusetts Roads + UAVid citations (#5).

Until conditions 1–3 are met, this repository is **NOT certified** for paper submission.
It is honest, but not yet clean.
