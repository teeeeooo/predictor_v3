"""Legacy registry facade generated from the canonical bootstrap snapshot.

Production Train composition injects a ``ModelRegistrySnapshot``.  These exports
remain for callers that have not yet crossed that application boundary.
"""

from __future__ import annotations

from core.data_definition.contract.bootstrap import bootstrap_manifest
from core.data_definition.target_registry.runtime import model_registry_snapshot


_COMPATIBILITY_SNAPSHOT = model_registry_snapshot(bootstrap_manifest())
MODEL_REGISTRY = _COMPATIBILITY_SNAPSHOT.compatibility_registry()


def get_model_config(model_key: str) -> dict[str, object]:
    if model_key not in MODEL_REGISTRY:
        raise KeyError(f"등록되지 않은 모델 키입니다: {model_key}")
    return MODEL_REGISTRY[model_key]


def compatibility_registry_snapshot():
    """Return the immutable source used to generate the compatibility facade."""
    return _COMPATIBILITY_SNAPSHOT
