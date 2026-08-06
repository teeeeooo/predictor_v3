"""Legacy-wide Data Mapping bootstrap preparation and stale-state guards."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from core.data_definition import MappingRequirement
from core.data_definition.mapping_requirement_contract import (
    MappingRequirementContractResolution,
    resolve_mapping_requirement_contracts,
)
from core.mapping.editor_model import MappingEditorDraft, MappingEditorValidationResult
from core.mapping.editor_projection import apply_effective_mapping_requirements_to_editor_draft
from core.mapping.entity_model import MappingValidationError


LegacyBootstrapParser = Callable[[str | Path], MappingEditorDraft]
RequirementLoader = Callable[[], tuple[MappingRequirement, ...]]
DraftValidator = Callable[
    [
        MappingEditorDraft,
        tuple[MappingRequirement, ...],
        MappingRequirementContractResolution,
    ],
    MappingEditorValidationResult,
]


@dataclass(frozen=True)
class DataMappingLegacyBootstrapPreview:
    """Prepared legacy-wide candidate plus the state it was reviewed against."""

    source_path: Path
    blockers: tuple[MappingValidationError, ...] = ()
    candidate: MappingEditorDraft | None = field(default=None, repr=False, compare=False)
    base_draft: MappingEditorDraft | None = field(default=None, repr=False, compare=False)
    base_revision: int = 0
    resource_revision: str = ""
    mapping_requirements: tuple[MappingRequirement, ...] = field(
        default=(), repr=False, compare=False
    )
    base_dirty: bool = False

    @property
    def can_apply(self) -> bool:
        return self.candidate is not None and not self.blockers

    @property
    def replacement_required(self) -> bool:
        # Applying bootstrap installs a new onboarding context and clears prior
        # command history, so any existing draft requires an explicit decision.
        return self.base_draft is not None


@dataclass(frozen=True)
class DataMappingLegacyBootstrapApplyResult:
    """Outcome of validating a prepared bootstrap for draft installation."""

    success: bool
    changed: bool = False
    stale: bool = False
    confirmation_required: bool = False
    message: str = ""


def prepare_legacy_bootstrap_preview(
    source: str | Path,
    *,
    parser: LegacyBootstrapParser | None,
    resource_status: str,
    resource_revision: str,
    base_draft: MappingEditorDraft | None,
    base_revision: int,
    base_dirty: bool,
    load_requirements: RequirementLoader,
    validate_draft: DraftValidator,
) -> DataMappingLegacyBootstrapPreview:
    """Prepare one strict bootstrap candidate without mutating Mapping state."""
    source_path = Path(source)
    common = dict(
        source_path=source_path,
        base_draft=base_draft,
        base_revision=base_revision,
        resource_revision=resource_revision,
        base_dirty=base_dirty,
    )
    if resource_status != "missing":
        return DataMappingLegacyBootstrapPreview(
            blockers=(_issue(
                "legacy_bootstrap_resource_exists",
                "Legacy bootstrap is available only while the runtime Mapping resource is missing.",
            ),),
            **common,
        )
    if parser is None:
        return DataMappingLegacyBootstrapPreview(
            blockers=(_issue(
                "legacy_bootstrap_unavailable",
                "No legacy Mapping bootstrap adapter is configured.",
            ),),
            **common,
        )
    try:
        requirements = load_requirements()
    except Exception as exc:
        return DataMappingLegacyBootstrapPreview(
            blockers=(_issue(
                "legacy_bootstrap_requirements_unavailable",
                f"Unable to load current Mapping Requirements: {_exception_summary(exc)}",
            ),),
            **common,
        )
    common["mapping_requirements"] = requirements
    try:
        parsed = parser(source_path)
    except Exception as exc:
        return DataMappingLegacyBootstrapPreview(
            blockers=(_legacy_exception_issue(exc),),
            **common,
        )
    resolution = resolve_mapping_requirement_contracts(requirements)
    candidate = apply_effective_mapping_requirements_to_editor_draft(
        parsed, resolution.contracts
    )
    validation = validate_draft(candidate, requirements, resolution)
    blockers = tuple(issue for issue in validation.issues if issue.severity == "error")
    return DataMappingLegacyBootstrapPreview(
        candidate=candidate if not blockers else None,
        blockers=blockers,
        **common,
    )


def evaluate_legacy_bootstrap_apply(
    preview: DataMappingLegacyBootstrapPreview,
    *,
    resource_status: str,
    resource_revision: str,
    current_draft: MappingEditorDraft | None,
    draft_revision: int,
    load_requirements: RequirementLoader,
    validate_draft: DraftValidator,
    allow_replace_current: bool,
) -> tuple[MappingEditorDraft | None, DataMappingLegacyBootstrapApplyResult]:
    """Recheck preview freshness and validity before the service mutates its session."""
    try:
        requirements = load_requirements()
    except Exception as exc:
        return None, DataMappingLegacyBootstrapApplyResult(
            success=False,
            stale=True,
            message=(
                "Legacy bootstrap is stale because current Mapping Requirements "
                f"could not be reloaded: {_exception_summary(exc)}"
            ),
        )
    stale = (
        resource_status != "missing"
        or resource_revision != preview.resource_revision
        or draft_revision != preview.base_revision
        or current_draft != preview.base_draft
        or requirements != preview.mapping_requirements
    )
    if stale:
        return None, DataMappingLegacyBootstrapApplyResult(
            success=False,
            stale=True,
            message=(
                "Legacy bootstrap is stale because the Mapping resource, draft, or "
                "Mapping Requirements changed. Review the current state and try again."
            ),
        )
    if not preview.can_apply or preview.candidate is None:
        return None, DataMappingLegacyBootstrapApplyResult(
            success=False,
            message="Legacy bootstrap is blocked; review the source issues first.",
        )
    if preview.replacement_required and not allow_replace_current:
        return None, DataMappingLegacyBootstrapApplyResult(
            success=False,
            confirmation_required=True,
            message="Replacing the current Data Mapping draft requires explicit confirmation.",
        )
    resolution = resolve_mapping_requirement_contracts(requirements)
    candidate = apply_effective_mapping_requirements_to_editor_draft(
        preview.candidate, resolution.contracts
    )
    blockers = tuple(
        issue
        for issue in validate_draft(candidate, requirements, resolution).issues
        if issue.severity == "error"
    )
    if blockers:
        return None, DataMappingLegacyBootstrapApplyResult(
            success=False,
            message=f"Legacy bootstrap candidate is invalid: {blockers[0].message}",
        )
    return candidate, DataMappingLegacyBootstrapApplyResult(
        success=True,
        changed=True,
        message=(
            "Legacy Mapping CSV loaded as an Unsaved draft. mapping.json has not been "
            "written; review the draft and use Save explicitly."
        ),
    )


def _issue(code: str, message: str) -> MappingValidationError:
    return MappingValidationError(
        code=code,
        message=message,
        entity_key="Legacy Bootstrap",
        field="source",
    )


def _legacy_exception_issue(exc: Exception) -> MappingValidationError:
    block = getattr(exc, "block", "") or "Legacy Bootstrap"
    field = getattr(exc, "field", "") or "source"
    key = getattr(exc, "key", "")
    return MappingValidationError(
        code="legacy_bootstrap_invalid_source",
        message=_exception_summary(exc),
        entity_key=block,
        attribute_key=field if field != "source" else "",
        row_key=key,
        field=field,
    )


def _exception_summary(exc: Exception) -> str:
    text = str(exc).strip()
    return text or type(exc).__name__
