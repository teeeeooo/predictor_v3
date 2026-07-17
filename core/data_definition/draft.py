"""In-memory Data Definition draft models for future edit/save slices."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from core.data_definition.derived_policy import load_current_derived_feature_policy
from core.data_definition.model import DerivedFeatureDefinition
from core.predictor_schema.catalog_v2 import (
    PredictSchemaV2Row,
    load_predict_schema_catalog_v2,
)

DataDefinitionSourceKind = Literal["schema_row", "derived_policy", "feature_projection"]


@dataclass(frozen=True)
class DataDefinitionDraftRow:
    """In-memory editable candidate row for a Data Definition surface."""

    source_kind: DataDefinitionSourceKind
    display_order: int = 0
    column_key: str = ""
    label: str = ""
    role: str = ""
    editor: str = ""
    data_type: str = ""
    visible: bool = False
    required: bool = False
    readonly: bool = False
    value_source: str = ""
    mapping_entity: str = ""
    mapping_attribute: str = ""
    trigger_column: str = ""
    rule_id: str = ""
    model_input_enabled: bool = False
    ml_name: str = ""
    one_hot_group: str = ""
    active: bool = True
    notes: str = ""

    @property
    def identity(self) -> tuple[str, str]:
        """Return a stable in-memory identity for diffing draft rows."""
        key = self.column_key or self.ml_name
        return (self.source_kind, key)


@dataclass(frozen=True)
class DataDefinitionDraftChange:
    """One field-level draft change compared with the baseline."""

    row_identity: tuple[str, str]
    field_name: str
    before: object
    after: object


@dataclass(frozen=True)
class DataDefinitionDraftIssue:
    """Draft-level issue before save planning."""

    severity: str
    code: str
    message: str
    row_identity: tuple[str, str] | None = None


@dataclass(frozen=True)
class DataDefinitionDraft:
    """In-memory Data Definition draft with immutable baseline rows."""

    rows: tuple[DataDefinitionDraftRow, ...]
    baseline_rows: tuple[DataDefinitionDraftRow, ...]
    issues: tuple[DataDefinitionDraftIssue, ...] = ()
    controlled_row_additions: frozenset[tuple[str, str]] = frozenset()
    controlled_addition_initial_rows: tuple[DataDefinitionDraftRow, ...] = ()
    base_generation_id: str = ""

    @property
    def is_changed(self) -> bool:
        """Return whether any draft row differs from the baseline."""
        return bool(self.changes())

    def changes(self) -> tuple[DataDefinitionDraftChange, ...]:
        """Return field-level changes from baseline to current rows."""
        baseline = {row.identity: row for row in self.baseline_rows}
        changes: list[DataDefinitionDraftChange] = []
        for row in self.rows:
            before = baseline.get(row.identity)
            if before is None:
                changes.append(
                    DataDefinitionDraftChange(row.identity, "__row__", None, row)
                )
                continue
            changes.extend(_row_changes(before, row))
        current = {row.identity for row in self.rows}
        for identity, row in baseline.items():
            if identity not in current:
                changes.append(DataDefinitionDraftChange(identity, "__row__", row, None))
        return tuple(changes)

    def attributed_changes(self) -> tuple[DataDefinitionDraftChange, ...]:
        """Include post-Add field changes without expanding the initial Add."""
        initial_rows = {
            row.identity: row for row in self.controlled_addition_initial_rows
        }
        current_rows = {row.identity: row for row in self.rows}
        changes: list[DataDefinitionDraftChange] = []
        for change in self.changes():
            changes.append(change)
            initial = initial_rows.get(change.row_identity)
            current = current_rows.get(change.row_identity)
            if (
                change.field_name == "__row__"
                and change.before is None
                and initial is not None
                and current is not None
            ):
                changes.extend(_row_changes(initial, current))
        return tuple(changes)

    def is_controlled_row_addition(self, identity: tuple[str, str]) -> bool:
        """Return whether a command owner authorized this new row."""
        return identity in self.controlled_row_additions

    def controlled_addition_initial_row(
        self,
        identity: tuple[str, str],
    ) -> DataDefinitionDraftRow | None:
        """Return the immutable row first produced by a controlled Add."""
        return next(
            (
                row
                for row in self.controlled_addition_initial_rows
                if row.identity == identity
            ),
            None,
        )


def build_data_definition_draft(
    schema_path: str | Path | None = None,
    derived_policy: tuple[DerivedFeatureDefinition, ...] | None = None,
) -> DataDefinitionDraft:
    """Build an in-memory draft from current schema rows and derived policy."""
    schema_rows = tuple(
        _schema_draft_row(row)
        for row in load_predict_schema_catalog_v2(schema_path).rows
    )
    derived_rows = tuple(
        _derived_draft_row(row)
        for row in (derived_policy or load_current_derived_feature_policy())
    )
    rows = (*schema_rows, *derived_rows)
    return DataDefinitionDraft(rows=rows, baseline_rows=rows)


def replace_draft_row(
    draft: DataDefinitionDraft,
    row_identity: tuple[str, str],
    **updates: object,
) -> DataDefinitionDraft:
    """Return a copy of the draft with one row replaced for tests/future UI."""
    rows = tuple(
        _replace_row(row, updates) if row.identity == row_identity else row
        for row in draft.rows
    )
    return DataDefinitionDraft(
        rows=rows,
        baseline_rows=draft.baseline_rows,
        issues=draft.issues,
        controlled_row_additions=draft.controlled_row_additions,
        controlled_addition_initial_rows=draft.controlled_addition_initial_rows,
        base_generation_id=draft.base_generation_id,
    )


def _schema_draft_row(row: PredictSchemaV2Row) -> DataDefinitionDraftRow:
    return DataDefinitionDraftRow(
        source_kind="schema_row",
        display_order=row.display_order,
        column_key=row.column_key,
        label=row.label,
        role=row.role,
        editor=row.editor,
        data_type=row.data_type,
        visible=row.visible,
        required=row.required,
        readonly=row.readonly,
        value_source=row.value_source,
        mapping_entity=row.mapping_entity,
        mapping_attribute=row.mapping_attribute,
        trigger_column=row.trigger_column,
        rule_id=row.rule_id,
        model_input_enabled=row.model_input_enabled,
        ml_name=row.ml_name,
        one_hot_group=row.one_hot_group,
        active=row.active,
        notes=row.notes,
    )


def _derived_draft_row(row: DerivedFeatureDefinition) -> DataDefinitionDraftRow:
    return DataDefinitionDraftRow(
        source_kind="derived_policy",
        role="derived",
        ml_name=row.ml_name,
        active=row.active,
        notes="Derived feature policy has no persistence owner in Arc 15C-1.",
    )


def _row_changes(
    before: DataDefinitionDraftRow,
    after: DataDefinitionDraftRow,
) -> tuple[DataDefinitionDraftChange, ...]:
    changes: list[DataDefinitionDraftChange] = []
    for field_name in DataDefinitionDraftRow.__dataclass_fields__:
        before_value = getattr(before, field_name)
        after_value = getattr(after, field_name)
        if before_value != after_value:
            changes.append(
                DataDefinitionDraftChange(
                    after.identity,
                    field_name,
                    before_value,
                    after_value,
                )
            )
    return tuple(changes)


def _replace_row(
    row: DataDefinitionDraftRow,
    updates: dict[str, object],
) -> DataDefinitionDraftRow:
    values = {
        field: getattr(row, field)
        for field in DataDefinitionDraftRow.__dataclass_fields__
    }
    values.update(updates)
    return DataDefinitionDraftRow(**values)
