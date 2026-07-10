"""Schemas and parsers for agent change-gate evidence."""

from __future__ import annotations

from dataclasses import dataclass
import re

_NEW_SOURCE_VALUES = {"none", "small", "split", "justified"}
_HOTSPOT_VALUES = {
    "none",
    "wiring-only",
    "accepted-for-slice",
    "split-audit-required",
    "split-required",
}
_CODE_MAP_VALUES = {"not_required", "checked", "skipped", "regenerated", "no-change"}
_UI_LITERAL_EXEMPTION_VALUES = {"none", "approved-for-slice"}
_REUSE_COMMONIZATION_VALUES = {
    "not_required",
    "checked",
    "reused-existing-owner",
    "local-with-reason",
    "design-deferred",
}
_EXEMPTION_VALUES = {
    "none",
    "user-approved-docs-only",
    "user-approved-formatting-only",
    "commit-push-only",
    "status-only",
}
_LEDGER_VALUES = {"not_required", "included", "skipped"}


@dataclass(frozen=True)
class Finding:
    severity: str
    path: str
    message: str


@dataclass(frozen=True)
class ChangeGate:
    new_source: str
    hotspot_delta: str
    code_map_check: str
    ui_literal_exemption: str
    reuse_commonization: str
    report_exemption: str
    read_ledger: str


@dataclass(frozen=True)
class TaskManifest:
    allowed_paths: tuple[str, ...]
    report_path: str | None
    reason: str
    scope: str
    approved_by_user: bool


@dataclass(frozen=True)
class RecordMetadata:
    date: str
    topic: str
    tags: str
    memory_review: str
    memory_reason: str


def parse_change_gate(source: str) -> ChangeGate:
    fields = _parse_indented_fields(source, "change_gate")
    required = {
        "new_source",
        "hotspot_delta",
        "code_map_check",
        "ui_literal_exemption",
        "reuse_commonization",
    }
    optional = {"report_exemption", "read_ledger"}
    if not required.issubset(fields) or set(fields) - required - optional:
        raise ValueError(
            "change_gate fields must contain the five active decision fields"
        )
    fields.setdefault("report_exemption", "none")
    fields.setdefault("read_ledger", "not_required")
    gate = ChangeGate(**fields)
    allowed = (
        (gate.new_source, _NEW_SOURCE_VALUES, "new_source"),
        (gate.hotspot_delta, _HOTSPOT_VALUES, "hotspot_delta"),
        (gate.code_map_check, _CODE_MAP_VALUES, "code_map_check"),
        (
            gate.ui_literal_exemption,
            _UI_LITERAL_EXEMPTION_VALUES,
            "ui_literal_exemption",
        ),
        (
            gate.reuse_commonization,
            _REUSE_COMMONIZATION_VALUES,
            "reuse_commonization",
        ),
        (gate.report_exemption, _EXEMPTION_VALUES, "report_exemption"),
        (gate.read_ledger, _LEDGER_VALUES, "read_ledger"),
    )
    for value, choices, key in allowed:
        if value not in choices:
            raise ValueError(f"unsupported {key}: {value}")
    return gate


def parse_record_metadata(source: str) -> RecordMetadata:
    fields = _parse_indented_fields(source, "record")
    required = {"date", "topic", "tags", "memory_review", "memory_reason"}
    if set(fields) != required:
        raise ValueError(f"record fields must be exactly {sorted(required)!r}")
    metadata = RecordMetadata(**fields)
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", metadata.date):
        raise ValueError("record date must use YYYY-MM-DD")
    if not metadata.topic or not metadata.tags:
        raise ValueError("record topic and tags must be nonempty")
    if metadata.memory_review not in {"updated", "no-change"}:
        raise ValueError(f"unsupported memory_review: {metadata.memory_review}")
    if not metadata.memory_reason:
        raise ValueError("record memory_reason must be nonempty")
    return metadata


def parse_manifest(source: str) -> TaskManifest:
    allowed: list[str] = []
    report_path: str | None = None
    exemption: dict[str, str] = {}
    seen_top_level: set[str] = set()
    section = ""
    for raw in source.splitlines():
        text = raw.strip()
        if not text or text.startswith("#"):
            continue
        if "\t" in raw:
            raise ValueError("manifest indentation must use spaces")
        indent = len(raw) - len(raw.lstrip(" "))
        if indent == 0:
            key, separator, value = text.partition(":")
            if not separator or key not in {
                "allowed_paths",
                "report_path",
                "report_exemption",
            }:
                raise ValueError(f"unknown manifest top-level field: {key}")
            if key in seen_top_level:
                raise ValueError(f"duplicate manifest top-level field: {key}")
            seen_top_level.add(key)
            if key == "report_path":
                value = _plain_value(value)
                report_path = None if value in {"", "null", "~"} else value
                section = ""
            else:
                if value.strip():
                    raise ValueError(f"manifest {key} must be a block")
                section = key
            continue
        if indent != 2:
            raise ValueError("manifest nested fields must use two-space indentation")
        if section == "allowed_paths" and text.startswith("- "):
            path = _plain_value(text[2:])
            if not path:
                raise ValueError("manifest allowed_paths entries must be nonempty")
            allowed.append(path)
            continue
        if section == "report_exemption" and ":" in text:
            key, value = text.split(":", 1)
            if key not in {"reason", "scope", "approved_by_user"}:
                raise ValueError(f"unknown report_exemption field: {key}")
            if key in exemption:
                raise ValueError(f"duplicate report_exemption field: {key}")
            exemption[key] = _plain_value(value)
            continue
        raise ValueError(f"invalid manifest field placement: {text}")
    if not allowed:
        raise ValueError("manifest allowed_paths must be nonempty")
    if any("*" in path or "?" in path for path in allowed):
        raise ValueError("manifest allowed_paths must use literal paths")
    reason = exemption.get("reason", "")
    scope = exemption.get("scope", "")
    approved = exemption.get("approved_by_user", "") == "true"
    if exemption:
        if reason not in _EXEMPTION_VALUES - {"none"}:
            raise ValueError(f"unsupported manifest exemption: {reason}")
        if not scope or not approved:
            raise ValueError("manifest requires scope and approved_by_user: true")
    else:
        reason = "none"
    return TaskManifest(tuple(allowed), report_path, reason, scope, approved)


def _parse_indented_fields(source: str, heading: str) -> dict[str, str]:
    lines = source.splitlines()
    matches = [
        index for index, line in enumerate(lines) if line.strip() == f"{heading}:"
    ]
    if len(matches) != 1:
        raise ValueError(f"record must contain exactly one {heading} block")
    fields: dict[str, str] = {}
    for line in lines[matches[0] + 1 :]:
        if not line.startswith((" ", "\t")):
            break
        text = line.strip()
        if text and ":" in text:
            key, value = text.split(":", 1)
            fields[key.strip()] = _plain_value(value)
    return fields


def _plain_value(value: str) -> str:
    return value.strip().strip("\"'")
