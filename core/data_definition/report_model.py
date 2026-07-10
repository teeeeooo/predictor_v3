"""Report and issue models for Arc 15A Data Definition validation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from core.data_definition.model import (
    MappingRequirement,
    OneHotRelationship,
    ProjectedFeatureRow,
)

IssueSeverity = Literal["error", "warning", "info"]
ReadinessStatus = Literal["ok", "missing", "unavailable", "not_evaluated"]


@dataclass(frozen=True)
class DataDefinitionIssue:
    """Structured validation issue emitted by the cross-contract validator."""

    severity: IssueSeverity
    code: str
    message: str
    subject: str = ""


@dataclass(frozen=True)
class ReadinessCheck:
    """Passive readiness slot for future training/model validation."""

    name: str
    status: ReadinessStatus
    message: str


@dataclass(frozen=True)
class DataDefinitionReport:
    """Read-only Arc 15A projection and validation report."""

    projected_features: tuple[ProjectedFeatureRow, ...]
    catalog_features: tuple[ProjectedFeatureRow, ...]
    parity_issues: tuple[DataDefinitionIssue, ...] = ()
    mapping_requirements: tuple[MappingRequirement, ...] = ()
    one_hot_relationships: tuple[OneHotRelationship, ...] = ()
    readiness: tuple[ReadinessCheck, ...] = ()
    issues: tuple[DataDefinitionIssue, ...] = field(default_factory=tuple)

    @property
    def ok(self) -> bool:
        """Return whether the report has no error-level issues."""
        return not any(issue.severity == "error" for issue in self.issues)
