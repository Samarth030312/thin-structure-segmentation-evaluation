# UAV Adversarial Review

Assume the paper is wrong. For each major claim, the strongest attack and whether
the claim survives the new real-UAV evidence.

## Claim 1 — "mIoU under-reports correctly-detected thin structures"
**Attack (strongest, and it lands partially):** on real UAV data (UAVid, 3 seeds,
converged), the effect is **absent** — mIoU ≈ clDice (0.570 vs 0.567), and the
thin-tertile IoU–clDice gap is +0.007 (≈0). corr(width, IoU) is even *negative*.
**Outcome: survives only in SCOPED form.** The claim is **thinness-bounded**: it
holds for ≲ few-px structures (synthetic 2 px gap +0.65; thin aerial LoveDA roads
<6 px gap +0.22) and *correctly vanishes* for wide UAVid roads. The unqualified
"mIoU under-reports thin structures" must be rewritten as "mIoU under-reports
correctly-detected **genuinely thin (≲ few-px)** structures; for wide structures it
agrees with topology metrics." The mechanism (width-coupling) *predicts* this
boundary, so the scoped claim is actually strengthened by the negative result.

## Claim 2 — "mIoU mis-ranks losses under extreme multi-class imbalance"
**Attack:** is it imbalance or just bad models? **Outcome: survives, scoped.** It
is explicitly a multi-class extreme-imbalance phenomenon (RLMD 609:1); the
three-test analysis shows all-class mIoU also fails and FWIoU/PixAcc are
insensitive. Not tested on UAV (binary road, no imbalance) — and we do not claim it
there. Unaffected by the UAV result.

## Claim 3 — "topology metrics (clDice) are the right tool"
**Attack:** on UAVid, clDice tracks mIoU, so it adds nothing there. **Outcome:
survives, scoped.** clDice equals mIoU when structures are wide (no harm) and
diverges (correctly) when they are thin. It is never *worse* than mIoU and is
better in the thin regime — a safe default. The UAVid agreement is evidence it is
not spurious.

## Claim 4 — "the CoRe loss helps"
Already retracted (multi-seed tie). Untouched by UAV evidence.

## Claim 5 — "the framework produces converged real models"
**Attack:** the 25-class RLMD models were under-trained. **Outcome: survives,
strengthened.** Converged binary models now exist on three real sources: RLMD
(clDice 0.64), LoveDA (clDice 0.64), UAVid (clDice 0.57, mIoU 0.57). The framework
converges when the task is well-posed.

## Net result of the adversarial pass
- **No claim was fabricated or salvaged dishonestly.** One claim (Claim 1) was
  **narrowed** by a genuine real-UAV contradiction; one (Claim 5) was strengthened.
- The paper's load-bearing statement is now: *mIoU under-reports correctly-detected
  thin (≲ few-px) structures; demonstrated on synthetic markings (CI-tight),
  supported on thin real aerial roads, and shown to be correctly absent on wide UAV
  roads — i.e. a measured thinness threshold.*
- **The "insufficient UAV evidence" objection is partially addressed (real UAV
  models + a real-UAV test of the claim) but not eliminated**: the decisive UAV
  case (aerial *markings*) needs gated data. We state this rather than overclaim.
