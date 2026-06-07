"""Leaderboard: a single CSV that ranks every evaluated model.

The leaderboard is the user-facing artifact of the whole benchmark. It is
idempotent on ``(run_name, split)`` - re-evaluating a run updates its row rather
than appending duplicates - and always re-sorts by the primary metric.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import pandas as pd

PRIMARY_METRIC = "mIoU"
COLUMNS = ["run_name", "model", "loss", "split",
           # standard region metrics
           "mIoU", "mDice", "mF1", "mPrecision", "mRecall", "PixelAcc", "FWIoU",
           # thin-structure protocol (this work)
           "clDice", "BoundaryIoU", "clF1", "clRecall", "TolIoU",
           "params_M", "notes"]


def update_leaderboard(csv_path: str | Path, row: Dict) -> "pd.DataFrame":
    csv_path = Path(csv_path)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    if csv_path.exists():
        df = pd.read_csv(csv_path)
    else:
        df = pd.DataFrame(columns=COLUMNS)

    for c in COLUMNS:
        if c not in df.columns:
            df[c] = None
    key = (df["run_name"] == row.get("run_name")) & (df["split"] == row.get("split"))
    df = df[~key]  # drop existing row for this (run, split)
    new = pd.DataFrame([row])
    # avoid pandas' all-NA concat FutureWarning when the table is empty
    df = new if df.empty else pd.concat([df, new], ignore_index=True)
    df = df.sort_values(PRIMARY_METRIC, ascending=False).reset_index(drop=True)
    df = df[COLUMNS]
    df.to_csv(csv_path, index=False)
    return df


def render_markdown(csv_path: str | Path) -> str:
    df = pd.read_csv(csv_path)
    try:
        return df.to_markdown(index=False)
    except ImportError:
        # no `tabulate` -> build a GitHub-flavoured markdown table by hand
        cols = list(df.columns)
        header = "| " + " | ".join(map(str, cols)) + " |"
        sep = "| " + " | ".join("---" for _ in cols) + " |"
        rows = ["| " + " | ".join("" if pd.isna(v) else str(v) for v in r) + " |"
                for r in df.itertuples(index=False, name=None)]
        return "\n".join([header, sep, *rows])


def make_row(run_name: str, model: str, loss: str, split: str,
             headline: Dict[str, float], params_m: float = None,
             notes: str = "") -> Dict:
    return {
        "run_name": run_name, "model": model, "loss": loss, "split": split,
        **headline, "params_M": round(params_m, 2) if params_m else None,
        "notes": notes,
    }


def count_params_millions(model) -> float:
    return sum(p.numel() for p in model.parameters()) / 1e6
