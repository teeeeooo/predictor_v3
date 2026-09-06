"""Schemas and parsers for staged agent change-gate controls."""

from __future__ import annotations

from dataclasses import dataclass

_UI_LITERAL_EXEMPTION_VALUES = {"none", "approved-for-slice"}


@dataclass(frozen=True)
class Finding:
    severity: str
    path: str
    message: str


@dataclass(frozen=True)
class TaskManifest:
    allowed_paths: tuple[str, ...]
    ui_literal_exemption: str = "none"


def parse_manifest(source: str) -> TaskManifest:
    allowed: list[str] = []
    ui_literal_exemption = "none"
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
            if not separator or key not in {"allowed_paths", "ui_literal_exemption"}:
                raise ValueError(f"unknown manifest top-level field: {key}")
            if key in seen_top_level:
                raise ValueError(f"duplicate manifest top-level field: {key}")
            seen_top_level.add(key)
            if key == "allowed_paths":
                if value.strip():
                    raise ValueError("manifest allowed_paths must be a block")
                section = "allowed_paths"
                continue
            ui_literal_exemption = _plain_value(value)
            if ui_literal_exemption not in _UI_LITERAL_EXEMPTION_VALUES:
                raise ValueError(
                    f"unsupported ui_literal_exemption: {ui_literal_exemption}"
                )
            section = ""
            continue
        if indent != 2:
            raise ValueError("manifest nested fields must use two-space indentation")
        if section == "allowed_paths" and text.startswith("- "):
            path = _plain_value(text[2:])
            if not path:
                raise ValueError("manifest allowed_paths entries must be nonempty")
            allowed.append(path)
            continue
        raise ValueError(f"invalid manifest field placement: {text}")

    if not allowed:
        raise ValueError("manifest allowed_paths must be nonempty")
    if any("*" in path or "?" in path for path in allowed):
        raise ValueError("manifest allowed_paths must use literal paths")
    return TaskManifest(tuple(allowed), ui_literal_exemption)


def _plain_value(value: str) -> str:
    return value.strip().strip("\"'")
