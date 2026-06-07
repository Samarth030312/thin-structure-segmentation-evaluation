# mIoU Failure Thresholds for Thin Structures

At what structure width does mIoU stop being misleading? Quantified from the
controlled experiment (1-px boundary error, 5 seeds) and the law
`Gap = 2δ/(w+2δ)`. "Misleading" = mIoU materially under-reports a correctly-detected
structure (large clDice−mIoU gap).

## 1. Per-band quantification (controlled, δ≈1 px)

| Width band | mean Gap (clDice−mIoU) | relative mIoU under-report | zone |
|---|---|---|---|
| 0–2 px | 0.38–0.55 | 38–55 % | **FAILURE** |
| 2–4 px | 0.27–0.38 | 27–38 % | **FAILURE** |
| 4–6 px | 0.21–0.27 | 21–27 % | **WARNING (high)** |
| 6–10 px | 0.14–0.16 | 14–16 % | **WARNING** |
| 10–15 px | 0.10–0.14 | 10–14 % | WARNING (low) |
| 15+ px | < 0.10 (→0.05 by 25 px) | < 10 % | **SAFE** |

## 2. Zones (Fig. D, `figD_failure_zones`)

- **FAILURE region — width ≲ 5 px (Gap > 0.20).** mIoU under-reports detected
  structure by >20 % (relative). This is the regime of **road markings (2–8 px)**
  and **thin/distant roads**. *Do not* use mIoU alone; report clDice / tolerance-IoU.
- **WARNING region — 5–25 px (0.05 < Gap < 0.20).** mIoU under-reports by 5–20 %.
  Interpret mIoU cautiously; report a topology metric alongside.
- **SAFE region — width ≳ 25 px (Gap < 0.05).** mIoU agrees with clDice to within
  5 %. Wide road surfaces, buildings, large objects — mIoU is reliable here.

## 3. The threshold scales with the model's boundary error δ
The zone boundaries move with δ (the per-side localisation error): the failure
threshold is roughly `w_fail ≈ 8δ` (Gap≈0.2) and the safe threshold `w_safe ≈ 38δ`
(Gap≈0.05). A better-localised model (smaller δ) shrinks the failure region; a
coarser one widens it. For δ≈1 px this gives w_fail≈5–8 px, w_safe≈25–40 px,
matching the table.

## 4. Practical rule of thumb
> If your structures are narrower than ~5× the model's boundary error (≈5 px for
> typical models), **mIoU is misleading — report clDice/tolerance-IoU.** Above
> ~25× the boundary error, mIoU is safe.

This converts the law into an actionable gate for perception evaluation.
