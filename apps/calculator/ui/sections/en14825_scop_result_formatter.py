"""SCOP section result summary formatting helpers."""

from __future__ import annotations

from apps.calculator.ui.en14825 import ScopResultSummary
from apps.calculator.ui.result_models import ResultSummary


STATUS_MAPPINGS = {
    "idle": "대기 중",
    "complete": "자동 계산 완료",
    "invalid_design_load": "설계 난방 부하 오류 (0 초과 필요)",
    "invalid_t_design": "설계 온도 오류 (16°C 불가)",
    "invalid_climate": "기후 선택 오류",
    "invalid_temp_override": "TOL/Tbiv 범위 오류 (TOL <= Tbiv 필요)",
    "input_incomplete": "입력 대기 중 (Declared 또는 Tested 데이터 입력 필요)",
    "declared_error": "Declared 계산 오류",
    "tested_error": "Tested 계산 오류",
}


def format_scop_result_summary(summary: ScopResultSummary, climate: str) -> ResultSummary:
    """Convert a SCOP result summary into the section result panel model."""
    fields = (
        ("기후 (Climate)", climate.capitalize()),
        ("Declared SCOP", _format_optional(summary.declared_scop, ".2f")),
        ("Tested SCOP", _format_optional(summary.tested_scop, ".2f")),
        ("SCOP %", _format_optional(summary.scop_percent, ".1f", suffix="%")),
        ("Declared QH [kWh]", _format_optional(summary.declared_qh_kwh, ".1f")),
        ("Tested QH [kWh]", _format_optional(summary.tested_qh_kwh, ".1f")),
        ("Declared Total [kWh]", _format_optional(summary.declared_total_kwh, ".1f")),
        ("Tested Total [kWh]", _format_optional(summary.tested_total_kwh, ".1f")),
    )
    return ResultSummary(
        title=f"EN14825 SCOP - {climate.capitalize()}",
        fields=fields,
        status=STATUS_MAPPINGS.get(summary.status_code, "계산 완료"),
    )


def format_scop_compact_rows(summary: ScopResultSummary) -> tuple[tuple[str, tuple[tuple[str, str], ...]], ...]:
    """Return compact Declared/Tested rows for the section-local result surface."""
    return (
        (
            "Declared",
            (
                ("SCOP", _format_optional(summary.declared_scop, ".2f")),
                ("QH [kWh]", _format_optional(summary.declared_qh_kwh, ".1f")),
                ("Total [kWh]", _format_optional(summary.declared_total_kwh, ".1f")),
            ),
        ),
        (
            "Tested",
            (
                ("SCOP", _format_optional(summary.tested_scop, ".2f")),
                ("QH [kWh]", _format_optional(summary.tested_qh_kwh, ".1f")),
                ("Total [kWh]", _format_optional(summary.tested_total_kwh, ".1f")),
                ("SCOP %", _format_optional(summary.scop_percent, ".1f", suffix="%")),
            ),
        ),
    )


def format_scop_status(summary: ScopResultSummary) -> str:
    """Return the user-facing status text for a SCOP result summary."""
    return STATUS_MAPPINGS.get(summary.status_code, "계산 완료")


def format_scop_climate_error_summary(climate: str, message: str) -> ResultSummary:
    """Build a climate-local error summary for invalid climate configuration."""
    return ResultSummary(
        title=f"{climate.upper()} SCOP 결과",
        fields=(("Climate", climate.capitalize()),),
        status=f"기류/설정 오류: {message}",
    )


def _format_optional(value: float | None, spec: str, *, suffix: str = "") -> str:
    if value is None:
        return "-"
    return f"{value:{spec}}{suffix}"
