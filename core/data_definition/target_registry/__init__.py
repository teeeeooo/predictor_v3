"""Canonical Target policy and immutable Train registry projection."""

from core.data_definition.target_registry.runtime import (
    ModelRegistrySnapshot,
    OrderedTrainingInputPool,
    RuntimeModelGroup,
    RuntimeTarget,
    TrainingInputOwner,
    apply_ordered_target_policy,
    apply_target_policy,
    model_registry_snapshot,
    ordered_training_input_pool,
)

__all__ = [
    "ModelRegistrySnapshot", "OrderedTrainingInputPool", "RuntimeModelGroup", "RuntimeTarget",
    "TrainingInputOwner", "apply_ordered_target_policy", "apply_target_policy",
    "model_registry_snapshot",
    "ordered_training_input_pool",
]
