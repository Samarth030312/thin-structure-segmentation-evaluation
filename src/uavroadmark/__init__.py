"""uavroadmark: an evaluation framework for road-marking segmentation from UAV imagery.

The package is intentionally layered so that the *numeric* core (metrics, losses,
config, synthetic data) has **no hard dependency on torch**. This lets the
validation, exploration, and metric-unit-test paths run in any environment,
while the heavy training/model code is imported lazily only when needed.
"""

__version__ = "0.1.0"

__all__ = ["__version__"]
