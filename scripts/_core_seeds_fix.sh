#!/usr/bin/env bash
set -uo pipefail; cd "$(dirname "$0")/.."
export PYTHONPATH="src:${PYTHONPATH:-}"; export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
LB=reports/leaderboard_multiseed.csv
for S in 123 999; do
  RN=ms_core_s${S}
  echo "==================== $RN (bs2/ga4) ===================="
  python3 -m uavroadmark.cli.train --config configs/experiment/rlmd_unetpp_core.yaml \
    --opt seed=$S run_name=$RN train.batch_size=2 train.grad_accum=4 \
          train.tensorboard=false train.leaderboard="$LB"
  python3 -m uavroadmark.cli.evaluate --config configs/experiment/rlmd_unetpp_core.yaml \
    --checkpoint outputs/$RN/best.pth --split test --opt run_name=$RN train.leaderboard="$LB" 2>&1 | grep -E "thin="
done
echo "==================== CORE SEEDS FIX COMPLETE ===================="
