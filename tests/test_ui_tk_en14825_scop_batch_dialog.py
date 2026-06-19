"""Focused tests for the EN14825 SCOP dynamic batch dialog profile."""

from __future__ import annotations

import pytest

from apps.calculator.ui.batch_dialogs.profiles.en14825_scop import (
    En14825ScopBatchSection,
)
from apps.calculator.ui.batch_dialogs.profiles.en14825_scop_dialog import (
    En14825ScopBatchDialog,
)
from apps.calculator.ui.en14825.scop_adapter import ScopAdapter
from apps.calculator.ui.en14825.scop_batch import build_en14825_scop_batch_spec
from apps.calculator.ui.en14825.scop_batch_session import (
    En14825ScopBatchActiveConditions,
    En14825ScopBatchSessionState,
    En14825ScopBatchSnapshot,
)


AVERAGE_CASE = {
    "p_design_h": "3000",
    "a_capacity": "3600",
    "a_power": "900",
    "b_capacity": "2650",
    "b_power": "576",
    "c_capacity": "1700",
    "c_power": "315",
    "d_capacity": "1200",
    "d_power": "194",
    "tol_capacity": "800",
    "tol_power": "400",
    "tbiv_capacity": "2650",
    "tbiv_power": "576",
}


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


def _set_conditions(section, climate: str, tbiv: str, tol: str) -> None:
    section._vars["climate"].set(climate)
    section._vars["tbiv_temp_c"].set(tbiv)
    section._vars["tol_temp_c"].set(tol)


def test_scop_session_store_excludes_results_and_projects_visible_keys() -> None:
    active = En14825ScopBatchActiveConditions("average", -10.0, -11.0)
    state = En14825ScopBatchSessionState(
        active,
        ({**AVERAGE_CASE, "scop": "4.00", "qh_kwh": "1000"},),
    )
    spec = build_en14825_scop_batch_spec("warmer", 2.0, -11.0)

    snapshot = state.snapshot({"climate": "average"})
    visible = state.visible_cases(spec)

    assert "scop" not in snapshot.cases[0]
    assert "qh_kwh" not in snapshot.cases[0]
    assert snapshot.cases[0]["a_capacity"] == "3600"
    assert visible[0]["b_capacity"] == "2650"
    assert "a_capacity" not in visible[0]


def test_scop_dialog_initial_matrix_uses_active_not_invalid_draft(tk_root) -> None:
    snapshot = En14825ScopBatchSnapshot(
        common_values={
            "climate": "warmer",
            "tbiv_temp_c": "bad",
            "tol_temp_c": "-11",
        },
        active_conditions=En14825ScopBatchActiveConditions("average", -10.0, -11.0),
        cases=(AVERAGE_CASE,),
    )
    dialog = En14825ScopBatchDialog(tk_root, initial_snapshot=snapshot)
    section = dialog.section
    assert section is not None

    assert tuple(point.key for point in section.table.spec.measurement_points) == (
        "p_design_h", "A", "B", "C", "D", "TOL", "Tbiv"
    )
    assert section._vars["climate"].get() == "warmer"
    assert section._vars["tbiv_temp_c"].get() == "bad"
    assert section.status_var.get() == "Condition inputs invalid"
    dialog.close()


def test_scop_draft_changes_do_not_rebuild_until_apply(tk_root) -> None:
    dialog = En14825ScopBatchDialog(tk_root)
    section = dialog.section
    assert section is not None
    original_table = section.table

    _set_conditions(section, "warmer", "2", "-11")

    assert section.table is original_table
    assert section._session.active_conditions.climate == "average"
    assert section.status_var.get() == "Conditions changed - apply to update matrix"
    dialog.close()


def test_scop_apply_rebuilds_and_preserves_hidden_inputs_round_trip(tk_root) -> None:
    dialog = En14825ScopBatchDialog(tk_root)
    section = dialog.section
    assert section is not None
    section.table.restore_snapshot([AVERAGE_CASE])
    original_table = section.table

    _set_conditions(section, "warmer", "2", "-11")
    section._apply_conditions()

    assert section.table is not original_table
    assert tuple(point.key for point in section.table.spec.measurement_points) == (
        "p_design_h", "B", "C", "D"
    )
    assert section.table.cases[0]["b_capacity"] == "2650"
    assert "a_capacity" not in section.table.cases[0]
    assert section.table.spec.is_not_applicable((1, 2))

    _set_conditions(section, "average", "-10", "-11")
    section._apply_conditions()

    assert section.table.cases[0]["a_capacity"] == "3600"
    assert section.table.cases[0]["tol_capacity"] == "800"
    assert section.table.cases[0]["tbiv_capacity"] == "2650"
    dialog.close()


