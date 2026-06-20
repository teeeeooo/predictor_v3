"""Schemas and parsers for agent change-gate evidence."""

from __future__ import annotations

from dataclasses import dataclass

_NEW_SOURCE_VALUES = {"none", "small", "split", "justified"}
_HOTSPOT_VALUES = {
    "none",
    "wiring-only",
    "accepted-for-slice",
    "split-audit-required",
    "split-required",
}
_CODE_MAP_VALUES = {"not_required", "checked", "skipped", "regenerated", "no-change"}
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
    report_exemption: str
    read_ledger: str


@dataclass(frozen=True)
class TaskManifest:
    allowed_paths: tuple[str, ...]
    report_path: str | None
    reason: str
    scope: str
    approved_by_user: bool


def parse_change_gate(source: str) -> ChangeGate:
    fields = _parse_indented_fields(source, "change_gate")
    required = {
        "new_source",
        "hotspot_delta",
        "code_map_check",
        "report_exemption",
        "read_ledger",
    }
    if set(fields) != required:
        raise ValueError(f"change_gate fields must be exactly {sorted(required)!r}")
    gate = ChangeGate(**fields)
    allowed = (
        (gate.new_source, _NEW_SOURCE_VALUES, "new_source"),
        (gate.hotspot_delta, _HOTSPOT_VALUES, "hotspot_delta"),
        (gate.code_map_check, _CODE_MAP_VALUES, "code_map_check"),
        (gate.report_exemption, _EXEMPTION_VALUES, "report_exemption"),
        (gate.read_ledger, _LEDGER_VALUES, "read_ledger"),
    )
    for value, choices, key in allowed:
        if value not in choices:
            raise ValueError(f"unsupported {key}: {value}")
    return gate


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
            if not separator or key not in {"allowed_paths", "report_path", "report_exemption"}:
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
    if reason not in _EXEMPTION_VALUES - {"none"}:
        raise ValueError(f"unsupported manifest exemption: {reason}")
    if not scope or not approved:
        raise ValueError("manifest requires scope and approved_by_user: true")
    return TaskManifest(tuple(allowed), report_path, reason, scope, approved)


def _parse_indented_fields(source: str, heading: str) -> dict[str, str]:
    lines = source.splitlines()
    matches = [index for index, line in enumerate(lines) if line.strip() == f"{heading}:"]
    if len(matches) != 1:
        raise ValueError(f"report must contain exactly one {heading} block")
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
    return value.strip().strip('"\'')
