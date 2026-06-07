#!/usr/bin/env bash
# TASK 4: multi-seed the headline comparison (CE+Dice vs CoRe) on U-Net++/RLMD at
# the CONVERGED budget (subsample 500, 12 epochs — identical to the reference
# rlmd_unetpp_{ce_dice,core} seed-42 runs). Seed 42 is reused from those existing
# checkpoints (eval-only); seeds 123 and 999 are trained here. 3 converged seeds
# is the honest, compute-feasible choice (5 seeds at this budget = >2 GPU-hours).
set -uo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="src:${PYTHONPATH:-}"
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
LB=reports/leaderboard_multiseed.csv

# seed 42: reuse the existing converged checkpoints (eval only)
for L in ce_dice core; do
  echo "==================== ms_${L}_s42 (reuse converged ckpt) ===================="
  python3 -m uavroadmark.cli.evaluate --config configs/experiment/rlmd_unetpp_${L}.yaml \
    --checkpoint outputs/rlmd_unetpp_${L}/best.pth --split test \
    --opt run_name=ms_${L}_s42 train.leaderboard="$LB" 2>&1 | grep -E "thin="
done

# seeds 123, 999: train at the converged budget (config defaults: subsample 500, 12 ep)
for S in 123 999; do
  for L in ce_dice core; do
    RN=ms_${L}_s${S}
    echo "==================== $RN ===================="
    python3 -m uavroadmark.cli.train --config configs/experiment/rlmd_unetpp_${L}.yaml \
      --opt seed=$S run_name=$RN train.tensorboard=false train.leaderboard="$LB"
    python3 -m uavroadmark.cli.evaluate --config configs/experiment/rlmd_unetpp_${L}.yaml \
      --checkpoint outputs/$RN/best.pth --split test \
      --opt run_name=$RN train.leaderboard="$LB" 2>&1 | grep -E "thin="
  done
done
echo "==================== MULTISEED COMPLETE ===================="
