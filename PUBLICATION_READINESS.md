# Publication Readiness by Venue

> **Historical / superseded.** From the project's initial benchmark-building phase. Current narrative: the **width-coupling law** (`reports/width_coupling_theory.md`, `paper_package/final_ieee_paper.pdf`). Experiments used a synthetic generator plus the public datasets RLMD, LoveDA, Massachusetts Roads, UAVid. See `reports/repository_integrity_report.md`.


Honest readiness percentages. "Readiness" = probability-weighted fit *as-is*,
without further experiments. Justifications are evidence-based.

| Target | Readiness | Verdict |
|---|---|---|
| **GitHub (portfolio repo)** | **90%** | Ready now. |
| **Resume / CV project** | **85%** | Ready now. |
| **Professor / advisor review** | **70%** | Ready as a project to discuss; advisor will push on scale + novelty. |
| **Workshop paper** (CVPR/ICCV ADW, etc.) | **50%** | Borderline; needs reframing + ideally converged runs. |
| **IEEE ITSC** (conference) | **30%** | Not ready; needs converged real-data + scope fix. |
| **WACV** (main) | **20%** | Not ready; novelty too low for a vision main track. |
| **IEEE T-ITS** (journal) | **15%** | Not ready; journal needs substantially more. |

---

### GitHub — 90%
**Why high:** clean installable package, 62 tests, CI, docs, 3 real-dataset
ingestions, deployment path, reproducible commands. This is a high-quality OSS
repo. **Missing 10%:** README still carries the original "UAV/road-marking" framing and
an out-of-date claim or two; a short, honest "what this is / what it shows /
limitations" top section would finish it.

### Resume / CV — 85%
**Why high:** demonstrates the full stack (data → training → evaluation →
statistics → deployment → C++/ONNX) plus scientific honesty (caught own errors).
Strong interview material. **Missing 15%:** the headline result is modest; frame
the bullet around *engineering + evaluation rigor*, not a novel method.

### Professor review — 70%
**Why:** a good, honest project an advisor can build on. **Gap:** an advisor will
immediately ask for (a) converged experiments and (b) a sharper novelty statement,
and will note the UAV scope mismatch.

### Workshop — 50%
**Why borderline:** the topology-aware evaluation angle is workshop-appropriate and
the honesty is appealing; the synthetic mechanism study is clean. **Gaps:** real
models are under-trained (best clDice 0.37); UAV framing unsupported; novelty
incremental. Reframed to "topology-aware evaluation of thin-structure segmentation"
+ one converged real run → ~70%.

### IEEE ITSC — 30%
**Why low:** topical fit is good (ITS/road perception) but the experimental power
and novelty are below bar; no real UAV results despite the framing. Needs converged
runs, a defensible (significant) statistical claim, and the scope fix.

### WACV — 20%
**Why low:** WACV expects methodological novelty or a strong new benchmark/SOTA.
This offers neither — existing metrics, a null method, under-trained models.

### T-ITS — 15%
**Why low:** a journal needs comprehensive experiments, multiple real datasets at
scale, baselines, and a clear advance. This is an early-stage study by that bar.

---

## What moves the needle (and to where)

| Action | New best-fit readiness |
|---|---|
| Reframe to "thin-structure evaluation" (no compute) | Workshop 50→65% |
| + Converged full-RLMD runs (≥12 GB GPU) | Workshop 65→80%, ITSC 30→50% |
| + Real UAV markings (SkyScapes) + larger seed/loss set | ITSC 50→70%, T-ITS 15→40% |

**One-line:** publishable at a **workshop** after reframing + one converged run;
**not** publishable at a competitive main venue without real UAV data and scale.
