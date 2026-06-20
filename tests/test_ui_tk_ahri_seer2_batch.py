"""Focused headless and Tk tests for AHRI SEER2 batch."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from apps.calculator.ui.ahri.seer2_batch import (
    AHRI_SEER2_BATCH_SPEC,
    AhriSeer2BatchCommonInputs,
    AhriSeer2BatchHandler,
)
from apps.calculator.ui.batch.matrix_models import (
    MatrixCellKind,
    MatrixPhysicalRowType,
)
from apps.calculator.ui.batch.models import BatchRowState
from apps.calculator.ui.batch_dialogs.profiles.ahri_seer2 import (
    AhriSeer2BatchDialog,
    AhriSeer2BatchSnapshot,
)
from apps.calculator.ui.layout_constants import (
    BATCH_MATRIX_POINT_WIDTH_CHARS,
    BATCH_MATRIX_RESULT_PRIMARY_WIDTH_CHARS,
)


VALID_CASE = {
    "capacity_A_Full": "36000",
    "power_A_Full": "3000",
    "capacity_B_Full": "30000",
    "power_B_Full": "2200",
    "capacity_B_Low": "18000",
    "power_B_Low": "1200",
    "capacity_E_Int": "24000",
    "power_E_Int": "1700",
    "capacity_F_Low": "12000",
    "power_F_Low": "900",
}


class FakeSeer2Adapter:
    def __init__(self) -> None:
        self.calls: list[tuple[dict[str, str], str]] = []
        self.raise_error = False

    def calculate(self, text_values, *, system_type):
        self.calls.append((dict(text_values), system_type))
        if self.raise_error:
            raise ValueError("adapter failure")
        return SimpleNamespace(seer2=13.677)


def test_seer2_batch_spec_has_exact_two_row_matrix_contract() -> None:
    spec = AHRI_SEER2_BATCH_SPEC

    assert spec.profile_key == "ahri_seer2"
    assert spec.physical_rows == (
        MatrixPhysicalRowType.CAPACITY,
        MatrixPhysicalRowType.POWER,
    )
    assert tuple(point.key for point in spec.measurement_points) == (
        "A_Full",
        "B_Full",
        "B_Low",
        "E_Int",
        "F_Low",
    )
    assert tuple(point.label for point in spec.measurement_points) == (
        "A_Full",
        "B_Full",
        "B_Low",
        "E_Int",
        "F_Low",
    )
    assert {point.width_chars for point in spec.measurement_points} == {
        BATCH_MATRIX_POINT_WIDTH_CHARS
    }
    assert spec.result_metrics[0][2] == BATCH_MATRIX_RESULT_PRIMARY_WIDTH_CHARS
    assert spec.input_keys == tuple(VALID_CASE)
    assert spec.result_keys == ("seer2",)
    assert spec.resolve_cell((0, 2)).input_key == "capacity_A_Full"
    assert spec.resolve_cell((1, 2)).input_key == "power_A_Full"
    assert spec.resolve_cell((0, 7)).kind is MatrixCellKind.RESULT
    assert spec.resolve_cell((1, 7)).kind is MatrixCellKind.BLANK_READ_ONLY


def test_seer2_batch_handler_maps_type_and_returns_seer2_only() -> None:
    adapter = FakeSeer2Adapter()
    handler = AhriSeer2BatchHandler(
        AhriSeer2BatchCommonInputs(system_type="AC"),
        adapter=adapter,
    )

    result = handler.calculate_row(VALID_CASE)

    assert result.state is BatchRowState.OK
    assert result.values == {"seer2": "13.677"}
    assert adapter.calls == [(VALID_CASE, "AC")]


def test_seer2_batch_handler_blanks_incomplete_and_invalid_results() -> None:
    adapter = FakeSeer2Adapter()
    handler = AhriSeer2BatchHandler(
        AhriSeer2BatchCommonInputs(system_type="HP"),
        adapter=adapter,
    )

    blank = handler.calculate_row({})
    partial = handler.calculate_row({"capacity_A_Full": "36000"})
    adapter.raise_error = True
    invalid = handler.calculate_row(VALID_CASE)

    assert blank.state is BatchRowState.PENDING
    assert partial.state is BatchRowState.PENDING
    assert invalid.state is BatchRowState.ERROR
    assert blank.values == partial.values == invalid.values == {"seer2": ""}
    assert len(adapter.calls) == 1


def test_seer2_batch_handler_runs_existing_core_adapter() -> None:
    handler = AhriSeer2BatchHandler(
        AhriSeer2BatchCommonInputs(system_type="HP")
    )

    result = handler.calculate_row(VALID_CASE)

    assert result.state is BatchRowState.OK
    assert float(result.values["seer2"]) > 0.0


@pytest.fixture
def tk_root():
    tk = pytest.importorskip("tkinter")
    try:
        root = tk.Tk()
    except tk.TclError as exc:
        pytest.skip(f"Tk not available: {exc}")
    root.withdraw()
    try:
        yield root
    finally:
        root.destroy()


def test_seer2_batch_dialog_autocalculates_and_reuses_actions(tk_root) -> None:
    dialog = AhriSeer2BatchDialog(tk_root)
    section = dialog.section
    assert section is not None

    section.table.restore_snapshot([VALID_CASE])
    section._auto_calc.flush_now()

    assert section.table.row_count() == 2
    assert float(section.table.cases[0]["seer2"]) > 0.0
    assert section.table.text_at_position((1, 7)) == ""
    headers, _rows = section.table.table_export_data()
    assert headers == (
        "Case",
        "Row Type",
        "A_Full",
        "B_Full",
        "B_Low",
        "E_Int",
        "F_Low",
        "SEER2",
    )
    button_texts = {
        child.cget("text")
        for frame in section._frame.winfo_children()
        for child in frame.winfo_children()
        if child.winfo_class() == "TButton"
    }
    assert {"Add Case", "Remove Case", "Copy All", "Export CSV"} <= button_texts
    dialog.close()


def test_seer2_batch_parent_prevents_duplicates_and_restores_snapshot(tk_root) -> None:
    from apps.calculator.ui.sections.ahri_seer2_section import AhriSeer2Section

    section = AhriSeer2Section(tk_root)
    section._batch_snapshot = AhriSeer2BatchSnapshot(
        {"type": "AC"},
        (VALID_CASE,),
    )

    section.batch_button.invoke()
    dialog = section._batch_dialog
    assert dialog is not None and dialog.section is not None
    section.batch_button.invoke()
    assert section._batch_dialog is dialog
    assert dialog.section.type_var.get() == "AC"
    assert float(dialog.section.table.cases[0]["seer2"]) > 0.0

    dialog.section.table.set_positions_batch({(0, 2): "37000"})
    dialog.close()

    assert section._batch_dialog is None
    assert section._batch_snapshot is not None
    assert section._batch_snapshot.common_values == {"type": "AC"}
    assert section._batch_snapshot.cases[0]["capacity_A_Full"] == "37000"
    assert "seer2" not in section._batch_snapshot.cases[0]

    section.batch_button.invoke()
    reopened = section._batch_dialog
    assert reopened is not None and reopened.section is not None
    assert reopened.section.type_var.get() == "AC"
    assert reopened.section.table.cases[0]["capacity_A_Full"] == "37000"
    assert float(reopened.section.table.cases[0]["seer2"]) > 0.0
    reopened.close()
