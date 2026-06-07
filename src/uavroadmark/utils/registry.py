"""A tiny string->callable registry used by the model and loss zoos.

A registry decouples *naming* from *construction*. Calling code asks for a model
by string (e.g. ``get_model("deeplabv3plus")``) which keeps experiment configs
declarative (YAML) and avoids scattering ``if name == ...`` branches.
"""
from __future__ import annotations

from typing import Callable, Dict, Iterable


class Registry:
    """Maps a canonical lowercase name to a factory callable."""

    def __init__(self, kind: str):
        self.kind = kind
        self._table: Dict[str, Callable] = {}

    def register(self, *names: str) -> Callable:
        """Decorator: register a factory under one or more aliases."""

        def _wrap(fn: Callable) -> Callable:
            for n in names:
                key = n.lower().strip()
                if key in self._table:
                    raise KeyError(f"{self.kind} '{key}' already registered")
                self._table[key] = fn
            return fn

        return _wrap

    def get(self, name: str, **kwargs):
        key = name.lower().strip()
        if key not in self._table:
            raise KeyError(
                f"Unknown {self.kind} '{name}'. Available: {sorted(self._table)}"
            )
        return self._table[key](**kwargs)

    def available(self) -> Iterable[str]:
        return sorted(self._table)

    def __contains__(self, name: str) -> bool:
        return name.lower().strip() in self._table
