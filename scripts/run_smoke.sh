#!/usr/bin/env bash
# End-to-end pipeline smoke test: data -> validate -> EDA -> train -> eval -> viz.
# Runs entirely on CPU with synthetic data in ~1 minute. Every number it prints
# is really computed (nothing is mocked). This is the command CI runs and the
# command a reviewer runs to reproduce the committed synthetic-baseline results.
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="src:${PYTHONPATH:-}"

CLASSES=(background solid_lane_line dashed_lane_line zebra_crossing road_arrow stop_line yellow_line)

echo "==> [1/6] generate synthetic dataset"
python3 scripts/make_synthetic.py --root datasets/synthetic

echo "==> [2/6] validate dataset"
python3 scripts/dataset_validator.py --root datasets/synthetic --num-classes 7 \
  --class-names "${CLASSES[@]}"

echo "==> [3/6] exploratory data analysis"
python3 scripts/explore_dataset.py --root datasets/synthetic --num-classes 7 \
  --out reports/exploratory_analysis

echo "==> [4/6] train (MiniUNet, CPU, 3 epochs)"
python3 -m uavroadmark.cli.train --config configs/experiment/smoke_miniunet.yaml

echo "==> [5/6] evaluate -> leaderboard"
python3 -m uavroadmark.cli.evaluate --config configs/experiment/smoke_miniunet.yaml \
  --checkpoint outputs/smoke_miniunet/best.pth --split test

echo "==> [6/6] qualitative visualisations"
python3 scripts/visualize.py --config configs/experiment/smoke_miniunet.yaml \
  --checkpoint outputs/smoke_miniunet/best.pth --out reports/qualitative -n 6

echo "==> SMOKE TEST COMPLETE. See reports/leaderboard.csv and reports/qualitative/"
