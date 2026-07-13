"""Validate the repository schema/mapping/mock-training structural contract."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import pandas as pd

from core.data_definition.projection import (
    data_definition_rows_from_catalog,
    extract_mapping_requirements,
    project_feature_catalog_from_catalog,
)
from core.mapping.condenser_identity import (
    canonical_condenser_pi,
    condenser_requires_pi,
    condenser_spec_key,
)
from core.predictor_schema.catalog_v2 import (
    PredictSchemaCatalogV2,
    load_predict_schema_catalog_v2,
    validate_predict_schema_catalog_v2,
)

_SELECTOR_SECTIONS = {
    "idu": "idu",
    "evap_index": "evap_index",
    "odu": "odu",
    "compressor": "compressor",
    "ref_type": "ref_type",
    "exp_type": "exp_type",
}


def validate_mock_alignment(
    mapping: Mapping[str, Any],
    selections: Sequence[Mapping[str, Any]],
    training_frame: pd.DataFrame,
    schema: PredictSchemaCatalogV2 | None = None,
) -> None:
    """Fail fast when mock selectors, resolved values, schema, or training diverge."""
    catalog = schema or load_predict_schema_catalog_v2()
    schema_errors = validate_predict_schema_catalog_v2(catalog)
    if schema_errors:
        raise ValueError(f"schema fixture is invalid: {schema_errors[0]}")
    if len(selections) != len(training_frame):
        raise ValueError(
            "mock alignment row count mismatch: "
            f"{len(selections)} selection row(s), {len(training_frame)} training row(s)"
        )

    projected = project_feature_catalog_from_catalog(catalog)
    required_headers = {
        row.ml_name
        for row in projected
        if row.active and row.role in {"input", "auto", "one_hot", "result"}
    }
    missing_headers = sorted(required_headers - set(training_frame.columns))
    if missing_headers:
        raise ValueError(
            f"schema/training header mismatch: missing {', '.join(missing_headers)}"
        )

    requirements = extract_mapping_requirements(
        data_definition_rows_from_catalog(catalog)
    )
    for row_index, selection in enumerate(selections, start=1):
        _validate_selector_options(mapping, selection, row_index)
        cond_spec = _condenser_spec(mapping, selection, row_index)
        training_row = training_frame.iloc[row_index - 1]
        for requirement in requirements:
            if not requirement.model_input_enabled or not requirement.ml_name:
                continue
            source = (
                cond_spec
                if requirement.mapping_entity == "cond_specs"
                else _selected_mapping_row(
                    mapping,
                    requirement.mapping_entity,
                    selection.get(requirement.trigger_column),
                    row_index,
                )
            )
            if requirement.mapping_attribute not in source:
                raise ValueError(
                    f"mock row {row_index}: mapping attribute "
                    f"'{requirement.mapping_attribute}' is missing from "
                    f"'{requirement.mapping_entity}'."
                )
            _require_equal(
                training_row.get(requirement.ml_name),
                source[requirement.mapping_attribute],
                row_index,
                requirement.ml_name,
            )
        _validate_one_hot(catalog, mapping, selection, training_row, row_index)


def _validate_selector_options(
    mapping: Mapping[str, Any],
    selection: Mapping[str, Any],
    row_index: int,
) -> None:
    for selector, section_name in _SELECTOR_SECTIONS.items():
        value = _clean(selection.get(selector))
        section = mapping.get(section_name)
        if not isinstance(section, Mapping) or value not in section:
            raise ValueError(
                f"mock row {row_index}: {selector} option '{value}' is not present "
                f"in mapping section '{section_name}'."
            )


def _condenser_spec(
    mapping: Mapping[str, Any],
    selection: Mapping[str, Any],
    row_index: int,
) -> Mapping[str, Any]:
    odu = _clean(selection.get("odu"))
    fin = _clean(selection.get("fin_type"))
    pi = canonical_condenser_pi(fin, selection.get("pi"))
    row = _clean(selection.get("row"))
    if condenser_requires_pi(fin) and not pi:
        raise ValueError(
            f"mock row {row_index}: Pi is required for Fin Type '{fin}'."
        )
    if not condenser_requires_pi(fin) and _clean(selection.get("pi")):
        raise ValueError(f"mock row {row_index}: PFC Pi must be empty.")

    cascade = mapping.get("odu_cascade", {})
    spec = cascade.get(odu) if isinstance(cascade, Mapping) else None
    if not isinstance(spec, Mapping):
        raise ValueError(f"mock row {row_index}: ODU '{odu}' has no cascade mapping.")
    for field, value, option_key in (
        ("Fin Type", fin, "Available_Fins"),
        ("Row", row, "Available_Rows"),
    ):
        if value not in _string_options(spec.get(option_key)):
            raise ValueError(
                f"mock row {row_index}: {field} '{value}' is not available for ODU '{odu}'."
            )
    if pi and pi not in _string_options(spec.get("Available_Pis")):
        raise ValueError(
            f"mock row {row_index}: Pi '{pi}' is not available for ODU '{odu}'."
        )

    key = condenser_spec_key(odu, fin, pi, row)
    cond_specs = mapping.get("cond_specs")
    value = cond_specs.get(key) if isinstance(cond_specs, Mapping) else None
    if not isinstance(value, Mapping):
        raise ValueError(
            f"mock row {row_index}: condenser combination '{key}' is not mapped."
        )
    return value


def _selected_mapping_row(
    mapping: Mapping[str, Any],
    section_name: str,
    key: Any,
    row_index: int,
) -> Mapping[str, Any]:
    section = mapping.get(section_name)
    clean_key = _clean(key)
    value = section.get(clean_key) if isinstance(section, Mapping) else None
    if not isinstance(value, Mapping):
        raise ValueError(
            f"mock row {row_index}: mapping row '{section_name}/{clean_key}' is missing."
        )
    return value


def _validate_one_hot(
    catalog: PredictSchemaCatalogV2,
    mapping: Mapping[str, Any],
    selection: Mapping[str, Any],
    training_row: pd.Series,
    row_index: int,
) -> None:
    selector_by_group = {
        row.one_hot_group: row.column_key
        for row in catalog.active_rows
        if row.role == "input" and row.value_source == "one_hot" and row.one_hot_group
    }
    emitted_by_group: dict[str, list[str]] = {}
    for row in catalog.active_rows:
        if row.role == "one_hot_feature" and row.one_hot_group and row.ml_name:
            emitted_by_group.setdefault(row.one_hot_group, []).append(row.ml_name)
    for group, selector in selector_by_group.items():
        selected = _clean(selection.get(selector))
        for emitted in emitted_by_group.get(group, []):
            expected = 1.0 if emitted == selected else 0.0
            _require_equal(training_row.get(emitted), expected, row_index, emitted)


def _require_equal(actual: Any, expected: Any, row_index: int, field: str) -> None:
    try:
        equal = float(actual) == float(expected)
    except (TypeError, ValueError):
        equal = actual == expected
    if not equal:
        raise ValueError(
            f"mock row {row_index}: training field '{field}' is {actual!r}; "
            f"mapping/schema requires {expected!r}."
        )


def _string_options(value: Any) -> set[str]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        return set()
    return {_clean(item) for item in value if _clean(item)}


def _clean(value: Any) -> str:
    return "" if value is None else str(value).strip()
