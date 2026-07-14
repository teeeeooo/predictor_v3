"""Strict value and duplicate checks for the legacy mapping adapter."""

from __future__ import annotations

import math
from typing import Any


class LegacyMappingBootstrapError(ValueError):
    """One strict legacy bootstrap failure with source context."""

    def __init__(
        self,
        reason: str,
        *,
        legacy_row: int | None = None,
        block: str = "",
        field: str = "",
        key: str = "",
    ) -> None:
        self.reason = reason
        self.legacy_row = legacy_row
        self.block = block
        self.field = field
        self.key = key
        context = [f"legacy row={legacy_row}" if legacy_row is not None else ""]
        context.extend(
            (f"block={block}" if block else "", f"field={field}" if field else "")
        )
        context.append(f"key={key}" if key else "")
        super().__init__(f"{reason} ({', '.join(item for item in context if item)})")


def reject_duplicate(
    seen: dict[Any, int],
    identity: Any,
    legacy_row: int,
    block: str,
    reason: str,
    display_key: str | None = None,
) -> None:
    if identity in seen:
        raise LegacyMappingBootstrapError(
            f"{reason}; first seen at legacy row {seen[identity]}",
            legacy_row=legacy_row,
            block=block,
            key=display_key or str(identity),
        )
    seen[identity] = legacy_row


def parse_number(
    value: str,
    legacy_row: int,
    block: str,
    field: str,
    key: str,
) -> int | float:
    try:
        number = float(value)
    except ValueError as exc:
        raise _invalid_number(legacy_row, block, field, key) from exc
    if not math.isfinite(number):
        raise _invalid_number(legacy_row, block, field, key)
    return int(number) if number.is_integer() else number


def _invalid_number(
    legacy_row: int,
    block: str,
    field: str,
    key: str,
) -> LegacyMappingBootstrapError:
    return LegacyMappingBootstrapError(
        "numeric attribute is invalid",
        legacy_row=legacy_row,
        block=block,
        field=field,
        key=key,
    )