def test_scop_invalid_apply_keeps_active_table_and_store(tk_root) -> None:
    dialog = En14825ScopBatchDialog(tk_root)
    section = dialog.section
    assert section is not None
    section.table.restore_snapshot([AVERAGE_CASE])
    original_table = section.table
    original_active = section._session.active_conditions

    _set_conditions(section, "warmer", "bad", "-11")
    section._apply_conditions()

    assert section.table is original_table
    assert section._session.active_conditions == original_active
    assert section.table.cases[0]["a_capacity"] == "3600"
    assert section.status_var.get() == "Condition inputs invalid"
    dialog.close()


def test_scop_contract_failure_keeps_active_table(tk_root, monkeypatch) -> None:
    adapter = ScopAdapter()
    section = En14825ScopBatchSection(tk_root, adapter=adapter)
    original_table = section.table
    original_active = section._session.active_conditions
    _set_conditions(section, "warmer", "2", "-11")
    monkeypatch.setattr(
        adapter,
        "resolve_point_availability",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(ValueError("contract")),
    )

    section._apply_conditions()

    assert section.table is original_table
    assert section._session.active_conditions == original_active
    assert section.status_var.get() == "Condition contract unavailable"
    section.dispose()


def test_scop_rows_keep_pending_and_error_states(tk_root) -> None:
    dialog = En14825ScopBatchDialog(tk_root)
    section = dialog.section
    assert section is not None

    section.table.restore_snapshot([{}])
    section._auto_calc.flush_now()
    assert section.status_var.get() == "0 valid / 1 pending"

    section.table.restore_snapshot([{"p_design_h": "3000"}])
    section._auto_calc.flush_now()
    assert section.status_var.get() == "0 valid / 1 pending"

    section.table.restore_snapshot([{**AVERAGE_CASE, "a_capacity": "bad"}])
    section._auto_calc.flush_now()
    assert section.status_var.get() == "0 valid / 0 pending / 1 invalid"
    dialog.close()


def test_scop_add_remove_syncs_case_store(tk_root) -> None:
    dialog = En14825ScopBatchDialog(tk_root)
    section = dialog.section
    assert section is not None

    section._add_case()
    assert len(section.table.cases) == section._session.case_count == 2

    section._remove_case()
    section._remove_case()
    assert len(section.table.cases) == section._session.case_count == 1
    dialog.close()


def test_scop_close_reopen_preserves_invalid_draft_active_and_hidden_store(tk_root) -> None:
    closed: list[En14825ScopBatchSnapshot] = []
    dialog = En14825ScopBatchDialog(tk_root, on_close=closed.append)
    section = dialog.section
    assert section is not None
    section.table.restore_snapshot([AVERAGE_CASE])
    _set_conditions(section, "warmer", "bad", "-11")
    dialog.close()

    saved = closed[0]
    assert saved.common_values["tbiv_temp_c"] == "bad"
    assert saved.active_conditions.climate == "average"
    assert saved.cases[0]["a_capacity"] == "3600"
    assert "scop" not in saved.cases[0]

    reopened = En14825ScopBatchDialog(tk_root, initial_snapshot=saved)
    reopened_section = reopened.section
    assert reopened_section is not None
    assert reopened_section._vars["tbiv_temp_c"].get() == "bad"
    assert reopened_section._session.active_conditions.climate == "average"
    assert "A" in tuple(point.key for point in reopened_section.table.spec.measurement_points)
    reopened.close()


def test_scop_actions_and_export_surface_use_visible_table(tk_root) -> None:
    dialog = En14825ScopBatchDialog(tk_root)
    section = dialog.section
    assert section is not None
    _set_conditions(section, "warmer", "2", "-11")
    section._apply_conditions()
    button_texts = {
        child.cget("text")
        for frame in section._frame.winfo_children()
        for child in frame.winfo_children()
        if child.winfo_class() == "TButton"
    }
    headers, _rows = section.table.table_export_data()

    assert {"Apply Conditions", "Add Case", "Remove Case", "Copy All", "Export CSV"} <= button_texts
    assert any(header.startswith("B (") for header in headers)
    assert not any(header.startswith("A (") for header in headers)
    dialog.close()
