"""Canonical Target policy and immutable Train registry projection."""

from core.data_definition.target_registry.runtime import (
    ModelRegistrySnapshot,
    RuntimeModelGroup,
    RuntimeTarget,
    apply_target_policy,
    model_registry_snapshot,
)

__all__ = [
    "ModelRegistrySnapshot", "RuntimeModelGroup", "RuntimeTarget",
    "apply_target_policy", "model_registry_snapshot",
]
