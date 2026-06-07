#!/usr/bin/env bash
set -uo pipefail; cd "$(dirname "$0")/.."
export PYTHONPATH="src:${PYTHONPATH:-}"; export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
LB=reports/leaderboard_uav.csv
for S in 42 123 999; do
  echo "==================== uav_massroads_s${S} ===================="
  python3 -m uavroadmark.cli.train --config configs/experiment/uav_massroads.yaml \
    --opt seed=$S run_name=uav_massroads_s${S} train.tensorboard=false train.leaderboard=$LB
  python3 -m uavroadmark.cli.evaluate --config configs/experiment/uav_massroads.yaml \
    --checkpoint outputs/uav_massroads_s${S}/best.pth --split test \
    --opt run_name=uav_massroads_s${S} train.leaderboard=$LB 2>&1 | grep -E "seg=|thin="
done
echo "==================== MASSROADS COMPLETE ===================="
