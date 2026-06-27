"""Pure mapping-based autofill and cascade policy."""

from dataclasses import dataclass, field
from typing import Any

from core.predictor_schema.columns import (
    COLUMNS,
    DROPDOWN_TARGET,
)


@dataclass(frozen=True)
class AutofillUpdate:
    """One row value update produced by mapping/autofill logic."""

    key: str
    value: Any


@dataclass(frozen=True)
class AutofillResult:
    """Mapping/autofill result for one edited row."""

    updates: tuple[AutofillUpdate, ...] = ()
    dropdown_options: dict[str, tuple[str, ...]] = field(default_factory=dict)


def build_autofill_updates(
    row_values: dict[str, Any],
    changed_key: str,
    mapping_data: dict[str, Any],
    columns: list[dict[str, Any]] | None = None,
) -> AutofillResult:
    """Return row updates after one dropdown/editable value changes."""
    schema = columns or COLUMNS
    updates: list[AutofillUpdate] = []
    dropdown_options: dict[str, tuple[str, ...]] = {}

    updates.extend(
        _simple_mapping_updates(
            row_values=row_values,
            changed_key=changed_key,
            mapping_data=mapping_data,
            columns=schema,
        )
    )

    if changed_key == "odu":
        updates.extend(
            [
                AutofillUpdate("fin_type", ""),
                AutofillUpdate("pi", ""),
                AutofillUpdate("row", ""),
                AutofillUpdate("cond_area", ""),
                AutofillUpdate("cond_volume", ""),
            ]
        )
        dropdown_options.update(_odu_dropdown_options(row_values, mapping_data))
    elif changed_key in {"fin_type", "pi", "row"}:
        updates.extend(_cond_spec_updates(row_values, mapping_data))

    return AutofillResult(
        updates=_dedupe_updates(updates),
        dropdown_options=dropdown_options,
    )


def _simple_mapping_updates(
    row_values: dict[str, Any],
    changed_key: str,
    mapping_data: dict[str, Any],
    columns: list[dict[str, Any]],
) -> list[AutofillUpdate]:
    section_name = DROPDOWN_TARGET.get(changed_key)
    if not section_name:
        return []

    target_columns = [
        column
        for column in columns
        if column.get("group") == "auto" and column.get("source") == changed_key
    ]
    if not target_columns:
        return []

    selected = _clean(row_values.get(changed_key))
    selected_spec = mapping_data.get(section_name, {}).get(selected)
    if not selected_spec:
        return [AutofillUpdate(str(column["key"]), "") for column in target_columns]

    updates: list[AutofillUpdate] = []
    for column in target_columns:
        mapping_key = column.get("mapping_key")
        if mapping_key:
            updates.append(
                AutofillUpdate(str(column["key"]), selected_spec.get(mapping_key, ""))
            )
    return updates


def _odu_dropdown_options(
    row_values: dict[str, Any],
    mapping_data: dict[str, Any],
) -> dict[str, tuple[str, ...]]:
    selected_odu = _clean(row_values.get("odu"))
    odu_spec = mapping_data.get("odu_cascade", {}).get(selected_odu, {})
    return {
        "fin_type": tuple(odu_spec.get("Available_Fins", ())),
        "pi": tuple(odu_spec.get("Available_Pis", ())),
        "row": tuple(odu_spec.get("Available_Rows", ())),
    }


def _cond_spec_updates(
    row_values: dict[str, Any],
    mapping_data: dict[str, Any],
) -> list[AutofillUpdate]:
    odu = _clean(row_values.get("odu"))
    fin = _clean(row_values.get("fin_type"))
    pi = _clean(row_values.get("pi"))
    row = _clean(row_values.get("row"))
    if not all((odu, fin, pi, row)):
        return [AutofillUpdate("cond_area", ""), AutofillUpdate("cond_volume", "")]

    cond_key = f"{odu} {fin} {pi} {row}"
    cond_spec = mapping_data.get("cond_specs", {}).get(cond_key)
    if not cond_spec:
        return [AutofillUpdate("cond_area", ""), AutofillUpdate("cond_volume", "")]
    return [
        AutofillUpdate("cond_area", cond_spec.get("Cond Area", "")),
        AutofillUpdate("cond_volume", cond_spec.get("Cond Volume", "")),
    ]


def _dedupe_updates(updates: list[AutofillUpdate]) -> tuple[AutofillUpdate, ...]:
    by_key: dict[str, AutofillUpdate] = {}
    for update in updates:
        by_key[update.key] = update
    return tuple(by_key.values())


def _clean(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()
