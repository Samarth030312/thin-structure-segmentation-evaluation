#!/usr/bin/env bash
# Headline experiment: loss ablation for the thin-structure thesis.
# Trains U-Net (R34) on synthetic_lg with each loss, holding everything else
# fixed, then evaluates with BOTH standard and thin-structure metrics.
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="src:${PYTHONPATH:-}"
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

LOSSES=(ce_dice tversky cldice core)
for L in "${LOSSES[@]}"; do
  echo "==================== LOSS: $L ===================="
  python3 -m uavroadmark.cli.train \
      --config configs/experiment/abl_unet_${L}.yaml
  python3 -m uavroadmark.cli.evaluate \
      --config configs/experiment/abl_unet_${L}.yaml \
      --checkpoint outputs/abl_unet_${L}/best.pth --split test
done
echo "==================== ABLATION COMPLETE ===================="
python3 -c "from uavroadmark.report.leaderboard import render_markdown; \
            print(render_markdown('reports/leaderboard.csv'))"
