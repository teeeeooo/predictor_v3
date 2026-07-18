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
DataDefinitionRowIdentity = tuple[str, str]


@dataclass(frozen=True)
class DataDefinitionDraftRow:
    """In-memory editable candidate row for a Data Definition surface."""

    source_kind: DataDefinitionSourceKind
    stable_identity: str = ""
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
    operation: str = ""
    numerator_identity: str = ""
    denominator_identity: str = ""
    zero_denominator_policy: str = ""
    zero_value: float = 0.0
    active: bool = True
    notes: str = ""

    @property
    def identity(self) -> DataDefinitionRowIdentity:
        """Return a stable in-memory identity for diffing draft rows."""
        key = self.stable_identity or self.column_key or self.ml_name
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
    controlled_row_removals: frozenset[tuple[str, str]] = frozenset()
    controlled_field_changes: frozenset[tuple[tuple[str, str], str]] = frozenset()
    controlled_addition_initial_rows: tuple[DataDefinitionDraftRow, ...] = ()
    base_generation_id: str = ""
    base_manifest: object | None = None
    predict_order: tuple[DataDefinitionRowIdentity, ...] = ()
    baseline_predict_order: tuple[DataDefinitionRowIdentity, ...] = ()
    ml_order: tuple[DataDefinitionRowIdentity, ...] = ()
    baseline_ml_order: tuple[DataDefinitionRowIdentity, ...] = ()
    one_hot_groups: tuple[object, ...] = ()
    baseline_one_hot_groups: tuple[object, ...] = ()

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
        if self.predict_order != self.baseline_predict_order:
            changes.append(DataDefinitionDraftChange(
                ("ordering", "predict"), "__order__",
                self.baseline_predict_order, self.predict_order,
            ))
        if self.ml_order != self.baseline_ml_order:
            changes.append(DataDefinitionDraftChange(
                ("ordering", "ml"), "__order__",
                self.baseline_ml_order, self.ml_order,
            ))
        if self.one_hot_groups != self.baseline_one_hot_groups:
            changes.append(DataDefinitionDraftChange(
                ("one_hot", "groups"), "__one_hot__", self.baseline_one_hot_groups,
                self.one_hot_groups))
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
        return self.resolve_identity(identity) in self.controlled_row_additions

    def is_controlled_row_removal(self, identity: tuple[str, str]) -> bool:
        """Return whether a command owner authorized this baseline removal."""
        return self.resolve_identity(identity) in self.controlled_row_removals

    def is_controlled_field_change(
        self,
        identity: tuple[str, str],
        field_name: str,
    ) -> bool:
        """Return whether a dedicated command authorized a restricted change."""
        return (self.resolve_identity(identity), field_name) in self.controlled_field_changes

    def resolve_identity(
        self,
        identity: DataDefinitionRowIdentity,
    ) -> DataDefinitionRowIdentity:
        """Resolve a legacy alias only at the compatibility boundary."""
        if any(row.identity == identity for row in (*self.rows, *self.baseline_rows)):
            return identity
        source_kind, alias = identity
        row = next(
            (
                item
                for item in (*self.rows, *self.baseline_rows)
                if item.source_kind == source_kind
                and alias in {item.column_key, item.ml_name}
            ),
            None,
        )
        return row.identity if row is not None else identity

    def controlled_addition_initial_row(
        self,
        identity: tuple[str, str],
    ) -> DataDefinitionDraftRow | None:
        """Return the immutable row first produced by a controlled Add."""
        resolved = self.resolve_identity(identity)
        return next(
            (
                row
                for row in self.controlled_addition_initial_rows
                if row.identity == resolved
            ),
            None,
        )


