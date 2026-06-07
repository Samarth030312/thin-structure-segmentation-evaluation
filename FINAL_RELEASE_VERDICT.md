# Final Release Verdict (Phase 10)

Brutally honest. Evidence-only. No optimism. Scores reflect the repository **as it
exists now**, after the integrity reconstruction but with the Phase 1–9 findings
unfixed.

## Scores

| Dimension | Score /100 | Basis (evidence) |
|---|---|---|
| Research Quality | **68** | derived+validated law (`width_coupling_theory.md`, `figA`), honest negatives; capped by bounded novelty and the **partly-circular** controlled study (`final_release_audit.md` M1) |
| Engineering Quality | **74** | installable package, config system, 62 tests, deploy path — **minus** a **missing core dependency** (`scikit-image`, `REPRODUCIBILITY_AUDIT.md`) and a stale `pyproject` description |
| Reproducibility | **58** | the law reproduces on CPU *after* adding deps; **as-shipped a clean `pip install` fails to import `cl_dice`** (CONFIRMED) |
| Novelty | **45** | the law is IoU's definition made explicit (`law_assessment.md`); metrics are prior work (cited) |
| Publication Readiness | **60** | workshop/ITSC plausible after fixes; blocked now by the `nan` CoRe CI (`table7`) and the dependency failure |
| Professor Readiness | **70** | science is defensible and honest, limits documented — but a professor who runs the install hits the skimage failure and sees the `nan` CI |
| GitHub Readiness | **64** | git repo + verified `.gitignore`; **minus** 16 cluttered top-level docs, contradictory verdicts (50/67/75/78), career-prep files public, stale `pyproject` |
| Portfolio Value | **88** | discovering+formalising a law, a 58-page monograph, controlled+real validation, and a documented integrity process is a strong portfolio artifact |

## Answers

**1. Can this go to GitHub today?** **NO.** Blockers: missing `scikit-image`/`scipy`
deps (clean install fails); `pyproject.toml:8` still says "Indian…"; career-prep and
audit files in the public root; contradictory top-level verdicts. **After ~1 hour of
packaging fixes: yes.**

**2. Can this go to a professor tomorrow?** **CONDITIONALLY.** The *science* is ready to
discuss and honestly scoped. But fix the **dependency failure** and the **`nan` CoRe
CI** first (≈30 min) — otherwise the first `pip install`/table read undermines trust.

**3. Can this go on a resume?** **YES.** The contribution (a derived, validated geometric
law for a universal metric, with a full monograph and honest rigor) is a strong,
defensible resume/portfolio line regardless of the packaging defects (Portfolio 88).
Frame it as *evaluation methodology + engineering rigor*, not a novel model.

**4. Remaining risks.**
- **Reproducibility:** undeclared `scikit-image` → import failure (`REPRODUCIBILITY_AUDIT.md`).
- **Statistical:** `table7` CoRe CI prints `nan`; controlled R²=0.98 is self-consistent
  (circularity not stated in the paper body).
- **Documentation:** stale `pyproject` description; contradictory verdict docs; career
  files public.
- **Legal:** reliance on third-party HF **mirrors** of UAVid/MassRoads with
  **unverified** redistribution rights (`LICENSING_AUDIT.md`).
- **Scientific:** bounded novelty; no aerial road-**markings**.

**5. Exact actions required before release.**
1. Add `scikit-image>=0.20`, `scipy>=1.9` to `requirements.txt` + `pyproject.toml`.
2. Fix `pyproject.toml:8` description (remove "Indian…"; match the paper).
3. Re-run the paired bootstrap to populate `table7` `mean_diff`/`ci95`, **or** delete the
   bracketed CI from prose.
4. Move PRIVATE/ARCHIVE files out of root (career-prep, audits, superseded verdicts);
   keep one current verdict (`GITHUB_RELEASE_PLAN.md`).
5. State the controlled study's self-consistency in the paper; frame real data as the
   independent test.
6. Add Massachusetts Roads + UAVid citations; set a real copyright holder; add
   `CITATION.cff`.
7. Caption `figD` "illustrative" and `fig5` "exploratory/confounded".
8. Verify/replace the UAVid/MassRoads mirror sources or document their licence status.

## Bottom line
**NOT releasable today**, but the gap is **packaging and rigor hygiene (≈1–2 hours),
not fraud.** No fabrication or figure manipulation was found in the current state; the
science is honest and the figures are now measured. Fix the eight items above and the
repository clears **GitHub + professor (workshop/ITSC)**. It is **not** a top-tier paper
— novelty is bounded — and the integrity certificate stays **WITHHELD** until items 1–3
are done.
