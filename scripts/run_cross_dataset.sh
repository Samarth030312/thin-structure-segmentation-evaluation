#!/usr/bin/env bash
# TASK 2: cross-dataset generalization (binary foreground). Train on each, eval 2x2.
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="src:${PYTHONPATH:-}"
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
LB=reports/leaderboard_xdomain.csv

echo "### train on RLMD (markings)"; python3 -m uavroadmark.cli.train --config configs/experiment/xd_rlmd_bin.yaml
echo "### train on LoveDA (road)";   python3 -m uavroadmark.cli.train --config configs/experiment/xd_loveda_bin.yaml

# 2x2 evaluation (in-domain diagonal + cross off-diagonal). Same arch + num_classes=2.
echo "### RLMD->RLMD";   python3 -m uavroadmark.cli.evaluate --config configs/experiment/xd_rlmd_bin.yaml   --checkpoint outputs/xd_rlmd_bin/best.pth   --split test --opt run_name=xd_rlmd_to_rlmd     train.leaderboard=$LB
echo "### RLMD->LoveDA"; python3 -m uavroadmark.cli.evaluate --config configs/experiment/xd_loveda_bin.yaml --checkpoint outputs/xd_rlmd_bin/best.pth   --split test --opt run_name=xd_rlmd_to_loveda   train.leaderboard=$LB
echo "### LoveDA->LoveDA"; python3 -m uavroadmark.cli.evaluate --config configs/experiment/xd_loveda_bin.yaml --checkpoint outputs/xd_loveda_bin/best.pth --split test --opt run_name=xd_loveda_to_loveda train.leaderboard=$LB
echo "### LoveDA->RLMD"; python3 -m uavroadmark.cli.evaluate --config configs/experiment/xd_rlmd_bin.yaml   --checkpoint outputs/xd_loveda_bin/best.pth --split test --opt run_name=xd_loveda_to_rlmd   train.leaderboard=$LB
echo "### CROSS-DATASET COMPLETE"
