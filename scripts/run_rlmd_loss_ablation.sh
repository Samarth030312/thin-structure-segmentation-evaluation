#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="src:${PYTHONPATH:-}"
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
for E in rlmd_unetpp_ce_dice rlmd_unetpp_tversky; do
  echo "==================== $E ===================="
  python3 -m uavroadmark.cli.train --config configs/experiment/${E}.yaml
  python3 -m uavroadmark.cli.evaluate --config configs/experiment/${E}.yaml \
      --checkpoint outputs/${E}/best.pth --split test
done
echo "==================== RLMD LOSS ABLATION COMPLETE ===================="