def build_data_definition_draft(
    schema_path: str | Path | None = None,
    derived_policy: tuple[DerivedFeatureDefinition, ...] | None = None,
    *,
    manifest: object | None = None,
) -> DataDefinitionDraft:
    """Build an in-memory draft from current schema rows and derived policy."""
    feature_ids = {
        item.column_key: item.identity
        for item in getattr(manifest, "features", ())
    }
    derived_ids = {
        item.ml_name: item.identity
        for item in getattr(manifest, "derived", ())
    }
    schema_rows = tuple(
        _schema_draft_row(row, stable_identity=feature_ids.get(row.column_key, ""))
        for row in load_predict_schema_catalog_v2(schema_path).rows
    )
    if manifest is not None:
        from core.data_definition.contract.compatibility import current_derived_definitions

        canonical_derived = current_derived_definitions(manifest)
    else:
        canonical_derived = ()
    derived_rows = tuple(
        _derived_draft_row(row, stable_identity=derived_ids.get(row.ml_name, ""))
        for row in (
            canonical_derived
            or derived_policy
            or load_current_derived_feature_policy()
        )
    )
    rows = (*schema_rows, *derived_rows)
    by_stable_id = {row.stable_identity: row.identity for row in rows if row.stable_identity}
    predict_order = tuple(
        by_stable_id[identity]
        for identity in getattr(getattr(manifest, "ordering", None), "predict", ())
        if identity in by_stable_id
    ) or tuple(row.identity for row in schema_rows)
    ml_order = tuple(
        by_stable_id[identity]
        for identity in getattr(getattr(manifest, "ordering", None), "ml", ())
        if identity in by_stable_id
    ) or _legacy_ml_order(rows)
    from core.data_definition.contract.compatibility import current_one_hot_definitions
    one_hot_groups = current_one_hot_definitions(manifest) if manifest is not None else ()
    return DataDefinitionDraft(
        rows=rows,
        baseline_rows=rows,
        base_manifest=manifest,
        predict_order=predict_order,
        baseline_predict_order=predict_order,
        ml_order=ml_order,
        baseline_ml_order=ml_order,
        one_hot_groups=one_hot_groups,
        baseline_one_hot_groups=one_hot_groups,
    )


def replace_draft_row(
    draft: DataDefinitionDraft,
    row_identity: tuple[str, str],
    **updates: object,
) -> DataDefinitionDraft:
    """Return a copy of the draft with one row replaced for tests/future UI."""
    resolved = draft.resolve_identity(row_identity)
    rows = tuple(
        _replace_row(row, updates) if row.identity == resolved else row
        for row in draft.rows
    )
    return DataDefinitionDraft(
        rows=rows,
        baseline_rows=draft.baseline_rows,
        issues=draft.issues,
        controlled_row_additions=draft.controlled_row_additions,
        controlled_row_removals=draft.controlled_row_removals,
        controlled_field_changes=draft.controlled_field_changes,
        controlled_addition_initial_rows=draft.controlled_addition_initial_rows,
        base_generation_id=draft.base_generation_id,
        base_manifest=draft.base_manifest,
        predict_order=draft.predict_order,
        baseline_predict_order=draft.baseline_predict_order,
        ml_order=draft.ml_order,
        baseline_ml_order=draft.baseline_ml_order,
        one_hot_groups=draft.one_hot_groups,
        baseline_one_hot_groups=draft.baseline_one_hot_groups,
    )


def _schema_draft_row(
    row: PredictSchemaV2Row,
    *,
    stable_identity: str = "",
) -> DataDefinitionDraftRow:
    return DataDefinitionDraftRow(
        source_kind="schema_row",
        stable_identity=stable_identity,
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


def _derived_draft_row(
    row: object,
    *,
    stable_identity: str = "",
) -> DataDefinitionDraftRow:
    return DataDefinitionDraftRow(
        source_kind="derived_policy",
        stable_identity=stable_identity,
        role="derived",
        data_type="number",
        ml_name=row.ml_name,
        operation=getattr(row, "operation", "safe_ratio"),
        numerator_identity=getattr(row, "numerator_identity", ""),
        denominator_identity=getattr(row, "denominator_identity", ""),
        zero_denominator_policy=getattr(row, "zero_denominator_policy", "constant"),
        zero_value=float(getattr(row, "zero_value", 0.0)),
        active=row.active,
        notes="Canonical restricted Derived definition.",
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


def _legacy_ml_order(
    rows: tuple[DataDefinitionDraftRow, ...],
) -> tuple[DataDefinitionRowIdentity, ...]:
    role_order = {"input": 0, "auto": 1, "one_hot_feature": 2, "result": 3, "derived": 4}
    eligible = [
        row
        for row in rows
        if row.active and (
            row.source_kind == "derived_policy"
            or bool(row.ml_name) and (row.model_input_enabled or row.role == "result")
        )
    ]
    return tuple(
        row.identity
        for row in sorted(
            eligible,
            key=lambda item: (
                role_order.get("derived" if item.source_kind == "derived_policy" else item.role, 99),
                item.display_order,
            ),
        )
    )
