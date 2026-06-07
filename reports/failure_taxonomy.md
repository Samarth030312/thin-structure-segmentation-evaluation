# Failure Taxonomy

> Automated worst-case analysis on **real RLMD** (U-Net++ + CE+Dice checkpoint,
> 276-image test split), via `scripts/run_failure_analysis.py`. Each prediction
> is scored (½·IoU + ½·clDice); the worst are categorised by interpretable,
> image-derived heuristics. Panels: `reports/visualizations/failure_taxonomy_rlmd/`.

## 1. Failure-mode distribution (worst 50, real data)

| Failure mode | Count | Share | Detection heuristic |
|---|---|---|---|
| **thin_marking** | 28 | 56 % | mean GT marking width < 3 px |
| **shadow / low-contrast** | 22 | 44 % | gray std < 28 or a dark cast-shadow band |
| intersections (high-density) | 0* | — | ≥6 connected marking components |
| sparse | 0* | — | foreground coverage < 2 % |

\* On RLMD the worst-50 are entirely thin/shadow; density/sparse appear further
down the ranking. The *blur / worn-paint / occlusion* modes are
**not directly detectable from the GT/image heuristics alone** (they need EXIF
metadata or a quality classifier we do not have) — see §3.

## 2. Interpretation (evidence-based, real data)

**Thin markings are the dominant real failure (56 %).** Evidence: the worst
frames have sub-3-px GT markings. Mechanism: at the trained resolution, a marking
1-2 px wide produces an encoder edge response near the detection threshold; the
decoder under-segments or breaks it. This is the **same thin-structure
difficulty** the project's clDice/Boundary-IoU protocol was built to *measure* —
the failure taxonomy and the metric thesis point at the same root cause.
*Mitigation:* higher input resolution, the connectivity prior, width-balanced
sampling.

**Shadows / low contrast (44 %).** Evidence: failing frames have low global
contrast or a cast-shadow band. Mechanism: paint-to-asphalt contrast under shadow
falls below the training mode → false negatives concentrate inside shadow.
*Mitigation:* shadow-simulation augmentation, CLAHE, shadow-invariant colour.

## 3. Honest limitation (which requested modes we could and could not isolate)

| Requested mode | Detected? | How / why not |
|---|---|---|
| shadows | ✅ | low-contrast / dark-band heuristic |
| thin / low-resolution markings | ✅ | GT width heuristic (dominant failure) |
| intersections | ✅ (heuristic) | connected-component count |
| **blur** | ✅ (added) | variance-of-Laplacian < 60; **0 cases in RLMD** (clean 1080p footage) — detector works, data has none |
| **worn / faded paint** | ❌ | needs paint-intensity-vs-GT analysis or a quality label we lack |
| **occlusion** | ❌ | needs vehicle detections to test marking overlap |

Blur detection is implemented (and finds none in RLMD's clean footage). Worn-paint
and occlusion remain honest gaps (each needs an extra signal we do not have); the
heuristic taxonomy covers the modes that **actually dominate** RLMD (thin + shadow),
which is the actionable result.

## 4. Autonomy relevance

For a lane-perception stack, the taxonomy says the two engineering priorities are
(1) **thin/low-GSD marking recovery** (resolution + connectivity) and (2)
**shadow robustness** (augmentation) — a concrete, data-driven roadmap rather
than generic "improve the model."

> Reproduce: `python scripts/run_failure_analysis.py --config configs/experiment/rlmd_unetpp_ce_dice.yaml --checkpoint outputs/rlmd_unetpp_ce_dice/best.pth --worst 50`.
