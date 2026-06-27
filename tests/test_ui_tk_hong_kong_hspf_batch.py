"""Focused tests for Hong Kong HSPF batch dialog and matrix handler."""

from __future__ import annotations

import pytest

from apps.calculator.ui.batch.controller import BatchMatrixCalculationController
from apps.calculator.ui.batch.matrix_models import (
    FULL_CAPACITY,
    FULL_POWER,
    HALF_CAPACITY,
    HALF_POWER,
    HONG_KONG_HSPF_MATRIX_SPEC,
    HSEC,
    HSPF,
    HSTL,
)
from apps.calculator.ui.batch.models import BatchRowState
from apps.calculator.ui.batch_dialogs.profiles.hong_kong_hspf import (
    HongKongHspfBatchHandler,
)
from apps.calculator.ui.layout_constants import BATCH_INPUT_BUTTON_TEXT
from apps.calculator.ui.sections.hong_kong_hspf_section import HongKongHspfSection
from tests.calculator_ui_sample_values import HONG_KONG_HSPF_SAMPLE_VALUES


class _HeadlessMatrixTable:
    """Headless stand-in for BatchMatrixTable."""

    def __init__(self, cases: list[dict[str, str]] | None = None) -> None:
        self.spec = HONG_KONG_HSPF_MATRIX_SPEC
        self.cases: list[dict[str, str]] = (
            [dict(c) for c in cases]
            if cases is not None
            else [dict(c) for c in self.spec.default_cases]
        )
        self._results: dict[int, dict[str, str]] = {}

    def set_result(self, logical_index: int, values: dict[str, str]) -> None:
        self._results[logical_index] = dict(values)
        if logical_index < len(self.cases):
            self.cases[logical_index].update(values)


@pytest.fixture
def tk_root():
    tk_module = pytest.importorskip("tkinter")
    try:
        root = tk_module.Tk()
    except tk_module.TclError as exc:
        pytest.skip(f"Tk not available: {exc}")
    root.withdraw()
    try:
        yield root
    finally:
        root.destroy()


def test_hong_kong_hspf_matrix_spec_contract() -> None:
    spec = HONG_KONG_HSPF_MATRIX_SPEC

    assert spec.profile_key == "hong_kong_hspf"
    assert spec.input_keys == (
        FULL_CAPACITY,
        FULL_POWER,
        HALF_CAPACITY,
        HALF_POWER,
    )
    assert spec.result_keys == (HSPF, HSTL, HSEC)
    assert len(spec.default_cases) == 5
    assert all(not case for case in spec.default_cases)


def test_hong_kong_hspf_handler_calculates_sample_row() -> None:
    handler = HongKongHspfBatchHandler("Hong Kong")

    result = handler.calculate_row(dict(HONG_KONG_HSPF_SAMPLE_VALUES))

    assert result.state is BatchRowState.OK
    assert result.values == {HSPF: "3.643", HSTL: "273.2", HSEC: "75.0"}


def test_hong_kong_hspf_handler_blank_and_invalid_rows() -> None:
    handler = HongKongHspfBatchHandler("Hong Kong")

    blank = handler.calculate_row({})
    assert blank.state is BatchRowState.PENDING
    assert blank.values == {HSPF: "", HSTL: "", HSEC: ""}

    invalid = handler.calculate_row(
        {
            FULL_CAPACITY: "bad",
            FULL_POWER: "1500",
            HALF_CAPACITY: "3200",
            HALF_POWER: "800",
        }
    )
    assert invalid.state is BatchRowState.ERROR
    assert invalid.values == {HSPF: "", HSTL: "", HSEC: ""}


def test_hong_kong_hspf_matrix_controller_calculates_cases() -> None:
    table = _HeadlessMatrixTable([dict(HONG_KONG_HSPF_SAMPLE_VALUES), {}, {}])
    controller = BatchMatrixCalculationController(
        table,
        HongKongHspfBatchHandler("Hong Kong"),
    )

    summary = controller.recalculate()

    assert summary.valid_rows == 1
    assert summary.blank_rows == 2
    assert summary.error_rows == 0
    assert table._results[0][HSPF] == "3.643"
    assert table._results[1][HSPF] == ""


def test_hong_kong_hspf_batch_dialog_opens_and_preserves_snapshot(tk_root) -> None:
    section = HongKongHspfSection(tk_root, "Hong Kong")

    assert section.batch_button.cget("text") == BATCH_INPUT_BUTTON_TEXT
    section.batch_button.invoke()
    dialog = section._batch_dialog

    assert dialog is not None
    assert dialog.window.winfo_exists()
    assert dialog.adapter.title == "HSPF Batch (Hong Kong)"
    assert dialog.section.table.spec.profile_key == "hong_kong_hspf"
    assert len(dialog.section.table.cases) == 5

    dialog.section.table.restore_snapshot([dict(HONG_KONG_HSPF_SAMPLE_VALUES), {}])
    assert dialog.snapshot()[0][FULL_CAPACITY] == "6300"

    dialog.close()
    tk_root.update_idletasks()

    assert section._batch_dialog is None
    assert section._batch_snapshot is not None

    section.batch_button.invoke()
    reopened = section._batch_dialog

    assert reopened is not None
    assert reopened is not dialog
    assert reopened.section.table.cases[0][FULL_CAPACITY] == "6300"
    assert reopened.section.table.cases[0][HALF_POWER] == "800"

    reopened.close()
    tk_root.update_idletasks()
