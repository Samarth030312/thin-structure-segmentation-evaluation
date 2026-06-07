# Final Paper Positioning

The discovery of a derived, confirmed, scoped **width-coupling law** changes the
positioning: the paper is no longer "mIoU is bad on thin things" (known) but "here
is the *quantitative geometric law* for when and by how much, validated on real
data." That is a stronger, more novel contribution.

## Options evaluated

| Option | Story | Strength | Issue |
|---|---|---|---|
| A. "When mIoU Lies" | metric failure, catchy | great hook | undersells the law (sounds qualitative) |
| **B. "The Width-Coupling … Law of Segmentation Metrics"** | the derived law | **most novel; now justified by evidence** | "theory/law" must be defended — it is (derivation + R²=0.98 + 3 real datasets + 10 attacks) |
| C. "Thin-Structure Evaluation for Aerial Perception" | applied/benchmark | venue-fit (ITSC) | undersells; applied framing hides the law |
| D. "Topology-Aware Evaluation of Thin Structures" | protocol | safe | generic; low novelty |

## Recommendation — combine A's hook with B's substance

> **Title:** *"When mIoU Lies: A Geometric Width-Coupling Law for Thin-Structure
> Segmentation Metrics."*

Lead the abstract with the **law** (`Gap = 2δ/(w+2δ)`, derived + confirmed), then
the controlled and real-data evidence, the failure thresholds (the practical
payload), and the honest scope. The mis-ranking and CoRe results become secondary.

## Novelty analysis

| Contribution | Novelty | Why |
|---|---|---|
| **The width-coupling law** (derived + confirmed + scoped) | **Moderate-High** | quantitative, mechanistic, falsifiable, validated out-of-sample on real data; turns a folk observation into a predictive law with failure thresholds — not previously formalised for road-marking/thin-structure evaluation |
| Failure-threshold zones (safe/warning/failure) | Moderate | actionable, derived from the law; directly usable by AV eval teams |
| Real multi-dataset validation + thinness threshold | Moderate | real aerial confirmation + the wide-road negative (UAVid) bounding it |
| clDice/Boundary-IoU/Tol-IoU protocol | Low | existing metrics, assembled and applied |
| CoRe loss | Low/null | supplementary negative result |

## Reviewer appeal
- **Pro:** a derived law with R²=0.98 controlled fit and real-data confirmation is
  unusually crisp for an evaluation paper; the failure thresholds are immediately
  useful; the honesty (negative UAVid, scoped law) reads as rigorous.
- **Con:** the underlying metrics are prior work; δ is model-dependent; experiments
  are compute-bounded; no aerial-*marking* data. A skeptic may call the law "a
  re-expression of IoU's definition" — to which the answer is: yes, made explicit,
  parameterised, thresholded, and validated, which is the contribution.

## Publication probability (with the law as the lead)

| Venue | Probability | Note |
|---|---|---|
| Workshop (CVPR/ICCV ADW, WACV-W) | **~70%** | the law + thresholds + honesty are a clean workshop story |
| IEEE ITSC / IV | **~50%** | strong topical fit; the law is a real contribution; scale/markings are the risk |
| IROS | ~30% | perception-evaluation angle, but robotics-systems fit is weaker |
| WACV (main) | ~30% | needs more breadth/novelty for a main track |
| CVPR (main) | <15% | bar too high without a method/SOTA |
| T-ITS (journal) | ~35% | viable after full-scale + aerial-marking validation |

## One-line positioning
*A folk wisdom ("IoU is bad for thin structures") is made into a derived, confirmed,
thresholded geometric law — with the precise width at which mIoU becomes misleading,
validated on real aerial data.*
