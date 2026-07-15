"""Structural CSV section parser for mapping_bundle_v1."""

from __future__ import annotations

from dataclasses import dataclass

from core.mapping.editor_model import MappingEditorDraft, MappingEditorGroup
from core.mapping.exchange.contract import (
    BUNDLE_FORMAT_MARKER,
    BUNDLE_SECTION_MARKER,
    CANONICAL_GROUP_KEYS,
)
from core.mapping.entity_model import MappingValidationError


@dataclass(frozen=True)
class MappingExchangeSection:
    """One section's header and rectangular raw CSV rows."""

    header: tuple[str, ...]
    rows: tuple[tuple[str, ...], ...]


def parse_mapping_sections(
    records: list[list[str]],
    current_draft: MappingEditorDraft,
    blockers: list[MappingValidationError],
) -> tuple[dict[str, MappingExchangeSection], tuple[str, ...]]:
    """Parse section markers and headers while leaving values as CSV text."""
    current_groups = {group.group_key: group for group in current_draft.groups}
    sections: dict[str, MappingExchangeSection] = {}
    order: list[str] = []
    seen_sections: set[str] = set()
    current_key = ""
    header: tuple[str, ...] | None = None
    rows: list[tuple[str, ...]] = []

    def finalize() -> None:
        if not current_key:
            return
        if header is None:
            blockers.append(
                import_issue(
                    "import_section_header_missing",
                    f"Section '{current_key}' has no header row.",
                    group=current_key,
                )
            )
            return
        if current_key in CANONICAL_GROUP_KEYS and current_key not in sections:
            sections[current_key] = MappingExchangeSection(header, tuple(rows))

    for record in records:
        if not record:
            continue
        marker = record[0]
        if marker == BUNDLE_FORMAT_MARKER:
            blockers.append(
                import_issue(
                    "import_duplicate_format_marker",
                    "The bundle contains a duplicate format marker.",
                    field=BUNDLE_FORMAT_MARKER,
                )
            )
            continue
        if marker == BUNDLE_SECTION_MARKER:
            finalize()
            current_key = ""
            header = None
            rows = []
            if len(record) != 2 or not record[1].strip():
                blockers.append(
                    import_issue(
                        "import_section_marker_malformed",
                        "A section marker must contain __SECTION__ and a group key.",
                        field=BUNDLE_SECTION_MARKER,
                    )
                )
                continue
            current_key = record[1]
            order.append(current_key)
            if current_key in seen_sections:
                blockers.append(
                    import_issue(
                        "import_duplicate_section",
                        f"Section '{current_key}' appears more than once.",
                        group=current_key,
                    )
                )
            seen_sections.add(current_key)
            if current_key not in CANONICAL_GROUP_KEYS:
                blockers.append(
                    import_issue(
                        "import_unknown_section",
                        f"Unknown group section '{current_key}'.",
                        group=current_key,
                    )
                )
            continue
        if not current_key:
            blockers.append(
                import_issue(
                    "import_record_outside_section",
                    "Every data record must belong to a named group section.",
                    field="record",
                )
            )
            continue
        if header is None:
            header = tuple(record)
            group = current_groups.get(current_key)
            if group is not None:
                validate_section_header(current_key, group, header, blockers)
            continue
        if len(record) != len(header):
            blockers.append(
                import_issue(
                    "import_row_width_mismatch",
                    f"Group '{current_key}' row has {len(record)} fields; expected {len(header)}.",
                    group=current_key,
                )
            )
            continue
        rows.append(tuple(record))
    finalize()
    return sections, tuple(order)


def validate_section_header(
    group_key: str,
    group: MappingEditorGroup,
    header: tuple[str, ...],
    blockers: list[MappingValidationError],
) -> None:
    """Enforce the exact current visible header set while allowing reorder."""
    seen: set[str] = set()
    duplicates: list[str] = []
    for column in header:
        if column in seen:
            duplicates.append(column)
        seen.add(column)
    if duplicates:
        duplicate_text = ", ".join(sorted(set(duplicates)))
        blockers.append(
            import_issue(
                "import_duplicate_header",
                f"Group '{group.label}' contains duplicate header(s): {duplicate_text}. "
                "Re-export using the current Data Definition projection.",
                group=group_key,
                field=duplicate_text,
            )
        )
    expected = set(group.columns)
    actual = set(header)
    missing = tuple(column for column in group.columns if column not in actual)
    unknown = tuple(column for column in header if column not in expected)
    if missing:
        missing_text = ", ".join(missing)
        blockers.append(
            import_issue(
                "import_missing_column",
                f"Group '{group.label}' is missing column(s): {missing_text}. Re-export using the current Data Definition projection.",
                group=group_key,
                field=missing_text,
            )
        )
    if unknown:
        unknown_text = ", ".join(unknown)
        blockers.append(
            import_issue(
                "import_unknown_column",
                f"Group '{group.label}' contains unknown column(s): {unknown_text}. Define them in Data Definition, then re-export the official bundle.",
                group=group_key,
                field=unknown_text,
            )
        )


def import_issue(
    code: str,
    message: str,
    *,
    group: str = "",
    field: str = "",
    row_index: int | None = None,
) -> MappingValidationError:
    """Create one stable blocker with group/field/row targeting metadata."""
    return MappingValidationError(
        code=code,
        message=message,
        entity_key=group,
        attribute_key=field,
        row_key=str(row_index + 1) if row_index is not None else "",
        field=field,
        row_index=row_index,
    )
