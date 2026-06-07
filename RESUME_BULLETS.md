# Resume Bullets

Framed around what the work actually demonstrates: strong engineering, rigorous
evaluation, and scientific honesty. No inflated novelty, no "UAV/SOTA" claims.

## Recommended (pick 3–4)

- Built a **reproducible semantic-segmentation evaluation benchmark** (PyTorch,
  5 architectures, 9 losses, config-driven training, 62 tests, CI) with
  one-command ingestion for multiple real datasets.
- **Identified and quantified a metric-failure mode**: on real road markings, mIoU
  *inverts* the loss ranking — it ranks a frame-flooding model first (top mIoU at
  0.9% pixel accuracy) while topology-aware metrics (centerline-Dice, Boundary-IoU)
  rank correctly; corroborated with a controlled width-stratified study.
- Applied **rigorous statistics** (per-image bootstrap CIs, paired tests,
  multi-seed) and **caught two of my own errors** — a confounded comparison and a
  single-seed result that reversed under multi-seed evaluation.
- Shipped a **deployment path**: TorchScript/ONNX export (bit-exact; ONNX Runtime
  1.47× faster than PyTorch on CPU) and a C++/LibTorch inference engine.
- Profiled the training pipeline (GPU-compute-bound; conv = 85% of CUDA time) and
  worked within a **4 GB GPU** budget via gradient accumulation and fp32 stability
  fixes.

## Honest one-liner

> Built a tested, reproducible road-marking segmentation benchmark and showed,
> with statistics, that the field-standard metric (mIoU) can rank the worst model
> first on thin structures — recommending topology-aware evaluation instead.

## What NOT to claim (integrity guardrails)

- Do **not** say "novel metric" (clDice/Boundary-IoU are prior work).
- Do **not** say "UAV" results (the real data is ground-view).
- Do **not** say the proposed loss (CoRe) "works" (it ties the baseline).
- Do **not** cite absolute accuracy as strong (models were compute-limited).
