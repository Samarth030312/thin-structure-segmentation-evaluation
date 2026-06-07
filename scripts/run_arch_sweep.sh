#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="src:${PYTHONPATH:-}"
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
for M in deeplabv3plus segformer pspnet unetpp; do
  echo "==================== ARCH: $M ===================="
  python3 -m uavroadmark.cli.train --config configs/experiment/arch_${M}.yaml
  python3 -m uavroadmark.cli.evaluate --config configs/experiment/arch_${M}.yaml \
      --checkpoint outputs/arch_${M}/best.pth --split test
done
echo "==================== ARCH SWEEP COMPLETE ===================="
