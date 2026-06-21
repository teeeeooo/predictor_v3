"""Focused tests for ISO/India ISEER 2-point batch dialog and adapter."""

from __future__ import annotations

import tkinter as tk
import pytest

from apps.calculator.ui.batch.models import BatchRowState
from apps.calculator.ui.sections.iso_iseer_2point_section import IsoIseer2PointSection
from apps.calculator.ui.batch_dialogs.profiles.iso_iseer_2point import (
    IsoIseer2PointBatchDialog,
    IsoIseer2PointBatchHandler,
    ISO_ISEER_2POINT_MATRIX_SPEC,
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


def test_iso_iseer_2point_batch_dialog_opens_and_closes(tk_root):
    # Initialize section
    section = IsoIseer2PointSection(tk_root)
    
    # Click batch button to open dialog
    section.batch_button.invoke()
    dialog = section._batch_dialog
    
    assert dialog is not None
    assert dialog.window.winfo_exists()
    assert dialog.adapter.title == "ISO / India ISEER 2-point Batch"
    assert all(
        not case.get(key, "")
        for case in dialog.section.table.cases
        for key in ISO_ISEER_2POINT_MATRIX_SPEC.input_keys
    )
    
    # Re-click to focus
    section.batch_button.invoke()
    
    # Close dialog
    dialog.close()
    assert section._batch_dialog is None
    assert section._batch_snapshot is not None
    assert len(section._batch_snapshot) > 0


def test_iso_iseer_2point_batch_dialog_preserves_snapshot_on_reopen(tk_root):
    section = IsoIseer2PointSection(tk_root)
    
    # Set custom snapshot
    custom_snapshot = [
        {
            "full_capacity": "4000",
            "full_power": "1000",
            "half_capacity": "2000",
            "half_power": "450",
        }
    ]
    section._batch_snapshot = custom_snapshot
    
    # Open dialog
    section.batch_button.invoke()
    dialog = section._batch_dialog
    
    # Check if snapshot is restored in the table cases
    assert dialog.section.table.cases[0]["full_capacity"] == "4000"
    
    dialog.close()


def test_iso_iseer_2point_batch_handler_calculates_valid_cases():
    handler = IsoIseer2PointBatchHandler()
    
    # Valid row case
    row = {
        "full_capacity": "3600",
        "full_power": "900",
        "half_capacity": "1700",
        "half_power": "380",
    }
    result = handler.calculate_row(row)
    assert result.state is BatchRowState.OK
    assert result.values["iso_cspf"] == "5.188"
    assert result.values["iseer"] == "4.560"
    
    # Empty row case
    empty_result = handler.calculate_row({})
    assert empty_result.state is BatchRowState.PENDING
    assert empty_result.values["iso_cspf"] == ""
    
    # Invalid row case
    invalid_result = handler.calculate_row({
        "full_capacity": "not-a-number",
        "full_power": "900",
        "half_capacity": "1700",
        "half_power": "380",
    })
    assert invalid_result.state is BatchRowState.ERROR
    assert invalid_result.values["iso_cspf"] == ""


def test_iso_iseer_2point_batch_spec_properties():
    spec = ISO_ISEER_2POINT_MATRIX_SPEC
    assert spec.profile_key == "iso_iseer_2point"
    assert "iso_cspf" in spec.result_keys
    assert "iseer" in spec.result_keys
    assert len(spec.default_cases) == 5
    assert all(not case for case in spec.default_cases)
