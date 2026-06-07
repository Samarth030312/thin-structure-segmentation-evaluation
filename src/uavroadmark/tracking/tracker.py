"""Unified experiment tracking over TensorBoard, Weights & Biases, and a
always-on CSV/JSON backend.

The CSV backend guarantees that *every* run leaves a machine-readable trace even
when neither TensorBoard nor wandb is installed - critical for a benchmark whose
whole point is reproducible, comparable numbers.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, Optional

from ..utils.logging import get_logger

log = get_logger("tracking")


class ExperimentTracker:
    def __init__(self, out_dir: str | Path, run_name: str,
                 use_tensorboard: bool = True, use_wandb: bool = False,
                 wandb_project: str = "uav-roadmark-benchmark",
                 config: Optional[Dict[str, Any]] = None):
        self.out_dir = Path(out_dir)
        self.run_name = run_name
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self._csv_path = self.out_dir / "metrics.csv"
        self._csv_header_written = self._csv_path.exists()

        self.tb = None
        if use_tensorboard:
            try:
                from torch.utils.tensorboard import SummaryWriter
                self.tb = SummaryWriter(log_dir=str(self.out_dir / "tb"))
            except Exception as e:  # noqa: BLE001
                log.warning("TensorBoard unavailable (%s); using CSV only.", e)

        self.wandb = None
        if use_wandb:
            try:
                import wandb
                self.wandb = wandb
                wandb.init(project=wandb_project, name=run_name,
                           dir=str(self.out_dir), config=config or {})
            except Exception as e:  # noqa: BLE001
                log.warning("wandb unavailable (%s); skipping.", e)

        if config is not None:
            (self.out_dir / "config.json").write_text(json.dumps(config, indent=2))

    def log_scalars(self, metrics: Dict[str, float], step: int,
                    prefix: str = "") -> None:
        flat = {f"{prefix}{k}": float(v) for k, v in metrics.items()}
        if self.tb:
            for k, v in flat.items():
                self.tb.add_scalar(k, v, step)
        if self.wandb:
            self.wandb.log(flat, step=step)
        self._csv_append({"step": step, **flat})

    def log_figure(self, tag: str, fig, step: int) -> None:
        if self.tb:
            self.tb.add_figure(tag, fig, step)
        if self.wandb:
            self.wandb.log({tag: self.wandb.Image(fig)}, step=step)

    def _csv_append(self, row: Dict[str, Any]) -> None:
        # union-of-keys CSV: rewrite header if a new column appears.
        rows = []
        fieldnames = list(row.keys())
        if self._csv_path.exists():
            with open(self._csv_path, newline="") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                fieldnames = list(dict.fromkeys((reader.fieldnames or []) + fieldnames))
        rows.append(row)
        with open(self._csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    def close(self) -> None:
        if self.tb:
            self.tb.flush()
            self.tb.close()
        if self.wandb:
            self.wandb.finish()
