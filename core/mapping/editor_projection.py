"""Project runtime mapping data into user-facing editor draft groups."""

from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from itertools import product
from typing import Any

from core.mapping.condenser_identity import condenser_requires_pi, condenser_spec_key
from core.mapping.editor_model import (
    MappingEditorDraft,
    MappingEditorGroup,
    MappingEditorRow,
)
from core.mapping.paths import MAPPING_JSON_FILE
from core.mapping.repository import load_mapping_data

IDU_GROUP = "idu"
EVAP_INDEX_GROUP = "evap_index"
ODU_GROUP = "odu"
COMPRESSOR_GROUP = "compressor"
REFRIGERANT_GROUP = "refrigerant"
EXPANSION_GROUP = "expansion"
ODU_COND_SPECS_GROUP = "odu_cond_specs"
MAPPING_ENTITY_GROUP_ALIASES = {
    "cond_specs": ODU_COND_SPECS_GROUP,
    "ref_type": REFRIGERANT_GROUP,
    "exp_type": EXPANSION_GROUP,
}

OWNED_RUNTIME_SECTIONS = (
    "idu",
    "evap_index",
    "odu",
    "compressor",
    "ref_type",
    "exp_type",
    "odu_cascade",
    "cond_specs",
    "fin_type",
    "pi",
    "row",
)


def load_runtime_mapping_editor_draft(
    mapping_file: str | None = None,
) -> MappingEditorDraft:
    """Load runtime mapping data and project it into editor draft groups."""
    source_path = mapping_file or MAPPING_JSON_FILE
    mapping_data = load_mapping_data(source_path)
    if not mapping_data:
        raise ValueError(f"runtime mapping data is empty or unavailable: {source_path}")
    if not isinstance(mapping_data, Mapping):
        raise ValueError("runtime mapping data must be a JSON object")
    return project_runtime_mapping_to_editor_draft(
        mapping_data,
        source_label=f"Runtime mapping repository: {source_path}",
    )


def project_runtime_mapping_to_editor_draft(
    mapping_data: Mapping[str, Any],
    *,
    source_label: str = "runtime mapping repository",
) -> MappingEditorDraft:
    """Return the seven user-facing draft groups from runtime mapping data."""
    groups = (
        _simple_group(IDU_GROUP, "IDU", ("IDU", "ID Volume", "Size"), "idu", mapping_data),
        _simple_group(
            EVAP_INDEX_GROUP,
            "Evap Index",
            ("Evap Index", "Size", "Evap Area", "Evap Volume"),
            "evap_index",
            mapping_data,
        ),
        _simple_group(ODU_GROUP, "ODU", ("ODU", "OD Volume"), "odu", mapping_data),
        _simple_group(
            COMPRESSOR_GROUP,
            "Compressor",
            ("Compressor", "Comp EER", "Comp cc"),
            "compressor",
            mapping_data,
        ),
        _option_group(
            REFRIGERANT_GROUP,
            "Refrigerant",
            ("Refrigerant",),
            "ref_type",
            mapping_data,
        ),
        _option_group(EXPANSION_GROUP, "Expansion", ("Expansion",), "exp_type", mapping_data),
        _odu_cond_specs_group(mapping_data),
    )
    return MappingEditorDraft(
        groups=groups,
        unowned_sections=_unowned_sections(mapping_data),
        source_label=source_label,
    )


def apply_mapping_requirements_to_editor_draft(
    draft: MappingEditorDraft,
    mapping_requirements: tuple[object, ...] = (),
) -> MappingEditorDraft:
    """Return a draft with Data Definition-required mapping attributes visible."""
    required_by_group = _requirements_by_group(mapping_requirements)
    if not required_by_group:
        return draft
    groups = tuple(
        _apply_group_requirements(group, required_by_group.get(group.group_key, ()))
        for group in draft.groups
    )
    return MappingEditorDraft(
        groups=groups,
        unowned_sections=draft.unowned_sections,
        source_label=draft.source_label,
    )


def mapping_group_key_for_requirement(requirement: object) -> str:
    """Return the Data Mapping group key for one Data Definition requirement."""
    entity = str(getattr(requirement, "mapping_entity", "")).strip()
    return MAPPING_ENTITY_GROUP_ALIASES.get(entity, entity)


def _simple_group(
    group_key: str,
    label: str,
    columns: tuple[str, ...],
    section_name: str,
    mapping_data: Mapping[str, Any],
) -> MappingEditorGroup:
    section = mapping_data.get(section_name, {})
    rows: list[MappingEditorRow] = []
    if isinstance(section, Mapping):
        key_column = columns[0]
        for row_key in sorted(str(key) for key in section):
            row_value = section.get(row_key)
            values = {column: "" for column in columns}
            values[key_column] = row_key
            if isinstance(row_value, Mapping):
                values.update({str(key): value for key, value in row_value.items()})
            rows.append(MappingEditorRow(values=values, source_key=row_key))
    return MappingEditorGroup(
        group_key=group_key,
        label=label,
        columns=columns,
        rows=tuple(rows),
        runtime_sections=(section_name,),
    )


def _requirements_by_group(
    mapping_requirements: tuple[object, ...],
) -> dict[str, tuple[object, ...]]:
    grouped: dict[str, list[object]] = {}
    for requirement in mapping_requirements:
        group_key = mapping_group_key_for_requirement(requirement)
        attribute = str(getattr(requirement, "mapping_attribute", "")).strip()
        if not group_key or not attribute:
            continue
        grouped.setdefault(group_key, [])
        if not any(
            str(getattr(item, "mapping_attribute", "")).strip() == attribute
            for item in grouped[group_key]
        ):
            grouped[group_key].append(requirement)
    return {key: tuple(values) for key, values in grouped.items()}


