#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="src:${PYTHONPATH:-}"
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
for L in ce dice ce_dice tversky focal core; do
  echo "==================== rlmd_unet_$L ===================="
  python3 -m uavroadmark.cli.train --config configs/experiment/rlmd_unet_${L}.yaml
  python3 -m uavroadmark.cli.evaluate --config configs/experiment/rlmd_unet_${L}.yaml \
      --checkpoint outputs/rlmd_unet_${L}/best.pth --split test
done
echo "==================== 6-LOSS ABLATION COMPLETE ===================="
