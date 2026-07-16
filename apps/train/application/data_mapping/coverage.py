"""Qt-free definition-backed Data Mapping coverage projection."""

from __future__ import annotations

from collections.abc import Sequence

from apps.train.application.data_mapping.contracts import (
    DataMappingCellTarget,
    DataMappingCoverageItem,
    DataMappingIssueTarget,
)
from core.data_definition.mapping_requirement_contract import (
    EffectiveMappingRequirement,
    resolve_mapping_requirement_contracts,
)
from core.mapping.editor_model import MappingEditorDraft, MappingEditorGroup
from core.mapping.entity_model import MappingValidationError
from core.mapping.value_policy import is_valid_mapping_boolean, is_valid_mapping_number


def project_mapping_coverage(
    requirements: tuple[EffectiveMappingRequirement, ...] | tuple[object, ...],
    draft: MappingEditorDraft,
    issues: Sequence[MappingValidationError] = (),
    issue_targets: Sequence[DataMappingIssueTarget | None] = (),
) -> tuple[DataMappingCoverageItem, ...]:
    """Project canonical requirement order over the current mapping draft."""
    effective = (
        requirements
        if all(isinstance(item, EffectiveMappingRequirement) for item in requirements)
        else resolve_mapping_requirement_contracts(requirements).contracts
    )
    blocking_targets = _blocking_targets(issues, issue_targets)
    return tuple(
        _coverage_item(requirement, draft, blocking_targets)
        for requirement in effective
    )


def _coverage_item(
    requirement: EffectiveMappingRequirement,
    draft: MappingEditorDraft,
    blocking_targets: frozenset[tuple[str, str, str, int | None, int | None]],
) -> DataMappingCoverageItem:
    group_key = requirement.resolved_group_key
    group = draft.group(group_key)
    if group is None:
        return _unavailable_item(requirement, group_key, "group_unavailable")
    if requirement.mapping_attribute not in group.columns:
        return _unavailable_item(requirement, group_key, "attribute_unavailable")
    if not group.rows:
        return DataMappingCoverageItem(
            definition_column_key=requirement.column_key,
            mapping_group_key=group_key,
            mapping_entity=requirement.mapping_entity,
            mapping_attribute=requirement.mapping_attribute,
            required=requirement.required,
            data_type=requirement.data_type,
            total_rows=0,
            ready_rows=0,
            missing_rows=0,
            invalid_rows=0,
            unresolved_targets=(),
            status="no_rows",
            summary="No applicable mapping rows.",
            source_definition_column_keys=requirement.definition_column_keys,
        )

    missing = 0
    invalid = 0
    unresolved: list[DataMappingCellTarget] = []
    row_key_occurrences: dict[str, int] = {}
    for row_index, row in enumerate(group.rows):
        value = row.value_for(requirement.mapping_attribute)
        occurrence = row_key_occurrences.get(row.source_key, 0)
        row_key_occurrences[row.source_key] = occurrence + 1
        target = DataMappingCellTarget(
            group_key,
            row.source_key,
            requirement.mapping_attribute,
            occurrence,
            row_index,
        )
        if _is_blank(value):
            missing += 1
            unresolved.append(target)
            continue
        if not _value_is_valid(value, requirement.data_type) or _has_blocking_issue(
            blocking_targets,
            group,
            target,
            row_index,
        ):
            invalid += 1
            unresolved.append(target)

    total = len(group.rows)
    ready = total - missing - invalid
    status = "ready" if not missing and not invalid else "incomplete"
    return DataMappingCoverageItem(
        definition_column_key=requirement.column_key,
        mapping_group_key=group_key,
        mapping_entity=requirement.mapping_entity,
        mapping_attribute=requirement.mapping_attribute,
        required=requirement.required,
        data_type=requirement.data_type,
        total_rows=total,
        ready_rows=ready,
        missing_rows=missing,
        invalid_rows=invalid,
        unresolved_targets=tuple(unresolved),
        status=status,
        summary=_summary(requirement.required, total, ready, missing, invalid),
        source_definition_column_keys=requirement.definition_column_keys,
    )


def _unavailable_item(
    requirement: EffectiveMappingRequirement,
    group_key: str,
    status: str,
) -> DataMappingCoverageItem:
    subject = "Mapping group" if status == "group_unavailable" else "Mapping attribute"
    return DataMappingCoverageItem(
        definition_column_key=requirement.column_key,
        mapping_group_key=group_key,
        mapping_entity=requirement.mapping_entity,
        mapping_attribute=requirement.mapping_attribute,
        required=requirement.required,
        data_type=requirement.data_type,
        total_rows=0,
        ready_rows=0,
        missing_rows=0,
        invalid_rows=0,
        unresolved_targets=(),
        status=status,
        summary=f"{subject} unavailable.",
        source_definition_column_keys=requirement.definition_column_keys,
    )


def _blocking_targets(
    issues: Sequence[MappingValidationError],
    targets: Sequence[DataMappingIssueTarget | None],
) -> frozenset[tuple[str, str, str, int | None, int | None]]:
    return frozenset(
        (
            target.group_key,
            target.row_key,
            target.attribute_key,
            target.row_occurrence,
            target.row_index,
        )
        for issue, target in zip(issues, targets)
        if issue.severity == "error"
        and target is not None
        and (target.row_index is not None or target.row_occurrence is not None)
    )


def _has_blocking_issue(
    targets: frozenset[tuple[str, str, str, int | None, int | None]],
    group: MappingEditorGroup,
    target: DataMappingCellTarget,
    row_index: int,
) -> bool:
    return any(
        group_key == group.group_key
        and attribute == target.attribute_key
        and (
            issue_row == row_index
            if issue_row is not None
            else row_key == target.row_key and occurrence == target.row_occurrence
        )
        for group_key, row_key, attribute, occurrence, issue_row in targets
    )


def _is_blank(value: object) -> bool:
    return value is None or not str(value).strip()


def _value_is_valid(value: object, data_type: str) -> bool:
    if data_type == "number":
        return is_valid_mapping_number(value)
    if data_type == "boolean":
        return is_valid_mapping_boolean(value)
    return True


def _summary(required: bool, total: int, ready: int, missing: int, invalid: int) -> str:
    if not missing and not invalid:
        return f"{ready} / {total} ready. Coverage ready."
    if required:
        return f"{ready} / {total} ready. {missing} missing, {invalid} invalid."
    return (
        f"Optional — {ready} of {total} populated. {missing} missing, {invalid} invalid. "
        "Save not blocked by missing optional values."
    )
