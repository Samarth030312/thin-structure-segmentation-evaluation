#!/usr/bin/env bash
set -euo pipefail; cd "$(dirname "$0")/.."
export PYTHONPATH="src:${PYTHONPATH:-}"; export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
for L in ce dice focal; do
  echo "==================== rlmd_unetpp_$L ===================="
  python3 -m uavroadmark.cli.train --config configs/experiment/rlmd_unetpp_${L}.yaml
  python3 -m uavroadmark.cli.evaluate --config configs/experiment/rlmd_unetpp_${L}.yaml --checkpoint outputs/rlmd_unetpp_${L}/best.pth --split test
done
echo "==================== UNETPP 6-LOSS COMPLETE ===================="
