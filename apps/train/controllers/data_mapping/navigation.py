"""Qt-free public Mapping Requirement navigation orchestration."""

from __future__ import annotations

from collections.abc import Callable

from apps.train.application.data_mapping import (
    DataMappingCellTarget,
    DataMappingNavigationRequest,
    DataMappingNavigationResult,
)
from apps.train.controllers.data_mapping.presentation import (
    DataMappingControllerState,
    display_source_label,
    error_state,
    exception_summary,
    missing_state,
    project_snapshot,
)
from apps.train.services.data_mapping_service import DataMappingService
from apps.train.services.data_mapping_types import DataMappingSnapshot
from core.mapping.editor_projection import mapping_group_key_for_requirement


def open_mapping_requirement(
    service: DataMappingService,
    request: DataMappingNavigationRequest,
    current_group_key: str,
    refresh: Callable[[str], DataMappingControllerState],
) -> tuple[DataMappingControllerState, DataMappingNavigationResult]:
    """Refresh saved requirements without reloading or saving mapping data."""
    if not request.saved:
        return refresh(current_group_key), _result(
            request,
            "requirement_not_saved",
            "Save schema before opening this Mapping Requirement.",
        )
    resource_status = service.resource_status()
    if resource_status == "missing":
        snapshot = _safe_current_snapshot(service)
        state = (
            _state(service, snapshot, current_group_key, resource_status="missing")
            if snapshot is not None
            else missing_state(
                source_label=display_source_label(service.source_label),
                bootstrap_enabled=service.legacy_bootstrap_available,
            )
        )
        return state, _result(
            request,
            "mapping_source_unavailable",
            "Mapping source unavailable; current draft was preserved.",
        )
    try:
        snapshot = service.load_snapshot()
    except Exception as exc:
        summary = exception_summary(exc)
        return error_state(
            "Unable to refresh mapping requirements.",
            source_label=display_source_label(service.source_label),
            detail_message=summary,
        ), _result(request, "load_failed", f"Data Mapping refresh failed: {summary}")

    requirement = next(
        (
            item
            for item in snapshot.mapping_requirements
            if item.column_key == request.definition_column_key
        ),
        None,
    )
    if requirement is None:
        return _state(service, snapshot, current_group_key), _result(
            request,
            "requirement_not_saved",
            "The requested Mapping Requirement is not in the latest saved schema.",
        )
    resolved_group = mapping_group_key_for_requirement(requirement)
    if (
        requirement.mapping_entity != request.mapping_entity
        or resolved_group != request.resolved_group_key
    ):
        return _state(service, snapshot, current_group_key), _result(
            request,
            "requested_group_unavailable",
            "The saved Mapping Requirement no longer resolves to the requested group.",
        )
    group = snapshot.draft.group(resolved_group)
    if group is None:
        return _state(service, snapshot, current_group_key), _result(
            request,
            "requested_group_unavailable",
            f"Data Mapping group '{resolved_group}' is unavailable.",
        )
    if (
        requirement.mapping_attribute != request.mapping_attribute
        or request.mapping_attribute not in group.columns
    ):
        return _state(service, snapshot, current_group_key), _result(
            request,
            "requested_attribute_unavailable",
            f"Mapping attribute '{request.mapping_attribute}' is unavailable.",
        )

    state = _state(service, snapshot, resolved_group)
    coverage = next(
        (
            item
            for item in state.coverage_items
            if request.definition_column_key
            in (
                item.source_definition_column_keys
                or (item.definition_column_key,)
            )
            and item.mapping_group_key == resolved_group
            and item.mapping_attribute == request.mapping_attribute
        ),
        None,
    )
    if coverage is None:
        return state, _result(
            request,
            "requested_attribute_unavailable",
            f"Coverage for '{request.mapping_attribute}' is unavailable.",
        )
    target = coverage.first_unresolved if request.prefer_unresolved else None
    if request.unresolved_row_key:
        target = next(
            (
                item
                for item in coverage.unresolved_targets
                if item.row_key == request.unresolved_row_key
                and item.row_occurrence == request.unresolved_row_occurrence
            ),
            None,
        )
        if target is None:
            return state, _result(
                request,
                "unresolved_row_unavailable",
                "The requested unresolved row is no longer available.",
            )
    if target is not None:
        return state, _result(
            request,
            "opened_unresolved",
            f"Opened {request.mapping_attribute} at an unresolved value.",
            target=target,
        )
    if coverage.status == "ready":
        return state, _result(
            request,
            "coverage_ready",
            f"Opened {request.mapping_attribute}. Coverage ready.",
        )
    return state, _result(
        request,
        "opened",
        f"Opened {request.mapping_attribute}. {coverage.summary}",
    )


def _state(
    service: DataMappingService,
    snapshot: DataMappingSnapshot,
    selected_group_key: str,
    *,
    resource_status: str | None = None,
) -> DataMappingControllerState:
    return project_snapshot(
        snapshot,
        selected_group_key,
        resource_status=resource_status or service.resource_status(),
    )


def _result(
    request: DataMappingNavigationRequest,
    status: str,
    message: str,
    *,
    target: DataMappingCellTarget | None = None,
) -> DataMappingNavigationResult:
    return DataMappingNavigationResult(status, message, request, target)


def _safe_current_snapshot(service: DataMappingService) -> DataMappingSnapshot | None:
    try:
        return service.current_snapshot()
    except Exception:
        return None
