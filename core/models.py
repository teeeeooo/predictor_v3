"""Compatibility wrapper for ML model registry.

Actual implementation lives in `core.ml.registry`.
"""

from core.ml.registry import MODEL_REGISTRY, get_model_config

__all__ = [
    "MODEL_REGISTRY",
    "get_model_config",
]
