"""Presentation-only formatting for Result Review values."""

from __future__ import annotations

from math import isfinite

from apps.predict.application.result_enrichment import DerivedMetricOutcome
from apps.predict.application.target_outcome import TargetOutcome

from .contracts import ResultReviewRow


UNAVAILABLE_DISPLAY = "—"

_STATUS_DISPLAY = {
    "pending": "대기",
    "running": "실행 중",
    "complete": "완료",
    "partial": "일부 완료",
    "error": "오류",
    "invalid": "입력 확인",
    "cancelled": "취소",
}


def display_value(row: ResultReviewRow, key: str) -> str:
    if key == "case_ordinal":
        return str(row.case_ordinal)
    if key == "status":
        status = _STATUS_DISPLAY.get(row.status, row.status)
        return f"{status} · 오래됨 (재실행 필요)" if row.freshness == "stale" else status
    if key in {"cooling_capacity", "heating_capacity"}:
        return _display_source(getattr(row, key))
    if key == "specification_summary":
        return row.specification_summary
    if key in {"eer", "cop"}:
        return _display_metric(getattr(row, key))
    if key in {
        "cooling_frequency",
        "heating_frequency",
        "refrigerant_quantity",
    }:
        return _display_target(getattr(row, key))
    raise KeyError(f"unknown Result Review display key: {key}")


def tooltip_value(row: ResultReviewRow, key: str) -> str:
    if key == "specification_summary":
        return row.specification_summary
    if key == "status":
        details = []
        if row.message:
            details.append(row.message)
        if row.stale_reason:
            details.append(f"재실행 필요: {row.stale_reason}")
        details.extend(
            " / ".join(part for part in (item.reason_code, item.message) if part)
            for item in row.issues
            if item.owner not in {"row", "freshness"}
        )
        return "\n".join(details)
    if key in {
        "eer",
        "cop",
        "cooling_frequency",
        "heating_frequency",
        "refrigerant_quantity",
    }:
        return _outcome_tooltip(getattr(row, key))
    return ""


def _outcome_tooltip(
    outcome: TargetOutcome | DerivedMetricOutcome | None,
) -> str:
    if outcome is None or outcome.status == "available":
        return ""
    return " / ".join(
        part for part in (outcome.reason_code, outcome.message) if part
    )


def _display_source(value) -> str:  # noqa: ANN001
    return _display_general(value.raw_value) if value.available else UNAVAILABLE_DISPLAY


def _display_target(outcome) -> str:  # noqa: ANN001
    if outcome is None or outcome.status != "available":
        return UNAVAILABLE_DISPLAY
    return _display_general(outcome.raw_value)


def _display_metric(outcome) -> str:  # noqa: ANN001
    if outcome is None or outcome.status != "available" or outcome.raw_value is None:
        return UNAVAILABLE_DISPLAY
    return f"{float(outcome.raw_value):.2f}"


def _display_general(value: object | None) -> str:
    if value is None:
        return UNAVAILABLE_DISPLAY
    if isinstance(value, (int, float)):
        number = float(value)
        if not isfinite(number):
            return UNAVAILABLE_DISPLAY
        return format(number, ".15g")
    text = str(value)
    return text if text else UNAVAILABLE_DISPLAY
