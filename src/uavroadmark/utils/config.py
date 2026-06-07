"""YAML configuration loading with composition and dotted-key overrides.

Design goals:
* **Declarative experiments** - an experiment is a YAML file, not Python.
* **Composition** - an experiment can ``_base_`` other YAML files (dataset,
  model, loss, train) so we never copy-paste hyper-parameters.
* **CLI overrides** - ``key.subkey=value`` strings let us sweep without editing
  files (e.g. ``train.lr=3e-4``).
"""
from __future__ import annotations

import ast
import copy
from pathlib import Path
from typing import Any, Dict, List

import yaml


class Config(dict):
    """A dict with attribute access and dotted get/set helpers.

    NOTE: ``__getattr__`` must raise ``AttributeError`` (not return ``None``) on
    a missing key, otherwise ``copy.deepcopy`` / pickling break - they probe for
    dunder hooks like ``__deepcopy__`` via ``getattr`` and a ``None`` answer is
    interpreted as "this object is uncopyable".
    """

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as e:
            raise AttributeError(name) from e

    def __setattr__(self, key, value):
        self[key] = value

    def get_dotted(self, dotted: str, default=None):
        node: Any = self
        for part in dotted.split("."):
            if not isinstance(node, dict) or part not in node:
                return default
            node = node[part]
        return node

    def set_dotted(self, dotted: str, value: Any):
        parts = dotted.split(".")
        node = self
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = value


def _to_config(obj: Any) -> Any:
    if isinstance(obj, dict):
        return Config({k: _to_config(v) for k, v in obj.items()})
    if isinstance(obj, list):
        return [_to_config(v) for v in obj]
    return obj


def merge_configs(base: Dict, override: Dict) -> Config:
    """Deep-merge ``override`` onto ``base`` (override wins on leaf conflicts)."""
    out = copy.deepcopy(dict(base))
    for k, v in override.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = merge_configs(out[k], v)
        else:
            out[k] = copy.deepcopy(v)
    return _to_config(out)


def _coerce(value: str) -> Any:
    """Turn a CLI string into a python scalar where possible (3e-4 -> float).

    Handles YAML-style lowercase booleans/null (``true``/``false``/``none``/
    ``null``) which ``ast.literal_eval`` rejects - a common foot-gun for CLI
    overrides like ``train.amp=false``.
    """
    low = value.strip().lower()
    if low in ("true", "false"):
        return low == "true"
    if low in ("none", "null", "~"):
        return None
    try:
        return ast.literal_eval(value)
    except (ValueError, SyntaxError):
        return value


def load_config(path: str | Path, overrides: List[str] | None = None) -> Config:
    """Load a YAML config, resolving ``_base_`` includes and applying overrides.

    ``_base_`` may be a single path or a list of paths, resolved relative to the
    including file. Later bases override earlier ones; the including file wins
    over all of its bases.
    """
    path = Path(path)
    with open(path, "r") as f:
        raw = yaml.safe_load(f) or {}

    bases = raw.pop("_base_", [])
    if isinstance(bases, str):
        bases = [bases]

    merged: Config = Config()
    for b in bases:
        merged = merge_configs(merged, load_config(path.parent / b))
    merged = merge_configs(merged, raw)

    for ov in overrides or []:
        if "=" not in ov:
            raise ValueError(f"Override must be key=value, got: {ov!r}")
        key, value = ov.split("=", 1)
        merged.set_dotted(key.strip(), _coerce(value.strip()))

    return merged
