"""UI-neutral models for SASO T3 calculation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


MeasuredPoints = Mapping[str, Mapping[str, float]]
ResultRow = tuple[str, ...]
DetailRows = Mapping[str, tuple[dict, ...]]
DetailSummaries = Mapping[str, tuple[tuple[str, str], ...]]


@dataclass(frozen=True)
class SasoT3UseCaseResult:
    """Result returned by the SASO T3 application usecase."""

    status: str
    status_text: str
    rows: tuple[ResultRow, ...] = ()
    detail_sources: DetailRows | None = None
    detail_summaries: DetailSummaries | None = None
    detail_statuses: Mapping[str, str] | None = None
    detail_status: str | None = None
    invalid_fields: Mapping[str, str] | None = None

    @property
    def is_ok(self) -> bool:
        return self.status == "ok"
