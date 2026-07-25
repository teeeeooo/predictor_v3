"""Shared Qt-free model lifecycle contracts and services."""

from .active_contracts import (
    ActiveModelReference,
    ActivationRecord,
    ModelResolution,
)
from .candidate_contracts import (
    CandidateArtifactReference,
    CandidateManifest,
    CandidateResult,
    TargetArtifactContract,
)
from .repository_contracts import CandidateSnapshot
from .durability_errors import (
    LifecycleDurabilityError,
    LifecycleRecoveryRequiredError,
)
from .paths import DEFAULT_WORKSPACE_ID, default_model_lifecycle_root
from .migration import LegacyMigrationResult, LegacyModelMigrationService
from .promotion import ModelPromotionService, PromotionResult
from .repository import ModelLifecycleRepository
from .resolver import ActiveModelResolver

__all__ = [
    "ActiveModelReference",
    "ActivationRecord",
    "ActiveModelResolver",
    "CandidateManifest",
    "CandidateArtifactReference",
    "CandidateResult",
    "CandidateSnapshot",
    "DEFAULT_WORKSPACE_ID",
    "ModelLifecycleRepository",
    "LegacyMigrationResult",
    "LegacyModelMigrationService",
    "LifecycleDurabilityError",
    "LifecycleRecoveryRequiredError",
    "ModelPromotionService",
    "ModelResolution",
    "PromotionResult",
    "TargetArtifactContract",
    "default_model_lifecycle_root",
]
