"""Focused initial geometry tests for BatchMatrix dialog profiles."""

from __future__ import annotations

import tkinter as tk

import pytest

from apps.calculator.ui.batch_dialogs.profiles.ahri_hspf2_dialog import (
    AhriHspf2BatchDialog,
)
from apps.calculator.ui.batch_dialogs.profiles.ahri_seer2 import (
    AhriSeer2BatchDialog,
)
from apps.calculator.ui.batch_dialogs.profiles.en14825_scop_dialog import (
    En14825ScopBatchDialog,
)
from apps.calculator.ui.batch_dialogs.profiles.en14825_seer import (
    En14825SeerBatchDialog,
)
from apps.calculator.ui.window_geometry import (
    capped_window_size,
    parent_centered_content_geometry,
    parse_window_geometry,
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


@pytest.mark.parametrize(
    "dialog_type",
    (
        AhriHspf2BatchDialog,
        AhriSeer2BatchDialog,
        En14825SeerBatchDialog,
        En14825ScopBatchDialog,
    ),
)
def test_batch_dialog_initial_geometry_uses_profile_natural_size(
    tk_root,
    dialog_type,
) -> None:
    dialog = dialog_type(tk_root)
    shell = dialog._shell
    expected = parent_centered_content_geometry(
        tk_root.geometry(),
        shell._initial_preferred_size,
        dialog.window.winfo_screenwidth(),
        dialog.window.winfo_screenheight(),
        dialog.adapter.min_size,
    )

    assert shell._initial_preferred_size[0] >= shell._initial_requested_size[0]
    assert shell._initial_preferred_size[1] >= shell._initial_requested_size[1]
    assert shell._initial_preferred_size[0] == shell._initial_requested_size[0]
    assert parse_window_geometry(dialog.window.geometry())[:2] == (
        parse_window_geometry(expected)[:2]
    )
    dialog.close()


def test_hspf2_batch_fits_natural_matrix_width_when_below_screen_cap(tk_root) -> None:
    dialog = AhriHspf2BatchDialog(tk_root)
    natural_width, natural_height = dialog.section.table.preferred_content_size()
    fitted_width, _fitted_height = parse_window_geometry(dialog.window.geometry())[:2]
    capped_width, _capped_height = capped_window_size(
        natural_width,
        natural_height,
        dialog.window.winfo_screenwidth(),
        dialog.window.winfo_screenheight(),
    )

    assert dialog._shell._initial_preferred_size[0] >= natural_width
    assert dialog._shell._initial_requested_size[0] >= natural_width
    if capped_width == natural_width:
        assert fitted_width >= natural_width
    dialog.close()
