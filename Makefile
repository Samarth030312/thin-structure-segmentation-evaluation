.PHONY: help install install-dev synth validate eda smoke train eval viz test lint clean

PY ?= python3
LABEL_MODE ?= id
export PYTHONPATH := src

help:
	@echo "make install      - install runtime deps"
	@echo "make install-dev  - install dev deps (pytest, ruff)"
	@echo "make smoke        - full pipeline on synthetic data (CPU, ~1 min)"
	@echo "make synth        - generate synthetic dataset"
	@echo "make validate     - validate synthetic dataset (-> JSON/HTML)"
	@echo "make eda          - exploratory data analysis"
	@echo "make test         - run the test suite"
	@echo "make lint         - ruff lint"
	@echo "make clean        - remove outputs/ and caches"

install:
	$(PY) -m pip install -r requirements.txt
	$(PY) -m pip install -e .

install-dev: install
	$(PY) -m pip install pytest pytest-cov ruff tabulate

synth:
	$(PY) scripts/make_synthetic.py --root datasets/synthetic

validate:
	$(PY) scripts/dataset_validator.py --root datasets/synthetic --num-classes 7 \
		--class-names background solid_lane_line dashed_lane_line zebra_crossing \
		road_arrow stop_line yellow_line

eda:
	$(PY) scripts/explore_dataset.py --root datasets/synthetic --num-classes 7

smoke:
	bash scripts/run_smoke.sh

# --- real data: SkyScapes-Lane (drop raw into datasets/skyscapes_raw first) ---
skyscapes-inspect:
	$(PY) scripts/prepare_skyscapes.py inspect --raw datasets/skyscapes_raw

skyscapes-prepare:
	$(PY) scripts/prepare_skyscapes.py prepare --raw datasets/skyscapes_raw \
		--out datasets/skyscapes --label-mode $(LABEL_MODE) \
		$(if $(filter rgb,$(LABEL_MODE)),--colormap configs/skyscapes_colormap.json,) \
		--tile 512 --keep-empty-frac 0.1
	$(PY) scripts/dataset_validator.py --root datasets/skyscapes --num-classes 13 --ignore-index 255

skyscapes-train:
	$(PY) -m uavroadmark.cli.train --config configs/experiment/skyscapes_unetpp_core.yaml

# --- research experiments (synthetic, GPU) ---
ablation:
	bash scripts/run_loss_ablation.sh
arch-sweep:
	bash scripts/run_arch_sweep.sh

train:
	$(PY) -m uavroadmark.cli.train --config $(CONFIG)

eval:
	$(PY) -m uavroadmark.cli.evaluate --config $(CONFIG) --checkpoint $(CKPT) --split test

viz:
	$(PY) scripts/visualize.py --config $(CONFIG) --checkpoint $(CKPT) -n 6

test:
	$(PY) -m pytest -q

lint:
	ruff check src tests scripts || true

clean:
	rm -rf outputs/ runs/ wandb/ .pytest_cache .ruff_cache
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
