# Licensing Audit (Phase 5)

## Code licence
- `LICENSE`: **MIT**, "Copyright (c) 2026 UAV RoadMark Benchmark Authors". Valid MIT
  text. **Minor:** the copyright holder is a generic placeholder ("…Authors") — set a
  real name/org before release.

## Dataset licences (`DATA_LICENSES.md`)
The file correctly flags non-commercial / research-only datasets and states no
redistribution. Verified that **no datasets and no checkpoints are committed** (git
`.gitignore` covers `datasets/*/`, `outputs/`, `*.pth`, `*.ts.pt`, `*.onnx`; the audit
confirmed 0 such files staged).

## Risks (CONFIRMED / flagged)

| Risk | Severity | Evidence / note |
|---|---|---|
| **MIT code + non-commercial data conflation** | Medium | LoveDA is **CC-BY-NC**; UAVid is **research-only**. A user could wrongly assume the MIT licence makes the *whole pipeline* commercially usable. `DATA_LICENSES.md` mitigates, but the README must keep the caveat prominent. |
| **Third-party dataset MIRRORS — authorization NOT VERIFIED** | **Medium-High** | The ingestion uses Hugging Face mirrors: UAVid `arakesh/uavid-15-hq-mixedres` and Massachusetts Roads `asolodin/massachusetts_roads_dataset_500`. **UAVid's original terms require registration**; whether these mirrors are authorized redistributions is **NOT VERIFIED**. Relying on (and scripting downloads from) a possibly-unauthorized mirror is a licensing risk. |
| **Derived checkpoints from NC data** | Low (mitigated) | Models trained on LoveDA/UAVid are derivative works under NC terms; they are **git-ignored and not redistributed**, so no current violation. Do **not** publish those checkpoints. |
| **Citation obligations** | Low | `DATA_LICENSES.md` instructs citing source papers; the paper cites LoveDA and RLMD (`\bibitem{loveda}`, `\bibitem{rlmd}`). Massachusetts Roads (Mnih) and UAVid are **not** in the paper bibliography — add them. |
| **Synthetic generator** | None | in-repo, MIT. |

## NOT VERIFIED
- The exact licence text/terms of each HF mirror were **not re-fetched** in this audit.
- Whether the UAVid/MassRoads mirrors hold redistribution rights — **NOT VERIFIED**.

## Verdict
No dataset or checkpoint is redistributed, so there is **no direct redistribution
violation in the repo today**. The real exposure is (1) **reliance on third-party
dataset mirrors of unverified authorization** (especially UAVid, which is normally
registration-gated), and (2) **NC/research-only terms** that the MIT code licence could
obscure. Before release: name a real copyright holder, add Massachusetts Roads + UAVid
citations, verify the mirrors' redistribution rights or point ingestion at the
official sources, and keep the NC caveat prominent.
