"""Atomic restricted Derived command transitions."""

from __future__ import annotations

import math
from dataclasses import replace
from uuid import uuid4

from core.data_definition.command_types import (
    DataDefinitionCommandIssue,
    DataDefinitionCommandResult,
)
from core.data_definition.contract import candidate_manifest_from_draft, validate_contract
from core.data_definition.draft import DataDefinitionDraft, DataDefinitionDraftRow
from core.data_definition.derived.intents import (
    AddDerivedIntent,
    DerivedCommandIntent,
    DuplicateDerivedIntent,
    EditDerivedIntent,
    RemoveDerivedIntent,
    RenameDerivedIntent,
    SetDerivedActiveIntent,
)
from core.data_definition.derived.graph import derived_downstream_identities


def apply_derived_command(
    draft: DataDefinitionDraft,
    intent: DerivedCommandIntent,
) -> DataDefinitionCommandResult:
    if isinstance(intent, AddDerivedIntent):
        return _add(draft, intent)
    row, failure = _selected(draft, intent.identity, type(intent).__name__.removesuffix("DerivedIntent"))
    if failure is not None:
        return failure
    assert row is not None
    if isinstance(intent, EditDerivedIntent):
        zero, issue = _zero_value(intent.zero_value)
        if issue:
            return _reject(draft, row, "Edit", issue)
        updated = replace(
            row,
            operation=intent.operation.strip(),
            numerator_identity=intent.numerator_identity,
            denominator_identity=intent.denominator_identity,
            zero_denominator_policy=intent.zero_denominator_policy.strip(),
            zero_value=zero,
            active=row.active if intent.active is None else intent.active,
        )
        return _replace_and_validate(draft, row, updated, "Edit")
    if isinstance(intent, RenameDerivedIntent):
        updated = replace(row, ml_name=intent.ml_name.strip())
        return _replace_and_validate(draft, row, updated, "Rename")
    if isinstance(intent, DuplicateDerivedIntent):
        duplicate = replace(
            row,
            stable_identity=f"ufm_derived_{uuid4().hex}",
            ml_name=intent.ml_name.strip(),
            active=False,
        )
        return _add_row(draft, duplicate, "Duplicate")
    if isinstance(intent, RemoveDerivedIntent):
        downstream = derived_downstream_identities(draft, row.stable_identity)
        if downstream:
            return _reject(draft, row, "Remove", _issue(
                "derived_downstream_dependency",
                "dependency",
                "Remove would orphan downstream Derived definitions: " + ", ".join(downstream),
                "Remove or retarget downstream definitions first.",
            ))
        was_added = draft.is_controlled_row_addition(row.identity)
        candidate = replace(
            draft,
            rows=tuple(item for item in draft.rows if item.identity != row.identity),
            controlled_row_additions=frozenset(
                item for item in draft.controlled_row_additions if item != row.identity
            ),
            controlled_addition_initial_rows=tuple(
                item for item in draft.controlled_addition_initial_rows
                if item.identity != row.identity
            ),
            controlled_row_removals=(
                draft.controlled_row_removals
                if was_added
                else frozenset((*draft.controlled_row_removals, row.identity))
            ),
            controlled_field_changes=frozenset(
                item for item in draft.controlled_field_changes if item[0] != row.identity
            ),
            ml_order=tuple(item for item in draft.ml_order if item != row.identity),
        )
        return _validated(draft, candidate, None, "Remove", (row.identity,))
    if isinstance(intent, SetDerivedActiveIntent):
        if row.active == intent.active:
            return _reject(draft, row, "Enable" if intent.active else "Disable", _issue(
                "derived_active_state_unchanged", "active", "Derived active state is unchanged."
            ))
        if not intent.active:
            active_downstream = tuple(
                identity for identity in derived_downstream_identities(draft, row.stable_identity)
                if _row_by_stable_id(draft, identity).active
            )
            if active_downstream:
                return _reject(draft, row, "Disable", _issue(
                    "derived_downstream_dependency",
                    "dependency",
                    "Disable would make active downstream Derived unavailable: "
                    + ", ".join(active_downstream),
                    "Disable or retarget downstream definitions first.",
                ))
        updated = replace(row, active=intent.active)
        return _replace_and_validate(
            draft, row, updated, "Enable" if intent.active else "Disable"
        )
    raise TypeError(f"Unsupported Derived command: {type(intent).__name__}")


