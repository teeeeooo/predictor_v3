"""Focused tests for shared result-formatting helpers (276).

Pure helper extraction regression guard. No Tk instances.
"""

from __future__ import annotations

import pytest

from apps.calculator.ui.sections.result_formatting import (
    bin_details,
    kwh_value,
    metric_value,
)


# ---------------------------------------------------------------------------
# bin_details
# ---------------------------------------------------------------------------


def test_bin_details_returns_list_of_dicts() -> None:
    result = {"bin_details": [{"a": 1}, {"b": 2}]}
    assert bin_details(result) == [{"a": 1}, {"b": 2}]


def test_bin_details_returns_empty_when_missing() -> None:
    assert bin_details({}) == []


def test_bin_details_returns_empty_when_none() -> None:
    assert bin_details({"bin_details": None}) == []


def test_bin_details_skips_non_mapping_items() -> None:
    result = {"bin_details": [{"a": 1}, "bad", {"b": 2}]}
    assert bin_details(result) == [{"a": 1}, {"b": 2}]


# ---------------------------------------------------------------------------
# metric_value
# ---------------------------------------------------------------------------


def test_metric_value_formats_three_decimals() -> None:
    assert metric_value({"cspf": 3.14159}, "cspf") == "3.142"


def test_metric_value_returns_dash_when_missing() -> None:
    assert metric_value({}, "cspf") == "-"


def test_metric_value_zero() -> None:
    assert metric_value({"cspf": 0}, "cspf") == "0.000"


# ---------------------------------------------------------------------------
# kwh_value
# ---------------------------------------------------------------------------


def test_kwh_value_formats_one_decimal() -> None:
    assert kwh_value({"kwh": 123.456}, ("kwh",)) == "123.5"


def test_kwh_value_first_alias_hit() -> None:
    assert kwh_value({"a": 10, "b": 20}, ("b", "a")) == "20.0"


def test_kwh_value_returns_dash_when_missing() -> None:
    assert kwh_value({}, ("kwh",)) == "-"
