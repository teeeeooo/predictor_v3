"""Qt-free parser facade for the mapping_bundle_v1 exchange format."""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass

from core.mapping.editor_model import MappingEditorDraft
from core.mapping.entity_model import MappingValidationError
from core.mapping.exchange.candidate import build_mapping_exchange_candidate
from core.mapping.exchange.contract import (
    BUNDLE_FORMAT,
    BUNDLE_FORMAT_MARKER,
    CANONICAL_GROUP_KEYS,
)
from core.mapping.exchange.parser import import_issue, parse_mapping_sections


@dataclass(frozen=True)
class MappingExchangeImportResult:
    """Parser result containing either a complete candidate or blockers."""

    success: bool
    format_version: str = ""
    section_order: tuple[str, ...] = ()
    candidate: MappingEditorDraft | None = None
    blockers: tuple[MappingValidationError, ...] = ()
    warnings: tuple[MappingValidationError, ...] = ()
    message: str = ""

    @property
    def can_apply(self) -> bool:
        """Return whether a complete replacement candidate is available."""
        return self.success and self.candidate is not None and not self.blockers


def parse_mapping_exchange_bundle(
    source: bytes | str,
    current_draft: MappingEditorDraft,
) -> MappingExchangeImportResult:
    """Parse and validate a bundle without consulting its filename or state."""
    decoded, decode_issue = _decode_source(source)
    if decode_issue is not None:
        return _blocked(decode_issue)
    try:
        records = list(csv.reader(io.StringIO(decoded, newline=""), strict=True))
    except csv.Error as exc:
        return _blocked(
            import_issue(
                "import_malformed_csv",
                f"Malformed CSV: {exc}",
                field="source",
            )
        )

    first_index = next((index for index, record in enumerate(records) if record), None)
    if first_index is None:
        return _blocked(
            import_issue(
                "import_format_marker_missing",
                "The bundle format marker is missing.",
                field=BUNDLE_FORMAT_MARKER,
            )
        )
    first = records[first_index]
    if not first or first[0] != BUNDLE_FORMAT_MARKER:
        return _blocked(
            import_issue(
                "import_format_marker_missing",
                "The first non-blank record must declare mapping_bundle_v1.",
                field=BUNDLE_FORMAT_MARKER,
            )
        )
    if len(first) != 2:
        return _blocked(
            import_issue(
                "import_format_marker_malformed",
                "The format marker must contain exactly __FORMAT__ and a version.",
                field=BUNDLE_FORMAT_MARKER,
            )
        )
    format_version = first[1]
    if format_version != BUNDLE_FORMAT:
        return _blocked(
            import_issue(
                "import_unsupported_format",
                f"Unsupported mapping bundle format '{format_version}'.",
                field=format_version,
            ),
            format_version=format_version,
        )

    blockers: list[MappingValidationError] = []
    format_count = sum(
        1 for record in records if record and record[0] == BUNDLE_FORMAT_MARKER
    )
    if format_count > 1:
        blockers.append(
            import_issue(
                "import_duplicate_format_marker",
                "The bundle contains a duplicate format marker.",
                field=BUNDLE_FORMAT_MARKER,
            )
        )

    sections, section_order = parse_mapping_sections(
        records[first_index + 1 :],
        current_draft,
        blockers,
    )
    for group_key in CANONICAL_GROUP_KEYS:
        if group_key not in sections:
            blockers.append(
                import_issue(
                    "import_missing_section",
                    f"Required group '{group_key}' section is missing.",
                    group=group_key,
                )
            )
    if blockers:
        return _blocked(
            *blockers,
            format_version=format_version,
            section_order=section_order,
        )

    candidate, candidate_blockers = build_mapping_exchange_candidate(
        current_draft,
        sections,
    )
    if candidate_blockers:
        return _blocked(
            *candidate_blockers,
            format_version=format_version,
            section_order=section_order,
        )
    return MappingExchangeImportResult(
        success=True,
        format_version=format_version,
        section_order=section_order,
        candidate=candidate,
        message="Mapping bundle parsed and validated.",
    )


def _decode_source(source: bytes | str) -> tuple[str, MappingValidationError | None]:
    if isinstance(source, bytes):
        try:
            return source.decode("utf-8-sig"), None
        except UnicodeDecodeError as exc:
            return "", import_issue(
                "import_invalid_encoding",
                f"Bundle must be UTF-8 CSV: {exc}",
                field="source",
            )
    return str(source), None


def _blocked(
    *blockers: MappingValidationError,
    format_version: str = "",
    section_order: tuple[str, ...] = (),
) -> MappingExchangeImportResult:
    return MappingExchangeImportResult(
        success=False,
        format_version=format_version,
        section_order=section_order,
        blockers=tuple(blockers),
        message="Mapping bundle import is blocked.",
    )