def _add(draft: DataDefinitionDraft, intent: AddDerivedIntent) -> DataDefinitionCommandResult:
    zero, issue = _zero_value(intent.zero_value)
    if issue:
        return _reject(draft, None, "Add", issue)
    row = DataDefinitionDraftRow(
        source_kind="derived_policy",
        stable_identity=f"ufm_derived_{uuid4().hex}",
        role="derived",
        data_type="number",
        ml_name=intent.ml_name.strip(),
        operation=intent.operation.strip(),
        numerator_identity=intent.numerator_identity,
        denominator_identity=intent.denominator_identity,
        zero_denominator_policy=intent.zero_denominator_policy.strip(),
        zero_value=zero,
        active=intent.active,
        notes="Canonical restricted Derived definition.",
    )
    return _add_row(draft, row, "Add")


def _add_row(draft, row, action):  # noqa: ANN001
    candidate = replace(
        draft,
        rows=(*draft.rows, row),
        controlled_row_additions=frozenset((*draft.controlled_row_additions, row.identity)),
        controlled_addition_initial_rows=(*draft.controlled_addition_initial_rows, row),
        ml_order=(*draft.ml_order, row.identity) if row.active else draft.ml_order,
    )
    return _validated(draft, candidate, row.identity, action)


def _replace_and_validate(draft, before, after, action):  # noqa: ANN001
    ml_order = draft.ml_order
    if before.active and not after.active:
        ml_order = tuple(item for item in ml_order if item != before.identity)
    elif not before.active and after.active:
        ml_order = (*ml_order, after.identity)
    candidate = replace(
        draft,
        rows=tuple(after if item.identity == before.identity else item for item in draft.rows),
        controlled_field_changes=frozenset((
            *draft.controlled_field_changes,
            *((before.identity, field) for field in (
                "ml_name", "operation", "numerator_identity", "denominator_identity",
                "zero_denominator_policy", "zero_value", "active",
            ) if getattr(before, field) != getattr(after, field)),
        )),
        ml_order=ml_order,
    )
    return _validated(draft, candidate, after.identity, action)


def _validated(original, candidate, identity, action, affected=()):  # noqa: ANN001
    if candidate.base_manifest is None:
        return _reject(original, None, action, _issue(
            "derived_canonical_manifest_required",
            "contract",
            "Derived authoring requires a canonical generation draft.",
            "Reload through the generation repository.",
        ))
    try:
        manifest = candidate_manifest_from_draft(candidate, candidate.base_manifest)
        issues = validate_contract(manifest)
    except (KeyError, TypeError, ValueError) as exc:
        code = (
            "derived_dependency_cycle"
            if "cycle" in str(exc).casefold()
            else "derived_candidate_invalid"
        )
        issues = (_SimpleIssue(code, str(exc)),)
    if issues:
        first = issues[0]
        return _reject(original, _find(original, identity), action, _issue(
            first.code,
            "derived",
            first.message,
            "Choose valid numeric operands and remove dependency or name conflicts.",
        ))
    return DataDefinitionCommandResult(
        candidate, True, identity, action, affected_identities=affected
    )


def _selected(draft, identity, action):  # noqa: ANN001
    row = _find(draft, identity)
    if row is None:
        return None, _reject(draft, None, action, _issue(
            "derived_not_found", "identity", "Derived definition was not found.", "Refresh and select it again."
        ))
    if row.source_kind != "derived_policy":
        return None, _reject(draft, row, action, _issue(
            "derived_selection_required", "identity", "Select a Derived definition."
        ))
    return row, None


def _find(draft, identity):  # noqa: ANN001
    if identity is None:
        return None
    resolved = draft.resolve_identity(identity)
    return next((item for item in draft.rows if item.identity == resolved), None)


def _row_by_stable_id(draft, identity):  # noqa: ANN001
    return next(item for item in draft.rows if item.stable_identity == identity)


def _zero_value(value: object) -> tuple[float, DataDefinitionCommandIssue | None]:
    if value is None or (isinstance(value, str) and not value.strip()):
        return 0.0, None
    if isinstance(value, bool):
        return 0.0, _issue("derived_zero_value_invalid", "zero_value", "Boolean is not a numeric constant.")
    try:
        normalized = float(value)
    except (TypeError, ValueError):
        return 0.0, _issue("derived_zero_value_invalid", "zero_value", "Enter a finite numeric constant.")
    if not math.isfinite(normalized):
        return 0.0, _issue("derived_zero_value_invalid", "zero_value", "NaN and infinity are not allowed.")
    return normalized, None


def _issue(code, field, message, resolution=""):  # noqa: ANN001
    return DataDefinitionCommandIssue(code, field, message, resolution)


def _reject(draft, row, action, issue):  # noqa: ANN001
    return DataDefinitionCommandResult(
        draft, False, row.identity if row is not None else None, action, (issue,)
    )


class _SimpleIssue:
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
