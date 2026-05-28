"""Smoke tests for the Tkinter calculator foundation.

These tests confirm that:

- importing the Tkinter shell does not pull in PyQt5;
- the widget tree builds on a withdrawn Tk root in environments where
  Tk is usable (skip otherwise);
- Hong Kong CSPF / HSPF dispatch through the new resolver still
  matches the established smoke values (CSPF = 4.939, HSPF = 3.643).
"""

import sys

import pytest

from core.calculator_dispatcher import create_calculator_for_profile
from ui_tk.profile_resolver import resolve_profile_id
from ui_tk.calculator_app import centered_geometry


def test_pyqt5_not_imported_via_ui_tk_calculator_app():
    """Importing the Tkinter shell must not pull PyQt5 in."""
    for name in list(sys.modules):
        if name.startswith("PyQt5"):
            del sys.modules[name]

    import ui_tk.calculator_app  # noqa: F401 — imported for side effects

    assert not any(name.startswith("PyQt5") for name in sys.modules)


def test_hong_kong_cspf_smoke_via_resolver():
    profile_id = resolve_profile_id("Hong Kong", "CSPF")
    calc = create_calculator_for_profile(profile_id=profile_id)
    result = calc.calculate_cspf(
        {
            "35_full": {"capacity": 3600, "power": 900},
            "35_half": {"capacity": 1700, "power": 380},
        },
        declared_capacity=3500,
    )
    assert result["cspf"] == pytest.approx(4.939, abs=0.001)


def test_hong_kong_hspf_smoke_via_resolver():
    profile_id = resolve_profile_id("Hong Kong", "HSPF")
    calc = create_calculator_for_profile(profile_id=profile_id)
    result = calc.calculate_hspf(
        {
            "rated_heating_capacity": 6300,
            "7_full": {"capacity": 6300, "power": 1500},
            "7_half": {"capacity": 3200, "power": 800},
        }
    )
    assert result["hspf"] == pytest.approx(3.643, abs=0.001)


def test_centered_geometry_clamps_to_visible_screen_origin():
    assert centered_geometry(800, 600, 1600, 1000) == "800x600+400+200"
    assert centered_geometry(1600, 1200, 1000, 800) == "1600x1200+0+0"
    assert centered_geometry(0, 0, 1000, 800) == "1x1+499+399"


def test_calculator_tk_app_builds_widget_tree():
    """Build the full Tk widget tree on a withdrawn root. Skip if Tk
    cannot initialize (headless environment without a usable Tcl/Tk).
    """
    tk = pytest.importorskip("tkinter")
    try:
        root = tk.Tk()
    except tk.TclError as exc:
        pytest.skip(f"Tk not available: {exc}")
    try:
        root.withdraw()

        from ui_tk.calculator_app import CalculatorTkApp
        from ui_tk.tabs.iso16358_tab import Iso16358Tab

        app = CalculatorTkApp(root=root)
        root.update_idletasks()
        root.update()

        assert isinstance(app.iso_tab, Iso16358Tab)
        assert root.winfo_x() >= 0
        assert root.winfo_y() >= 0
        # Region selector defaults to "Hong Kong" and the tab exposes a
        # result panel that downstream sections push text into.
        assert app.iso_tab.result_panel is not None
    finally:
        root.destroy()
