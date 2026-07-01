"""Focused KOREA detail-view contract tests."""

from __future__ import annotations

from apps.calculator.application.korea import KoreaCspfUseCase, KoreaHspfUseCase
from tests.test_calculator_korea_cspf_usecase import KOREA_CSPF_SAMPLE_VALUES
from tests.test_calculator_korea_hspf_usecase import KOREA_HSPF_SAMPLE_VALUES


def test_korea_cspf_detail_uses_official_bin_rows_not_guide_fields():
    result = KoreaCspfUseCase().calculate(KOREA_CSPF_SAMPLE_VALUES)

    assert result.is_ok
    assert result.detail_rows
    assert result.detail_summary == result.summary_fields
    assert not {"current_tc", "recommended_tc"} & set(result.detail_rows[0])


def test_korea_hspf_detail_uses_official_bin_rows_not_guide_fields():
    result = KoreaHspfUseCase().calculate(KOREA_HSPF_SAMPLE_VALUES)

    assert result.is_ok
    assert result.detail_rows
    assert result.detail_summary == result.summary_fields
    assert not {"current_tc", "recommended_tc"} & set(result.detail_rows[0])