def _apply_group_requirements(
    group: MappingEditorGroup,
    requirements: tuple[object, ...],
) -> MappingEditorGroup:
    if not requirements:
        return group
    required_columns = tuple(
        str(getattr(requirement, "mapping_attribute", "")).strip()
        for requirement in requirements
    )
    columns = (*group.columns, *(column for column in required_columns if column not in group.columns))
    rows = tuple(_row_with_columns(row, columns) for row in group.rows)
    column_data_types = dict(group.column_data_types)
    required = list(group.required_columns)
    for requirement, column in zip(requirements, required_columns):
        data_type = str(getattr(requirement, "data_type", "string")).strip() or "string"
        if data_type not in {"string", "number", "boolean"}:
            raise ValueError(
                f"unsupported mapping attribute data type '{data_type}' for '{column}'"
            )
        column_data_types[column] = data_type
        if bool(getattr(requirement, "required", True)) and column not in required:
            required.append(column)
    return MappingEditorGroup(
        group_key=group.group_key,
        label=group.label,
        columns=columns,
        rows=rows,
        runtime_sections=group.runtime_sections,
        notes=_requirement_note(group.notes, tuple(required)),
        column_data_types=column_data_types,
        required_columns=tuple(required),
    )


def _row_with_columns(row: MappingEditorRow, columns: tuple[str, ...]) -> MappingEditorRow:
    values = {column: row.value_for(column, "") for column in columns}
    return MappingEditorRow(
        values=values,
        source_key=row.source_key,
        unresolved=row.unresolved,
        notes=row.notes,
    )


def _requirement_note(existing: str, required_columns: tuple[str, ...]) -> str:
    note = f"Required by Data Definition: {', '.join(required_columns)}"
    if not existing:
        return note
    if note in existing:
        return existing
    return f"{existing} {note}"


def _option_group(
    group_key: str,
    label: str,
    columns: tuple[str, ...],
    section_name: str,
    mapping_data: Mapping[str, Any],
) -> MappingEditorGroup:
    section = mapping_data.get(section_name, {})
    rows: list[MappingEditorRow] = []
    if isinstance(section, Mapping):
        key_column = columns[0]
        rows = [
            MappingEditorRow(values={key_column: row_key}, source_key=row_key)
            for row_key in sorted(str(key) for key in section)
        ]
    return MappingEditorGroup(
        group_key=group_key,
        label=label,
        columns=columns,
        rows=tuple(rows),
        runtime_sections=(section_name,),
    )


def _odu_cond_specs_group(mapping_data: Mapping[str, Any]) -> MappingEditorGroup:
    columns = ("ODU", "Fin Type", "Pi", "Row", "Cond Area", "Cond Volume")
    cond_specs = _mapping_section(mapping_data, "cond_specs")
    matched: set[str] = set()
    rows: list[MappingEditorRow] = []

    for odu, spec in _mapping_section(mapping_data, "odu_cascade").items():
        if not isinstance(spec, Mapping):
            continue
        fins = _string_values(spec.get("Available_Fins", ()))
        pis = _string_values(spec.get("Available_Pis", ()))
        rows_values = _string_values(spec.get("Available_Rows", ()))
        for fin in fins:
            fin_pis = pis if condenser_requires_pi(fin) else ("",)
            for pi, row in product(fin_pis, rows_values):
                key = condenser_spec_key(odu, fin, pi, row)
                cond_value = cond_specs.get(key)
                if not isinstance(cond_value, Mapping):
                    continue
                matched.add(key)
                rows.append(_odu_cond_specs_row(str(odu), fin, pi, row, cond_value, key))

    for key in sorted(str(key) for key in cond_specs if str(key) not in matched):
        cond_value = cond_specs.get(key)
        rows.append(_unresolved_cond_specs_row(key, cond_value))

    return MappingEditorGroup(
        group_key=ODU_COND_SPECS_GROUP,
        label="ODU Cond Specs",
        columns=columns,
        rows=tuple(rows),
        runtime_sections=("odu_cascade", "cond_specs", "fin_type", "pi", "row"),
    )


def _odu_cond_specs_row(
    odu: str,
    fin: str,
    pi: str,
    row: str,
    cond_value: Mapping[str, Any],
    source_key: str,
) -> MappingEditorRow:
    return MappingEditorRow(
        values={
            **{str(key): value for key, value in cond_value.items()},
            "ODU": odu,
            "Fin Type": fin,
            "Pi": pi,
            "Row": row,
        },
        source_key=source_key,
    )


def _unresolved_cond_specs_row(key: str, cond_value: Any) -> MappingEditorRow:
    values = {
        "ODU": key,
        "Fin Type": "",
        "Pi": "",
        "Row": "",
        "Cond Area": "",
        "Cond Volume": "",
    }
    if isinstance(cond_value, Mapping):
        values.update({str(item): value for item, value in cond_value.items()})
    return MappingEditorRow(
        values=values,
        source_key=key,
        unresolved=True,
        notes="Unresolved cond_specs row not matched by ODU cascade options.",
    )


def _mapping_section(mapping_data: Mapping[str, Any], section_name: str) -> Mapping[str, Any]:
    section = mapping_data.get(section_name, {})
    return section if isinstance(section, Mapping) else {}


def _string_values(value: Any) -> tuple[str, ...]:
    if isinstance(value, (str, bytes)) or not isinstance(value, tuple | list):
        return ()
    return tuple(str(item) for item in value if str(item).strip())


def _unowned_sections(mapping_data: Mapping[str, Any]) -> dict[str, Any]:
    return {
        str(key): deepcopy(value)
        for key, value in mapping_data.items()
        if str(key) not in OWNED_RUNTIME_SECTIONS
    }
