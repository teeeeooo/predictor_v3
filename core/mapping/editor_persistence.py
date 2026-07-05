"""Persist mapping editor drafts to runtime mapping JSON."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from core.mapping.editor_model import MappingEditorDraft
from core.mapping.editor_projection import (
    COMPRESSOR_GROUP,
    EVAP_INDEX_GROUP,
    EXPANSION_GROUP,
    IDU_GROUP,
    ODU_COND_SPECS_GROUP,
    ODU_GROUP,
    REFRIGERANT_GROUP,
)
from core.mapping.editor_validation import validate_mapping_editor_draft
from core.mapping.entity_model import MappingValidationError


@dataclass(frozen=True)
class MappingEditorSaveResult:
    """Result of a mapping editor save attempt."""

    success: bool
    path: Path
    backup_path: Path | None = None
    issues: tuple[MappingValidationError, ...] = ()
    message: str = ""


def runtime_mapping_from_editor_draft(draft: MappingEditorDraft) -> dict[str, Any]:
    """Project user-facing draft groups back to owned runtime sections."""
    runtime = dict(draft.unowned_sections)
    runtime["idu"] = _simple_section(draft, IDU_GROUP)
    runtime["evap_index"] = _simple_section(draft, EVAP_INDEX_GROUP)
    runtime["odu"] = _simple_section(draft, ODU_GROUP)
    runtime["compressor"] = _simple_section(draft, COMPRESSOR_GROUP)
    runtime["ref_type"] = _option_section(draft, REFRIGERANT_GROUP)
    runtime["exp_type"] = _option_section(draft, EXPANSION_GROUP)
    cond_projection = _odu_cond_specs_sections(draft)
    runtime.update(cond_projection)
    return runtime


def save_mapping_editor_draft(
    draft: MappingEditorDraft,
    mapping_file: str | Path,
) -> MappingEditorSaveResult:
    """Validate and atomically save a draft to mapping JSON."""
    destination = Path(mapping_file)
    validation = validate_mapping_editor_draft(draft)
    if not validation.save_enabled:
        return MappingEditorSaveResult(
            success=False,
            path=destination,
            issues=validation.issues,
            message="Resolve Issues before saving.",
        )

    runtime = runtime_mapping_from_editor_draft(draft)
    backup_path: Path | None = None
    tmp_name = ""
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            backup_path = _backup_existing_file(destination)
        fd, tmp_name = tempfile.mkstemp(
            prefix=f".{destination.name}.",
            suffix=".tmp",
            dir=str(destination.parent),
        )
        with os.fdopen(fd, "w", encoding="utf-8") as json_file:
            json.dump(runtime, json_file, indent=2, ensure_ascii=False)
            json_file.write("\n")
        os.replace(tmp_name, destination)
    except Exception as exc:
        if tmp_name:
            try:
                Path(tmp_name).unlink(missing_ok=True)
            except OSError:
                pass
        return MappingEditorSaveResult(
            success=False,
            path=destination,
            backup_path=backup_path,
            message=f"Save failed: {exc}",
        )
    return MappingEditorSaveResult(
        success=True,
        path=destination,
        backup_path=backup_path,
        message=f"Saved mapping JSON to {destination}.",
    )


def _simple_section(draft: MappingEditorDraft, group_key: str) -> dict[str, dict[str, Any]]:
    group = draft.group(group_key)
    if group is None or not group.columns:
        return {}
    key_column = group.columns[0]
    numeric_columns = {
        "ID Volume",
        "Evap Area",
        "Evap Volume",
        "OD Volume",
        "Comp EER",
        "Comp cc",
    }
    section: dict[str, dict[str, Any]] = {}
    for row in group.rows:
        key = _clean(row.value_for(key_column))
        if not key:
            continue
        section[key] = {
            column: _coerce_number(row.value_for(column))
            if column in numeric_columns
            else row.value_for(column, "")
            for column in group.columns[1:]
        }
    return section


def _option_section(draft: MappingEditorDraft, group_key: str) -> dict[str, dict[str, Any]]:
    group = draft.group(group_key)
    if group is None or not group.columns:
        return {}
    key_column = group.columns[0]
    return {
        key: {}
        for key in sorted({_clean(row.value_for(key_column)) for row in group.rows})
        if key
    }


def _odu_cond_specs_sections(draft: MappingEditorDraft) -> dict[str, Any]:
    group = draft.group(ODU_COND_SPECS_GROUP)
    if group is None:
        return {"odu_cascade": {}, "cond_specs": {}, "fin_type": {}, "pi": {}, "row": {}}

    cascade: dict[str, dict[str, list[str]]] = {}
    options: dict[str, set[str]] = defaultdict(set)
    cond_specs: dict[str, dict[str, Any]] = {}
    grouped: dict[str, dict[str, set[str]]] = defaultdict(
        lambda: {"Available_Fins": set(), "Available_Pis": set(), "Available_Rows": set()}
    )
    for draft_row in group.rows:
        odu = _clean(draft_row.value_for("ODU"))
        fin = _clean(draft_row.value_for("Fin Type"))
        pi = _clean(draft_row.value_for("Pi"))
        row = _clean(draft_row.value_for("Row"))
        if not all((odu, fin, pi, row)):
            continue
        grouped[odu]["Available_Fins"].add(fin)
        grouped[odu]["Available_Pis"].add(pi)
        grouped[odu]["Available_Rows"].add(row)
        options["fin_type"].add(fin)
        options["pi"].add(pi)
        options["row"].add(row)
        cond_specs[f"{odu} {fin} {pi} {row}"] = {
            "Cond Area": _coerce_number(draft_row.value_for("Cond Area")),
            "Cond Volume": _coerce_number(draft_row.value_for("Cond Volume")),
        }

    for odu, values in grouped.items():
        cascade[odu] = {
            "Available_Fins": sorted(values["Available_Fins"]),
            "Available_Pis": sorted(values["Available_Pis"]),
            "Available_Rows": sorted(values["Available_Rows"]),
        }
    return {
        "odu_cascade": cascade,
        "cond_specs": cond_specs,
        "fin_type": {value: {} for value in sorted(options["fin_type"])},
        "pi": {value: {} for value in sorted(options["pi"])},
        "row": {value: {} for value in sorted(options["row"])},
    }


def _backup_existing_file(destination: Path) -> Path:
    backup_dir = destination.parent / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    backup_path = backup_dir / f"{destination.stem}_{stamp}{destination.suffix}"
    shutil.copy2(destination, backup_path)
    return backup_path


def _coerce_number(value: Any) -> Any:
    text = _clean(value)
    if not text:
        return ""
    number = float(text)
    return int(number) if number.is_integer() else number


def _clean(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()
