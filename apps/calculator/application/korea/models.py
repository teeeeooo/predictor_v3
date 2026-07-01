"""UI-neutral models for KOREA calculator usecases."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


DetailRows = tuple[dict, ...]
SummaryFields = tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class KoreaCspfUseCaseResult:
    """Result returned by the KOREA CSPF application usecase."""

    status: str
    status_text: str
    summary_title: str = "CSPF"
    summary_fields: SummaryFields = ()
    detail_rows: DetailRows = ()
    detail_summary: SummaryFields = ()
    detail_status: str | None = None
    invalid_fields: Mapping[str, str] | None = None
    guide_fields: SummaryFields = ()
    guide_status: str | None = None

    @property
    def is_ok(self) -> bool:
        return self.status == "ok"
