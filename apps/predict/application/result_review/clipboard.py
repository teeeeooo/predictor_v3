"""Full-row Result Review clipboard/export application boundary."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from io import StringIO
from math import isfinite

from apps.predict.application.result_enrichment import (
    COOLING_POWER_TARGET_ID,
    HEATING_POWER_TARGET_ID,
)

from .contracts import RESULT_REVIEW_COLUMNS, ResultReviewRow
from .presentation import display_value


_HIDDEN_HEADERS = (
    "냉방 소비전력 raw",
    "난방 소비전력 raw",
    "result freshness",
    "stable case identity",
    "execution run identity",
    "case input revision",
    "runtime generation identity",
    "loaded model candidate identity",
    "loaded model active revision",
    "loaded model generation identity",
    "cooling power Target identity",
    "cooling power Result Feature identity",
    "cooling power canonical unit",
    "cooling power value source",
    "heating power Target identity",
    "heating power Result Feature identity",
    "heating power canonical unit",
    "heating power value source",
    "stale reason",
    "issue reason codes",
    "issue messages",
)


@dataclass(frozen=True)
class ResultReviewClipboardDocument:
    """Flat TSV plus the richer typed rows from which it is serialized."""

    source_rows: tuple[ResultReviewRow, ...]

    @property
    def headers(self) -> tuple[str, ...]:
        return tuple(item.header for item in RESULT_REVIEW_COLUMNS) + _HIDDEN_HEADERS

    def grid(self) -> tuple[tuple[object, ...], ...]:
        return (self.headers,) + tuple(_clipboard_row(row) for row in self.source_rows)

    def to_tsv(self) -> str:
        return _format_tsv(self.grid())


def _clipboard_row(row: ResultReviewRow) -> tuple[object, ...]:
    targets = {item.target_identity: item for item in row.target_outcomes}
    cooling_power = targets.get(COOLING_POWER_TARGET_ID)
    heating_power = targets.get(HEATING_POWER_TARGET_ID)
    context = row.execution_context
    visible = (
        row.case_ordinal,
        display_value(row, "status"),
        _source_raw(row.cooling_capacity),
        _source_raw(row.heating_capacity),
        row.specification_summary,
        _metric_raw(row.eer),
        _metric_raw(row.cop),
        _target_raw(row.cooling_frequency),
        _target_raw(row.heating_frequency),
        _target_raw(row.refrigerant_quantity),
    )
    hidden = (
        _target_raw(cooling_power),
        _target_raw(heating_power),
        row.freshness,
        row.case_id,
        context.run_id if context else "",
        context.case_input_revision if context else "",
        context.semantics.runtime_generation_id if context else "",
        context.model.candidate_id if context else "",
        context.model.active_revision if context else "",
        context.model.generation_id if context else "",
        cooling_power.target_identity if cooling_power else "",
        cooling_power.result_feature_identity if cooling_power else "",
        cooling_power.canonical_unit if cooling_power else "",
        cooling_power.value_source if cooling_power else "",
        heating_power.target_identity if heating_power else "",
        heating_power.result_feature_identity if heating_power else "",
        heating_power.canonical_unit if heating_power else "",
        heating_power.value_source if heating_power else "",
        row.stale_reason,
        " | ".join(item.reason_code for item in row.issues if item.reason_code),
        " | ".join(item.message for item in row.issues if item.message),
    )
    return visible + hidden


def _source_raw(value) -> object:  # noqa: ANN001
    return _finite_or_blank(value.raw_value) if value.available else ""


def _target_raw(outcome) -> object:  # noqa: ANN001
    if outcome is None or outcome.status != "available":
        return ""
    return _finite_or_blank(outcome.raw_value)


def _metric_raw(outcome) -> object:  # noqa: ANN001
    if outcome is None or outcome.status != "available":
        return ""
    return _finite_or_blank(outcome.raw_value)


def _finite_or_blank(value: object | None) -> object:
    if value is None:
        return ""
    if isinstance(value, (int, float)) and not isfinite(float(value)):
        return ""
    return value


def _format_tsv(grid: tuple[tuple[object, ...], ...]) -> str:
    stream = StringIO(newline="")
    writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
    writer.writerows(grid)
    return stream.getvalue()
