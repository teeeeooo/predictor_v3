"""Focused tests for SASO T3 batch dialog and adapter."""

from __future__ import annotations

import tkinter as tk
import pytest

from apps.calculator.ui.batch.models import BatchRowState
from apps.calculator.ui.sections.iso_saso_t3_section import IsoSasoT3Section
from apps.calculator.ui.batch_dialogs.profiles.saso_t3 import (
    SasoT3BatchDialog,
    SasoT3BatchHandler,
    SASO_T3_MATRIX_SPEC,
)


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


def test_saso_t3_batch_dialog_opens_and_closes(tk_root):
    # Initialize section
    section = IsoSasoT3Section(tk_root)
    
    # Click batch button to open dialog
    section.batch_button.invoke()
    dialog = section._batch_dialog
    
    assert dialog is not None
    assert dialog.window.winfo_exists()
    assert dialog.adapter.title == "SASO T3 Batch"
    
    # Re-click to focus
    section.batch_button.invoke()
    
    # Close dialog
    dialog.close()
    assert section._batch_dialog is None
    assert section._batch_snapshot is not None
    assert len(section._batch_snapshot) > 0


def test_saso_t3_batch_dialog_preserves_snapshot_on_reopen(tk_root):
    section = IsoSasoT3Section(tk_root)
    
    # Set custom snapshot
    custom_snapshot = [
        {
            "full_46_capacity": "4500",
            "full_46_power": "1400",
            "full_35_capacity": "5500",
            "full_35_power": "1400",
            "half_35_capacity": "2800",
            "half_35_power": "600",
        }
    ]
    section._batch_snapshot = custom_snapshot
    
    # Open dialog
    section.batch_button.invoke()
    dialog = section._batch_dialog
    
    # Check if snapshot is restored in the table cases
    assert dialog.section.table.cases[0]["full_46_capacity"] == "4500"
    
    dialog.close()


def test_saso_t3_batch_handler_calculates_cases():
    handler = SasoT3BatchHandler()
    
    # Valid required + optional row case
    row_with_opt = {
        "full_46_capacity": "5000",
        "full_46_power": "1500",
        "full_35_capacity": "6000",
        "full_35_power": "1500",
        "half_35_capacity": "3000",
        "half_35_power": "680",
        "min_35_capacity": "1200",
        "min_35_power": "300",
    }
    res_opt = handler.calculate_row(row_with_opt)
    assert res_opt.state is BatchRowState.OK
    assert res_opt.values["req_cspf"] == "4.166"
    assert res_opt.values["opt_cspf"] == "4.230"
    
    # Valid required only row case
    row_req_only = {
        "full_46_capacity": "5000",
        "full_46_power": "1500",
        "full_35_capacity": "6000",
        "full_35_power": "1500",
        "half_35_capacity": "3000",
        "half_35_power": "680",
    }
    res_req = handler.calculate_row(row_req_only)
    assert res_req.state is BatchRowState.OK
    assert res_req.values["req_cspf"] == "4.166"
    assert res_req.values["opt_cspf"] == ""
    
    # Partial optional inputs: capacity only
    res_partial_cap = handler.calculate_row({
        "full_46_capacity": "5000",
        "full_46_power": "1500",
        "full_35_capacity": "6000",
        "full_35_power": "1500",
        "half_35_capacity": "3000",
        "half_35_power": "680",
        "min_35_capacity": "1200",
    })
    assert res_partial_cap.state is BatchRowState.ERROR
    assert res_partial_cap.values["req_cspf"] == "4.166"
    assert res_partial_cap.values["opt_cspf"] == ""

    # Partial optional inputs: power only
    res_partial_pw = handler.calculate_row({
        "full_46_capacity": "5000",
        "full_46_power": "1500",
        "full_35_capacity": "6000",
        "full_35_power": "1500",
        "half_35_capacity": "3000",
        "half_35_power": "680",
        "min_35_power": "300",
    })
    assert res_partial_pw.state is BatchRowState.ERROR
    assert res_partial_pw.values["req_cspf"] == "4.166"
    assert res_partial_pw.values["opt_cspf"] == ""

    # Invalid optional inputs: non-positive value
    res_invalid_opt = handler.calculate_row({
        "full_46_capacity": "5000",
        "full_46_power": "1500",
        "full_35_capacity": "6000",
        "full_35_power": "1500",
        "half_35_capacity": "3000",
        "half_35_power": "680",
        "min_35_capacity": "1200",
        "min_35_power": "-300",
    })
    assert res_invalid_opt.state is BatchRowState.ERROR
    assert res_invalid_opt.values["req_cspf"] == "4.166"
    assert res_invalid_opt.values["opt_cspf"] == ""

    # Empty row case
    empty_result = handler.calculate_row({})
    assert empty_result.state is BatchRowState.PENDING
    assert empty_result.values["req_cspf"] == ""

    # Invalid required row case
    invalid_result = handler.calculate_row({
        "full_46_capacity": "not-a-number",
        "full_46_power": "1500",
        "full_35_capacity": "6000",
        "full_35_power": "1500",
        "half_35_capacity": "3000",
        "half_35_power": "680",
    })
    assert invalid_result.state is BatchRowState.ERROR
    assert invalid_result.values["req_cspf"] == ""


def test_saso_t3_batch_spec_properties():
    spec = SASO_T3_MATRIX_SPEC
    assert spec.profile_key == "saso_t3"
    assert "req_cspf" in spec.result_keys
    assert "opt_cspf" in spec.result_keys

    # Verify display order (4pt first, then 3pt)
    assert spec.result_keys.index("opt_cspf") < spec.result_keys.index("req_cspf")
    assert spec.result_keys.index("opt_cstl") < spec.result_keys.index("req_cstl")
    assert spec.result_keys.index("opt_csec") < spec.result_keys.index("req_csec")

    # Verify labels (no 'Req' should remain, they should be '3pt')
    labels = [label for key, label, width in spec.result_metrics]
    assert all("Req" not in label for label in labels)
    assert any("3pt" in label for label in labels)
    assert any("4pt" in label for label in labels)
