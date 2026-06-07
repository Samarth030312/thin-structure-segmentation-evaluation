#!/usr/bin/env bash
set -uo pipefail; cd "$(dirname "$0")/.."
export PYTHONPATH="src:${PYTHONPATH:-}"; export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
LB=reports/leaderboard_xdomain.csv
echo "### train LoveDA"; python3 -m uavroadmark.cli.train --config configs/experiment/xd_loveda_bin.yaml
echo "### RLMD->RLMD";   python3 -m uavroadmark.cli.evaluate --config configs/experiment/xd_rlmd_bin.yaml   --checkpoint outputs/xd_rlmd_bin/best.pth   --split test --opt run_name=xd_rlmd_to_rlmd     train.leaderboard=$LB 2>&1 | grep -E "seg=|thin="
echo "### RLMD->LoveDA"; python3 -m uavroadmark.cli.evaluate --config configs/experiment/xd_loveda_bin.yaml --checkpoint outputs/xd_rlmd_bin/best.pth   --split test --opt run_name=xd_rlmd_to_loveda   train.leaderboard=$LB 2>&1 | grep -E "seg=|thin="
echo "### LoveDA->LoveDA"; python3 -m uavroadmark.cli.evaluate --config configs/experiment/xd_loveda_bin.yaml --checkpoint outputs/xd_loveda_bin/best.pth --split test --opt run_name=xd_loveda_to_loveda train.leaderboard=$LB 2>&1 | grep -E "seg=|thin="
echo "### LoveDA->RLMD"; python3 -m uavroadmark.cli.evaluate --config configs/experiment/xd_rlmd_bin.yaml   --checkpoint outputs/xd_loveda_bin/best.pth --split test --opt run_name=xd_loveda_to_rlmd   train.leaderboard=$LB 2>&1 | grep -E "seg=|thin="
echo "### XD DONE"
