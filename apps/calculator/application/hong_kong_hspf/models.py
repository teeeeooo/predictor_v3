"""UI-neutral models for Hong Kong HSPF calculation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


DetailRows = tuple[dict, ...]
SummaryFields = tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class HongKongHspfUseCaseResult:
    """Result returned by the Hong Kong HSPF application usecase."""

    status: str
    status_text: str
    summary_title: str = "HSPF"
    summary_fields: SummaryFields = ()
    detail_rows: DetailRows = ()
    detail_summary: SummaryFields = ()
    detail_status: str | None = None
    invalid_fields: Mapping[str, str] | None = None

    @property
    def is_ok(self) -> bool:
        return self.status == "ok"
