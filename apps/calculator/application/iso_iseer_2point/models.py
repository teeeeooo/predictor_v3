"""UI-neutral models for ISO/ISEER 2-point calculation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


MeasuredPoints = Mapping[str, Mapping[str, float]]
ResultRow = tuple[str, str, str, str, str, str]
DetailRows = Mapping[str, tuple[dict, ...]]
DetailSummaries = Mapping[str, tuple[tuple[str, str], ...]]


@dataclass(frozen=True)
class IsoIseer2PointUseCaseResult:
    """Result returned by the ISO/ISEER 2-point application usecase."""

    status: str
    status_text: str
    rows: tuple[ResultRow, ...] = ()
    detail_sources: DetailRows | None = None
    detail_summaries: DetailSummaries | None = None
    detail_status: str | None = None

    @property
    def is_ok(self) -> bool:
        return self.status == "ok"
