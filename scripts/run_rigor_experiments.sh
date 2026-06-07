#!/usr/bin/env bash
# Scientific-rigor experiments (4 GB-feasible):
#  E2: multi-seed converged SYNTHETIC (CE+Dice & CoRe, seeds 123/999; seed 42 exists)
#      -> width-study bootstrap CIs for the primary (width-coupling) claim.
#  E1: ONE converged BINARY RLMD run, 30 epochs -> learning curve rebutting "under-trained".
set -uo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="src:${PYTHONPATH:-}"
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
LB=reports/leaderboard_rigor.csv

for L in ce_dice core; do
  for S in 123 999; do
    echo "==================== synth_${L}_s${S} ===================="
    python3 -m uavroadmark.cli.train --config configs/experiment/abl_unet_${L}.yaml \
      --opt seed=$S run_name=synth_${L}_s${S} train.tensorboard=false train.leaderboard="$LB"
  done
done

echo "==================== rlmdbin_converge (30ep learning curve) ===================="
python3 -m uavroadmark.cli.train --config configs/experiment/xd_rlmd_bin.yaml \
  --opt run_name=rlmdbin_converge train.epochs=30 dataset.subsample=600 \
        train.tensorboard=false train.leaderboard="$LB"
python3 -m uavroadmark.cli.evaluate --config configs/experiment/xd_rlmd_bin.yaml \
  --checkpoint outputs/rlmdbin_converge/best.pth --split test \
  --opt run_name=rlmdbin_converge train.leaderboard="$LB" 2>&1 | grep -E "thin="
echo "==================== RIGOR EXPERIMENTS COMPLETE ===================="
