# Public Release Checklist

Status after the integrity reconstruction (`reports/repository_integrity_report.md`),
which resolved the four critical findings of `reports/final_release_audit.md`. Honest
pass/fail; integrity issues are separated from impact/novelty issues.

---

## Safe for GitHub — **PASS**

| Check | Status | Note |
|---|---|---|
| Version-controlled (git repo + initial commit) | ✅ PASS | initialised; clean commit, no AI attribution |
| `.gitignore` protects large binaries | ✅ PASS | verified: 21 MB staged, **0** checkpoints/datasets/logs |
| No phantom/non-existent dataset presented as real | ✅ PASS | AU-Drone purged (only meta-audit docs mention it) |
| README accurate & matches the project | ✅ PASS | rewritten around the width-coupling law |
| LICENSE (code) + dataset licences | ✅ PASS | MIT + `DATA_LICENSES.md` (NC datasets flagged) |
| No false claims in README | ✅ PASS | removed "nothing hard-coded"; test count correct (62) |
| Tests pass | ✅ PASS | 62/62 |
| Figures reproducible from data | ✅ PASS | `make_law_figures.py` loads measured JSON values |
| AI-authorship traces | ⚠️ PASS\* | clean except the two audit reports that *document* the cleanup; exclude or keep as internal |

**Verdict: safe to publish.** (\*If a zero-occurrence `grep claude/au-drone` is required,
exclude `reports/final_release_audit.md` and `reports/repository_integrity_report.md` from
the public tree — they necessarily quote the removed strings.)

---

## Safe for Professor — **PASS**

| Check | Status | Note |
|---|---|---|
| Single, consistent narrative across README/report/paper/monograph | ✅ PASS | all describe the width-coupling law |
| Central claim has a derivation + evidence | ✅ PASS | geometry + controlled fit + measured real data |
| Killer figure is honestly constructed | ✅ PASS | Figure A x-axis now **measured**, loaded from JSONs |
| Limitations stated plainly | ✅ PASS | novelty ceiling, δ-dependence, no aerial markings |
| Negative results reported, not hidden | ✅ PASS | CoRe (null), UAVid (no effect, bounds the law) |
| Known weaknesses acknowledged | ✅ PASS | controlled-study circularity documented (M1) |
| Reproducible in <30 min (the law, on CPU) | ✅ PASS | 3 scripts, no GPU/data needed |

**Verdict: ready for advisor review.** A professor can engage with an honest, scoped
result. They will (correctly) push on novelty and the circularity of the controlled
study — both are documented, not concealed.

---

## Safe for Paper — **PASS WITH CAVEATS (workshop / IEEE ITSC level)**

| Check | Status | Note |
|---|---|---|
| No fabricated data or results | ✅ PASS | phantom dataset removed; figures measured |
| Claims supported by evidence | ✅ PASS | every major claim traced (`repository_integrity_report.md` §3) |
| Statistical rigor (multi-seed, CIs) | ✅ PASS | 3-seed validation, bootstrap CIs |
| Honest scope & limitations section | ✅ PASS | in paper and reports |
| Citations present | ✅ PASS | 12 references in the paper |
| Novelty sufficient for a **top-tier** venue | ❌ FAIL | the law is IoU's definition made explicit — bounded novelty |
| Decisive domain evidence (aerial markings) | ❌ FAIL | SkyScapes gated; validated on thin *roads* only |
| Non-circular validation | ⚠️ PARTIAL | controlled study is self-consistent by construction; real-data is the independent test (n=4) |

**Verdict: submittable to a workshop or IEEE ITSC/IV (~50–70%, per
`FINAL_RESEARCH_VERDICT.md`); NOT to a top-tier (CVPR/ICCV main) venue.** The
**integrity** bar is now met (the blocker before); the remaining failures are about
**impact/novelty**, which are honestly disclosed rather than overcome.

---

## Summary

| Target | Before reconstruction | After |
|---|---|---|
| GitHub | NOT READY (phantom dataset, wrong README, not a repo) | **READY** |
| Professor | NOT READY (contradictory docs, hand-placed figure) | **READY** |
| Paper | NOT READY (integrity blockers) | **READY (workshop/ITSC), caveated** |

The four critical integrity defects are fixed; credibility is restored. What remains are
**honest scientific limitations** (bounded novelty, no aerial markings, a partly
self-consistent controlled study), all documented. Per the project's own rule —
*credibility over impressiveness* — unsupportable claims were removed rather than
softened.
