# GitHub Release Plan (Phase 8)

Classification of every major path: **PUBLIC** (safe + useful), **PRIVATE** (keep
local), **ARCHIVE** (historical, move out of the front page).

## PUBLIC
```
README.md  LICENSE  DATA_LICENSES.md  pyproject.toml  requirements*.txt
src/uavroadmark/      # package
scripts/              # the science (controlled study, fit, figures, validation, ingestion)
configs/              # YAML composition + custom_dataset.yaml template
tests/                # 62 tests
paper_package/        # final_ieee_paper.{md,tex,pdf}
docs/UAV_Roadmark_Master_Monograph.{md,pdf}  docs/{training,evaluation}_guide.md  docs/architecture.md
paper_figures/        # figA-D, fig1b, fig6, fig7 (GREEN); figD/fig5 caption as illustrative/exploratory
paper_tables/         # table2 (verified); others trace to archived reports
reports/  (LAW SUBSET): width_coupling_theory, first_principles_width_analysis,
   failure_thresholds, controlled_robustness_study, reviewer_attack_campaign,
   law_assessment, metric_sensitivity_analysis, multiseed_width_study,
   massroads_width_validation, uav_*_*, skyscapes_acquisition_attempt, final_report
deploy/  (code only; deploy/models/* are git-ignored)
```

## PRIVATE (do NOT publish)
```
INTERVIEW_GUIDE.md  RESUME_BULLETS.md  SYSTEM_DESIGN_DISCUSSION.md   # career-prep; unprofessional in a public research repo
reports/resume/                                                     # interview_prep etc.
outputs/   datasets/   deploy/models/*.ts.pt                        # already git-ignored (27 GB + checkpoints)
REPOSITORY_TRUTH_AUDIT.md  FIGURE_PROVENANCE_REPORT.md  TABLE_PROVENANCE_REPORT.md
REPRODUCIBILITY_AUDIT.md  LICENSING_AUDIT.md  RESEARCH_INTEGRITY_CERTIFICATE.md
FINAL_RELEASE_VERDICT.md  reports/final_release_audit.md  reports/repository_integrity_report.md
   # internal audits; they necessarily quote removed strings ("AU-Drone"). Keep local
   # or in a separate /audit branch, not on the public landing page.
```

## ARCHIVE (historical; move to `archive/` or a tag, not the root)
```
FINAL_VERDICT.md  PUBLICATION_READINESS.md  PUBLISHABILITY_UPGRADE_REPORT.md
PROJECT_READINESS_REPORT.md  UAV_VALIDATION_VERDICT.md  PAPER_POSITIONING.md
PROFESSOR_REVIEW.md  REVIEWER_SIMULATION.md  FIGURE_AUDIT.md  PUBLIC_RELEASE_CHECKLIST.md
reports/{dataset_selection_report, model_comparison, loss_function_study, dataset_ranking,
   dataset_survey, final_dataset_selection, foundation_model_study, architecture_analysis,
   claim_audit, literature_review, ...}   # banner-superseded initial-phase reports
notebooks/ORIGINAL_NOTEBOOK_CRITIQUE.md
```
**Reason:** these are the source of the **contradictory-verdict** clutter (publishability
variously 50/67/75/78 across `FINAL_VERDICT`, `FINAL_RESEARCH_VERDICT`,
`PUBLISHABILITY_UPGRADE_REPORT`, `UAV_VALIDATION_VERDICT`). Keep exactly **one** current
verdict (`FINAL_RESEARCH_VERDICT.md`) visible; archive the rest.

## Recommended top-level after cleanup
```
README.md  LICENSE  DATA_LICENSES.md  CITATION.cff
pyproject.toml  requirements.txt  requirements-dev.txt
src/  scripts/  configs/  tests/  docs/  paper_package/  paper_figures/  paper_tables/  reports/  deploy/
archive/   (historical reports + superseded verdicts)
```

## Recommended `.gitignore` additions (current one is good; add)
```
# already present: outputs/ datasets/*/ *.pth *.ckpt *.onnx *.ts.pt
# add for a clean public repo:
INTERVIEW_GUIDE.md
RESUME_BULLETS.md
SYSTEM_DESIGN_DISCUSSION.md
reports/resume/
*_AUDIT.md
RESEARCH_INTEGRITY_CERTIFICATE.md
FINAL_RELEASE_VERDICT.md
reports/final_release_audit.md
reports/repository_integrity_report.md
docs/_monograph_parts/    # keep the built .md/.pdf, drop the loose parts
*.aux *.log *.toc *.out    # latex intermediates
```

## Recommended README structure (already implemented)
TL;DR (the law) → Start-here table → reproduce (CPU) → what's-in-the-box → datasets →
findings → **limitations** → data & licences → tests → citation → licence. **Keep the
limitations and licence sections prominent.**

## Release package
A GitHub Release attaching: `paper_package/final_ieee_paper.pdf`,
`docs/UAV_Roadmark_Master_Monograph.pdf`, and a `figures.zip`. **Do not** attach
checkpoints (NC-derived) or datasets.

## Must-fix before flipping public
1. Add `scikit-image`/`scipy` to deps (`REPRODUCIBILITY_AUDIT.md`).
2. Fix `pyproject.toml:8` description (still "Indian…").
3. Move PRIVATE/ARCHIVE files out of root.
4. Add a real copyright holder + `CITATION.cff` + MassRoads/UAVid citations.
