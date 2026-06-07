# Release Diff — Remediation Changes

Every file modified, moved, or created in the final release remediation. No new
experiments; no new claims. Only release blockers were repaired.

## Modified

| File | Change |
|---|---|
| `pyproject.toml` | (1) `description` rewritten from "…Indian road-marking…UAV imagery." to the "When mIoU Lies / width-coupling" framing; (2) added `scikit-image>=0.20` and `scipy>=1.9` to `dependencies`. |
| `requirements.txt` | Added `scikit-image>=0.20` and `scipy>=1.9` (with inline note: required by clDice / controlled study). |
| `paper_tables/table7_multiseed.md` | Reformatted from one table with confusing `nan` cells into (a) a per-loss mean±CI block and (b) an explicit **paired comparison** block (Δ=−0.001, 95% CI [−0.182, 0.180]) + interpretation. The paired CI was always present in the original `_paired_…` row; this makes it unambiguous. |
| `paper_tables/table7_multiseed.tex` | Same reformat as the `.md` (per-loss rows + paired-comparison line). |
| `paper_package/final_ieee_paper.tex` | Added `\bibitem{uavid}` (Lyu et al., ISPRS 2020) and `\bibitem{massroads}` (Mnih thesis, 2013); expanded the LoveDA entry. Bibliography 12 → 14 entries. |
| `paper_package/final_ieee_paper.md` | Added references [14] UAVid and [15] Massachusetts Roads; expanded LoveDA. |
| `paper_package/final_ieee_paper.pdf` | Rebuilt from the updated `.tex` (2 pages). |
| `RESEARCH_INTEGRITY_CERTIFICATE.md` | Corrected finding #3: the CoRe CI is **supported** by `table7`'s paired row; the prior "unsupported" finding was a `head -6` reading error. Integrity decision updated. |
| `TABLE_PROVENANCE_REPORT.md` | Corrected the `table7` "defect" to a false positive; documented the reformat. |

## Moved (renamed) — career/preparation material out of the public root

| From | To |
|---|---|
| `INTERVIEW_GUIDE.md` | `archive/internal/INTERVIEW_GUIDE.md` |
| `RESUME_BULLETS.md` | `archive/internal/RESUME_BULLETS.md` |
| `SYSTEM_DESIGN_DISCUSSION.md` | `archive/internal/SYSTEM_DESIGN_DISCUSSION.md` |
| `reports/resume/` | `archive/internal/resume/` |

## Created

| File | Purpose |
|---|---|
| `archive/internal/` | Directory for internal career/prep material (excluded from the research release). |
| `archive/internal/README.md` | Explains the archive is non-scientific internal material. |
| `FINAL_RELEASE_CHECKLIST.md` | PASS/FAIL for Research Integrity, Reproducibility, Licensing, GitHub Readiness, Professor Readiness (all PASS). |
| `RELEASE_DIFF.md` | This file. |

## Verification performed (no new experiments)
- `from uavroadmark.metrics.thin_structure import cl_dice` imports and runs
  (identity = 1.0) — confirms the dependency fix resolves the import failure.
- Narrative consistency: `pyproject` description, `README.md`, `final_ieee_paper`,
  and `reports/final_report.md` all lead with "When mIoU Lies" / the width-coupling law.
- Paper PDF rebuilt; bibliography now includes `uavid`, `massroads`, `loveda`.
- 62 tests pass.

## NOT changed (out of scope / intentional)
- No figures regenerated (already measured in the prior reconstruction).
- No experiments re-run; the paired CI was *already computed* (only its presentation
  was clarified).
- Bounded-novelty and no-aerial-markings limitations are scientific, not blockers —
  left as documented limitations.
- Redundant top-level verdict docs left in place (housekeeping recommendation in
  `GITHUB_RELEASE_PLAN.md`, not a release blocker).
