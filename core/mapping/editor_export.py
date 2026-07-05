"""Export read-only mapping editor review snapshots."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.mapping.editor_model import MappingEditorDraft
from core.mapping.entity_model import MappingValidationError


@dataclass(frozen=True)
class MappingEditorExportResult:
    """Result of exporting a mapping editor review snapshot."""

    success: bool
    path: Path
    message: str = ""


def mapping_editor_snapshot_payload(
    draft: MappingEditorDraft,
    issues: tuple[MappingValidationError, ...] = (),
) -> dict[str, Any]:
    """Return a read-only user-facing snapshot payload."""
    return {
        "snapshot_type": "mapping_editor_review_snapshot",
        "read_only": True,
        "import_contract": False,
        "source": draft.source_label,
        "groups": [
            {
                "group": group.label,
                "key": group.group_key,
                "columns": list(group.columns),
                "rows": [
                    {
                        "values": {column: row.value_for(column, "") for column in group.columns},
                        "source_key": row.source_key,
                        "unresolved": row.unresolved,
                        "notes": row.notes,
                    }
                    for row in group.rows
                ],
            }
            for group in draft.groups
        ],
        "issues": [
            {
                "level": issue.severity,
                "group": issue.entity_key,
                "row": issue.row_key,
                "field": issue.attribute_key or issue.field,
                "message": issue.message,
            }
            for issue in issues
        ],
    }


def export_mapping_editor_snapshot_json(
    draft: MappingEditorDraft,
    issues: tuple[MappingValidationError, ...],
    destination: str | Path,
) -> MappingEditorExportResult:
    """Write a pretty JSON read-only review snapshot."""
    path = Path(destination)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = mapping_editor_snapshot_payload(draft, issues)
        with path.open("w", encoding="utf-8") as json_file:
            json.dump(payload, json_file, indent=2, ensure_ascii=False)
            json_file.write("\n")
    except Exception as exc:
        return MappingEditorExportResult(
            success=False,
            path=path,
            message=f"Export failed: {exc}",
        )
    return MappingEditorExportResult(
        success=True,
        path=path,
        message=f"Exported read-only review snapshot to {path}.",
    )
