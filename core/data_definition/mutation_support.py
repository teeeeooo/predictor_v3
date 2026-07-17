"""Shared validation helpers for controlled basic Feature mutations."""

from __future__ import annotations

from core.data_definition.command_types import (
    DataDefinitionCommandIssue,
    DataDefinitionCommandResult,
)
from core.data_definition.dependency_policy import FeatureDependency, is_supported_basic_feature


def new_name_issues(draft, label, column_key, ml_name, *, exclude=None):  # noqa: ANN001
    issues = []
    if not label:
        issues.append(issue("label_required", "label", "Display name is required."))
    if not column_key or not column_key[0].isalpha():
        issues.append(issue(
            "column_key_invalid", "column_key",
            "Predict key must normalize to snake_case and start with a letter.",
        ))
    for item in draft.rows:
        if item.identity == exclude:
            continue
        if column_key and item.column_key == column_key:
            issues.append(issue(
                "column_key_duplicate", "column_key",
                f"Predict key '{column_key}' already exists in the current draft.",
                "Enter a unique Predict key.",
            ))
        if ml_name and item.ml_name == ml_name:
            issues.append(issue(
                "ml_name_duplicate", "ml_name",
                f"ML name '{ml_name}' already exists in the current draft.",
                "Enter a unique ML name.",
            ))
    return tuple(issues)


def dependency_issue(item: FeatureDependency) -> DataDefinitionCommandIssue:
    return issue(item.code, "dependency", item.message, item.resolution)


def find_row(draft, identity):  # noqa: ANN001
    resolved = draft.resolve_identity(identity)
    return next((item for item in draft.rows if item.identity == resolved), None)


def unsupported(draft, row, action):  # noqa: ANN001
    if row is None:
        return reject(
            draft, action, "definition_not_found", "identity",
            "Feature not found.", "Refresh the draft and select an existing Feature.", None,
        )
    if is_supported_basic_feature(row):
        return None
    return reject(
        draft, action, "feature_authoring_deferred", "role",
        f"{action} is not available for role/source '{row.role}/{row.value_source}'.",
        "Use the later Derived, One-hot, or Target authoring slice.", row.identity,
    )


def next_display_order(draft):  # noqa: ANN001
    return (max((item.display_order for item in draft.rows if item.source_kind == "schema_row"), default=0) // 10 + 1) * 10


def append_ml_identity(draft, row):  # noqa: ANN001
    if not row.active or not row.ml_name or not row.model_input_enabled:
        return draft.ml_order
    first_derived = next(
        (index for index, identity in enumerate(draft.ml_order) if identity[0] == "derived_policy"),
        len(draft.ml_order),
    )
    return (*draft.ml_order[:first_derived], row.identity, *draft.ml_order[first_derived:])


def issue(code, field, message, resolution=""):  # noqa: ANN001
    return DataDefinitionCommandIssue(code, field, message, resolution)


def reject(draft, action, code, field, message, resolution, identity):  # noqa: ANN001
    return DataDefinitionCommandResult(
        draft, False, identity, action, (issue(code, field, message, resolution),)
    )
