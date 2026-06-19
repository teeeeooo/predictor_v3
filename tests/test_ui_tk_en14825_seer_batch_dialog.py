"""Focused tests for the EN14825 SEER batch dialog profile."""

from __future__ import annotations

import pytest

from apps.calculator.ui.batch_dialogs.profiles.en14825_seer import (
    En14825SeerBatchDialog,
    En14825SeerBatchSnapshot,
)
from apps.calculator.ui.sections.en14825_seer_section import En14825SeerSection


VALID_CASE = {
    "p_design_c": "3500",
    "a_capacity": "3500",
    "a_power": "900",
    "b_capacity": "3200",
    "b_power": "800",
    "c_capacity": "2800",
    "c_power": "680",
    "d_capacity": "2400",
    "d_power": "560",
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


def test_seer_batch_dialog_calculates_matrix_and_compact_status(tk_root) -> None:
    dialog = En14825SeerBatchDialog(tk_root)
    section = dialog.section
    assert section is not None

    section.table.restore_snapshot([VALID_CASE])
    section._auto_calc.flush_now()

    assert float(section.table.cases[0]["seer"]) > 0.0
    assert float(section.table.cases[0]["qc_kwh"]) > 0.0
    assert section.status_var.get() == "1 valid / 0 pending"
    button_texts = {
        child.cget("text")
        for frame in section._frame.winfo_children()
        for child in frame.winfo_children()
        if child.winfo_class() == "TButton"
    }
    assert {"Add Case", "Remove Case", "Copy All", "Export CSV"} <= button_texts
    dialog.close()


def test_seer_batch_dialog_preserves_common_inputs_and_cases(tk_root) -> None:
    common_values = {
        "t_design_c": "36",
        "cd": "0.3",
        "appliance_type": "cooling_only",
        "p_to_w": "10",
        "p_sb_w": "20",
        "p_ck_w": "30",
        "p_off_w": "40",
    }
    section = En14825SeerSection(tk_root)
    section._batch_snapshot = En14825SeerBatchSnapshot(
        common_values,
        (VALID_CASE,),
    )

    section.batch_button.invoke()
    dialog = section._batch_dialog
    assert dialog is not None and dialog.section is not None
    assert dialog.section.common_values() == common_values
    assert dialog.section.table.cases[0]["a_capacity"] == "3500"

    dialog.section._vars["cd"].set("0.4")
    dialog.section.table.set_positions_batch({(0, 2): "3600"})
    dialog.close()

    assert section._batch_dialog is None
    assert section._batch_snapshot is not None
    assert section._batch_snapshot.common_values["cd"] == "0.4"
    assert section._batch_snapshot.cases[0]["p_design_c"] == "3600"

    section.batch_button.invoke()
    reopened = section._batch_dialog
    assert reopened is not None and reopened.section is not None
    assert reopened.section._vars["cd"].get() == "0.4"
    assert reopened.section.table.cases[0]["p_design_c"] == "3600"
    reopened.close()


def test_seer_batch_dialog_common_inputs_are_dialog_owned(tk_root) -> None:
    section = En14825SeerSection(
        tk_root,
        common_input_values=lambda: {
            "p_to": "999",
            "p_sb": "999",
            "p_ck": "999",
            "p_off": "999",
        },
    )
    section._t_design_var.set("99")

    section.batch_button.invoke()
    dialog = section._batch_dialog
    assert dialog is not None and dialog.section is not None

    values = dialog.section.common_values()
    assert values["t_design_c"] != "99"
    assert values["p_to_w"] == "0"
    dialog.close()


def test_seer_batch_dialog_marks_invalid_common_inputs_compactly(tk_root) -> None:
    dialog = En14825SeerBatchDialog(tk_root)
    section = dialog.section
    assert section is not None
    section.table.restore_snapshot([VALID_CASE])
    section._vars["cd"].set("bad")

    section._auto_calc.flush_now()

    assert section.table.cases[0]["seer"] == ""
    assert section.table.cases[0]["qc_kwh"] == ""
    assert section.status_var.get() == "Common inputs invalid"
    dialog.close()
