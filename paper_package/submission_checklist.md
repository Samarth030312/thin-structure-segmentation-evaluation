# Submission Checklist

## Content
- [x] Abstract reflects corrected findings (mis-ranking headline; CoRe multi-seed tie)
- [x] Every quantitative claim cites a result file (`reports/claim_audit.md`)
- [x] Real-data primary evidence (RLMD); synthetic clearly scoped to mechanism
- [x] Honest limitations section (compute, ground-view, CoRe)
- [ ] Aerial-UAV (SkyScapes) result — *blocked*: license + GPU; ingestion ready
- [x] Statistical rigor: bootstrap CIs + paired significance tests
- [x] Multi-seed mean±std/CI for headline — multi-seed analysis done (3 seeds; overturned single-seed claim)

## Figures (paper_figures/, 300 DPI + PDF vector)
- [x] Fig 1 width study · [x] Fig 2 loss ablation · [x] Fig 3 perf Pareto
- [x] Fig 4 stats CI · [ ] Fig 5 cross-dataset 
- [x] Consistent style (colour-blind-safe palette, no top/right spines)

## Tables (paper_tables/)
- [x] auto-extracted from result CSVs (`scripts/make_paper_tables.py`)
- [x] regenerate-able / reproducible

## Reproducibility
- [x] Seeds fixed; configs committed; commands in each report
- [x] 62 unit/integration tests pass
- [x] CI workflow (`.github/workflows/ci.yml`)
- [x] Data ingestion scripts (RLMD, LoveDA, SkyScapes) + validators
- [x] Hardware report (`reports/system_report.md`)

## Writing
- [ ] Anonymise for double-blind (remove repo URL/author hints)
- [ ] Page limit pass (ITSC 6+1)
- [ ] Spell/grammar; figure refs; table refs
- [ ] References complete (`citation_checklist.md`)

## Ethics / licensing
- [x] RLMD MIT; LoveDA CC-BY-NC-SA (research use); SkyScapes DLR agreement noted
- [x] No PII; driving scenes are public datasets
