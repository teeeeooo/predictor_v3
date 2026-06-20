"""Focused headless and Tk tests for the dynamic AHRI HSPF2 batch."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from apps.calculator.ui.ahri.hspf2_batch import (
    AhriHspf2BatchActiveOptions,
    AhriHspf2BatchCommonInputs,
    AhriHspf2BatchHandler,
    build_ahri_hspf2_batch_spec,
)
from apps.calculator.ui.ahri.hspf2_batch_session import (
    AhriHspf2BatchSessionState,
    AhriHspf2BatchSnapshot,
)
from apps.calculator.ui.ahri.hspf2_mock_data import HSPF2_DEV_SAMPLE_VALUES
from apps.calculator.ui.batch.matrix_models import MatrixCellKind, MatrixPhysicalRowType
from apps.calculator.ui.batch.models import BatchRowState


VALID_CASE = dict(HSPF2_DEV_SAMPLE_VALUES)
COMMON_NUMERIC = {
    "cd": "0.25",
    "defrost_credit": "1.0",
    "cut_out_c": "-40.0",
    "cut_in_c": "-40.0",
}


class FakeHspf2Adapter:
    def __init__(self) -> None:
        self.calls = []
        self.raise_error = False

    def calculate(self, values, *, options):
        self.calls.append((dict(values), options))
        if self.raise_error:
            raise ValueError("adapter failure")
        return SimpleNamespace(
            hspf2=9.876,
            h12_source="not provided",
            h22_source="calculated",
            h42_source="measured",
        )


def _common(active=AhriHspf2BatchActiveOptions()):
    return AhriHspf2BatchCommonInputs(
        active=active,
        h1n_h32_same_hz=False,
        min_spd=True,
        numeric_values=COMMON_NUMERIC,
    )


def test_hspf2_batch_spec_has_two_rows_optional_roles_and_results() -> None:
    spec = build_ahri_hspf2_batch_spec(AhriHspf2BatchActiveOptions())

    assert spec.physical_rows == (
        MatrixPhysicalRowType.CAPACITY,
        MatrixPhysicalRowType.POWER,
    )
    assert tuple(point.key for point in spec.measurement_points) == (
        "A2", "H01", "H11", "H1N", "H2Int", "H32", "H42", "H12", "H22",
    )
    assert tuple(point.label for point in spec.measurement_points) == (
        "A2", "H01 (16.7°C)", "H11 (8.3°C)", "H1N (8.3°C)",
        "H2Int (1.7°C)", "H32 (-8.3°C)", "H42 (-15.0°C)",
        "H12 (8.3°C)", "H22 (1.7°C)",
    )
    assert spec.result_keys == ("hspf2", "h12_source", "h22_source", "h42_source")
    assert spec.resolve_cell((0, 2)).input_key == "a2_capacity"
    assert spec.resolve_cell((1, 2)).kind is MatrixCellKind.NOT_APPLICABLE
    assert spec.resolve_cell((0, 8)).input_key == "capacity_H42"
    assert spec.resolve_cell((0, 9)).kind is MatrixCellKind.NOT_APPLICABLE
    assert spec.resolve_cell((0, 10)).kind is MatrixCellKind.NOT_APPLICABLE
    assert spec.resolve_cell((0, 11)).kind is MatrixCellKind.RESULT
    assert spec.resolve_cell((1, 14)).kind is MatrixCellKind.BLANK_READ_ONLY


def test_hspf2_batch_handler_omits_disabled_points_and_maps_sources() -> None:
    adapter = FakeHspf2Adapter()
    handler = AhriHspf2BatchHandler(_common(), adapter=adapter)

    result = handler.calculate_row(VALID_CASE)

    assert result.state is BatchRowState.OK
    assert result.values == {
        "hspf2": "9.876",
        "h12_source": "not provided",
        "h22_source": "calculated",
        "h42_source": "measured",
    }
    values, options = adapter.calls[0]
    assert "a2_power" not in values
    assert "capacity_H12" not in values and "capacity_H22" not in values
    assert options.measured_h42 is True
    assert options.measured_h12 is options.measured_h22 is False


def test_hspf2_batch_handler_blanks_incomplete_and_invalid_rows() -> None:
    adapter = FakeHspf2Adapter()
    handler = AhriHspf2BatchHandler(_common(), adapter=adapter)
    blank = handler.calculate_row({})
    adapter.raise_error = True
    invalid = handler.calculate_row(VALID_CASE)

    assert blank.state is BatchRowState.PENDING
    assert invalid.state is BatchRowState.ERROR
    assert set(blank.values.values()) == set(invalid.values.values()) == {""}


def test_hspf2_batch_session_preserves_hidden_superset_without_results() -> None:
    session = AhriHspf2BatchSessionState(
        AhriHspf2BatchActiveOptions(),
        ({**VALID_CASE, "a2_power": "legacy", "hspf2": "9.9", "h12_source": "measured"},),
    )
    default_spec = build_ahri_hspf2_batch_spec(session.active_options)
    assert "capacity_H12" not in session.visible_cases(default_spec)[0]

    session.set_active_options(
        AhriHspf2BatchActiveOptions(h12_enabled=True, h22_enabled=True)
    )
    enabled_spec = build_ahri_hspf2_batch_spec(session.active_options)
    assert session.visible_cases(enabled_spec)[0]["capacity_H12"] == (
        VALID_CASE["capacity_H12"]
    )
    snapshot = session.snapshot({"h12_enabled": "1"})
    assert "hspf2" not in snapshot.cases[0]
    assert "h12_source" not in snapshot.cases[0]
    assert "a2_power" not in snapshot.cases[0]


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


def test_hspf2_batch_dialog_rebuild_restores_hidden_input_and_actions(tk_root) -> None:
    from apps.calculator.ui.batch_dialogs.profiles.ahri_hspf2_dialog import (
        AhriHspf2BatchDialog,
    )

    snapshot = AhriHspf2BatchSnapshot(
        common_values={"h12_enabled": "0"},
        active_options=AhriHspf2BatchActiveOptions(),
        cases=(VALID_CASE,),
    )
    dialog = AhriHspf2BatchDialog(tk_root, initial_snapshot=snapshot)
    section = dialog.section
    assert section is not None
    assert section.table.text_at_position((0, 9)) == ""
    assert section.table.text_at_position((1, 2)) == ""
    section._vars["h12_enabled"].set("1")
    section._apply_options()
    assert section.table.cases[0]["capacity_H12"] == VALID_CASE["capacity_H12"]
    assert float(section.table.cases[0]["hspf2"]) > 0.0
    assert section.table.text_at_position((1, 11)) == ""
    headers, _rows = section.table.table_export_data()
    assert headers[-4:] == ("HSPF2", "H12", "H22", "H42")
    button_texts = {
        child.cget("text")
        for frame in section._frame.winfo_children()
        for child in frame.winfo_children()
        if child.winfo_class() == "TButton"
    }
    assert {"Add Case", "Remove Case", "Copy All", "Export CSV"} <= button_texts
    dialog.close()


def test_hspf2_batch_preserves_invalid_draft_with_last_valid_matrix(tk_root) -> None:
    from apps.calculator.ui.batch_dialogs.profiles.ahri_hspf2 import (
        AhriHspf2BatchSection,
    )

    section = AhriHspf2BatchSection(tk_root)
    section._vars["h12_enabled"].set("invalid")
    section._vars["cd"].set("bad")
    section._auto_calc.flush_now()
    snapshot = section.snapshot()

    assert snapshot.common_values["h12_enabled"] == "invalid"
    assert snapshot.common_values["cd"] == "bad"
    assert snapshot.active_options == AhriHspf2BatchActiveOptions()
    assert section.table.spec.resolve_cell((0, 9)).kind is MatrixCellKind.NOT_APPLICABLE
    assert all(not case.get(key) for case in section.table.cases for key in section.table.spec.result_keys)
    section.dispose()


def test_hspf2_batch_parent_prevents_duplicates_restores_and_destroys(tk_root) -> None:
    from apps.calculator.ui.sections.ahri_hspf2_section import AhriHspf2Section

    section = AhriHspf2Section(tk_root)
    section._batch_access.snapshot = AhriHspf2BatchSnapshot(
        common_values={"h12_enabled": "0"},
        active_options=AhriHspf2BatchActiveOptions(),
        cases=(VALID_CASE,),
    )
    section.batch_button.invoke()
    dialog = section._batch_access.dialog
    assert dialog is not None
    section.batch_button.invoke()
    assert section._batch_access.dialog is dialog
    assert dialog.section is not None
    dialog.section.table.set_positions_batch({(0, 2): "25000"})
    dialog.close()
    assert section._batch_access.dialog is None
    assert section._batch_access.snapshot.cases[0]["a2_capacity"] == "25000"

    section.batch_button.invoke()
    reopened = section._batch_access.dialog
    assert reopened is not None and reopened.section is not None
    assert reopened.section.table.cases[0]["a2_capacity"] == "25000"
    section._frame.destroy()
    assert section._batch_access.dialog is None
