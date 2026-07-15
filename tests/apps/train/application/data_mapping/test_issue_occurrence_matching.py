"""Exact validation-to-coverage matching for duplicate mapping row keys."""

from __future__ import annotations

from apps.train.application.data_mapping import row_index_for_identity
from apps.train.controllers.data_mapping.presentation import project_snapshot
from apps.train.services.data_mapping_types import DataMappingSnapshot
from core.data_definition import MappingRequirement
from core.mapping.editor_commands import duplicate_draft_row, set_draft_cell
from core.mapping.editor_model import MappingEditorValidationResult
from core.mapping.editor_projection import (
    apply_mapping_requirements_to_editor_draft,
    project_runtime_mapping_to_editor_draft,
)
from core.mapping.editor_validation import validate_mapping_editor_draft
from core.mapping.entity_model import MappingValidationError


def test_duplicate_key_second_occurrence_invalid_matches_only_exact_cell():
    requirement = _requirement("fan_diameter", "Fan Diameter")
    draft = _duplicate_draft((requirement,), first={"Fan Diameter": 2.5})
    draft = set_draft_cell(draft, "idu", 1, "Fan Diameter", "bad")

    state = _state(draft, (requirement,))
    coverage = state.coverage_items[0]
    invalid_index = next(
        index
        for index, issue in enumerate(state.validation_rows)
        if issue.code == "invalid_number"
    )
    issue_target = state.issue_targets[invalid_index]

    assert any(issue.code == "duplicate_key" for issue in state.validation_rows)
    assert (coverage.ready_rows, coverage.missing_rows, coverage.invalid_rows) == (1, 0, 1)
    assert (coverage.first_unresolved.row_key, coverage.first_unresolved.row_occurrence) == (
        "IDU-A",
        1,
    )
    assert (
        issue_target.group_key,
        issue_target.row_key,
        issue_target.row_occurrence,
        issue_target.attribute_key,
        issue_target.row_index,
    ) == ("idu", "IDU-A", 1, "Fan Diameter", 1)


def test_duplicate_key_first_occurrence_invalid_and_other_attribute_stays_ready():
    requirements = (
        _requirement("attribute_a", "Attribute A"),
        _requirement("attribute_b", "Attribute B"),
    )
    draft = _duplicate_draft(
        requirements,
        first={"Attribute A": "bad", "Attribute B": 2.5},
    )
    draft = set_draft_cell(draft, "idu", 1, "Attribute A", 3.5)

    state = _state(draft, requirements)
    attribute_a, attribute_b = state.coverage_items

    assert (attribute_a.ready_rows, attribute_a.invalid_rows) == (1, 1)
    assert attribute_a.first_unresolved.row_occurrence == 0
    assert (attribute_b.ready_rows, attribute_b.invalid_rows) == (2, 0)
    assert attribute_b.first_unresolved is None


def test_valid_row_index_is_authoritative_over_conflicting_key_occurrence():
    requirement = _requirement("fan_diameter", "Fan Diameter")
    draft = _duplicate_draft((requirement,), first={"Fan Diameter": 2.5})
    issue = MappingValidationError(
        code="synthetic_cell_invalid",
        message="Second occurrence is invalid.",
        entity_key="idu",
        attribute_key="Fan Diameter",
        row_key="IDU-A",
        field="Fan Diameter",
        row_index=1,
        row_occurrence=0,
    )

    state = _state(draft, (requirement,), issues=(issue,))
    target = state.issue_targets[0]
    coverage = state.coverage_items[0]

    assert (target.row_index, target.row_occurrence) == (1, 1)
    assert (coverage.ready_rows, coverage.invalid_rows) == (1, 1)
    assert coverage.first_unresolved.row_occurrence == 1


def test_indexless_stable_occurrence_is_exact_and_ambiguous_key_is_unscoped():
    requirement = _requirement("fan_diameter", "Fan Diameter")
    draft = _duplicate_draft((requirement,), first={"Fan Diameter": 2.5})
    exact_issue = MappingValidationError(
        code="synthetic_cell_invalid",
        message="Second occurrence is invalid.",
        entity_key="idu",
        attribute_key="Fan Diameter",
        row_key="IDU-A",
        field="Fan Diameter",
        row_occurrence=1,
    )
    ambiguous_issue = MappingValidationError(
        code="synthetic_cell_invalid",
        message="Occurrence is unavailable.",
        entity_key="idu",
        attribute_key="Fan Diameter",
        row_key="IDU-A",
        field="Fan Diameter",
    )

    exact = _state(draft, (requirement,), issues=(exact_issue,))
    ambiguous = _state(draft, (requirement,), issues=(ambiguous_issue,))

    assert (exact.issue_targets[0].row_index, exact.issue_targets[0].row_occurrence) == (1, 1)
    assert (exact.coverage_items[0].ready_rows, exact.coverage_items[0].invalid_rows) == (1, 1)
    assert ambiguous.issue_targets[0].row_index is None
    assert ambiguous.issue_targets[0].row_occurrence is None
    assert (ambiguous.coverage_items[0].ready_rows, ambiguous.coverage_items[0].invalid_rows) == (
        2,
        0,
    )


def test_stable_occurrence_re_resolves_after_index_shift_and_fails_when_removed():
    assert row_index_for_identity(("OTHER", "IDU-A", "IDU-A"), "IDU-A", 1) == 2
    assert row_index_for_identity(("IDU-A",), "IDU-A", 1) is None


def _state(draft, requirements, *, issues=None):  # noqa: ANN001, ANN201
    validation = (
        MappingEditorValidationResult(tuple(issues))
        if issues is not None
        else validate_mapping_editor_draft(draft)
    )
    snapshot = DataMappingSnapshot(
        draft=draft,
        validation_errors=validation.issues,
        validation_result=validation,
        source_label="synthetic duplicate rows",
        actions=(),
        mapping_requirements=tuple(requirements),
    )
    return project_snapshot(snapshot, "idu", resource_status="available")


def _duplicate_draft(requirements, *, first):  # noqa: ANN001, ANN201
    draft = apply_mapping_requirements_to_editor_draft(
        project_runtime_mapping_to_editor_draft(
            {
                "idu": {"IDU-A": {"ID Volume": 1.25, **first}},
                "ref_type": {"R32": {}},
                "exp_type": {"EEV": {}},
            }
        ),
        tuple(requirements),
    )
    return duplicate_draft_row(draft, "idu", 0)


def _requirement(column_key, attribute):  # noqa: ANN001, ANN201
    return MappingRequirement(
        column_key=column_key,
        ml_name="",
        mapping_entity="idu",
        mapping_attribute=attribute,
        trigger_column="idu",
        data_type="number",
        required=False,
    )
