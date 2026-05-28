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
from ui_tk.calculator_app import (
    centered_geometry,
    initial_window_geometry,
    resolve_min_window_size,
)
from ui_tk.layout_constants import (
    APP_WINDOW_FALLBACK_MIN_HEIGHT,
    APP_WINDOW_FALLBACK_MIN_WIDTH,
    APP_WINDOW_MAX_HEIGHT_RATIO,
    APP_WINDOW_MAX_WIDTH_RATIO,
    APP_WINDOW_MIN_VISIBLE_HEIGHT,
    APP_WINDOW_MIN_VISIBLE_WIDTH,
    APP_WINDOW_PREFERRED_WIDTH_RATIO,
    APP_WINDOW_SCREEN_MARGIN_X_RATIO,
    APP_WINDOW_SCREEN_MARGIN_Y_RATIO,
)
from ui_tk.tabs.iso16358_tab import mousewheel_units


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


def test_initial_window_geometry_caps_to_screen_with_minimum_size():
    screen_width, screen_height = 1600, 1000
    max_width = min(
        screen_width - int(screen_width * APP_WINDOW_SCREEN_MARGIN_X_RATIO),
        int(screen_width * APP_WINDOW_MAX_WIDTH_RATIO),
    )
    preferred_width = min(max_width, int(screen_width * APP_WINDOW_PREFERRED_WIDTH_RATIO))
    max_height = min(
        screen_height - int(screen_height * APP_WINDOW_SCREEN_MARGIN_Y_RATIO),
        int(screen_height * APP_WINDOW_MAX_HEIGHT_RATIO),
    )
    normal_width, normal_height = 900, 700
    assert initial_window_geometry(900, 700, screen_width, screen_height) == (
        f"{normal_width}x{normal_height}+{(screen_width - normal_width) // 2}+"
        f"{(screen_height - normal_height) // 2}"
    )
    assert initial_window_geometry(2200, 1800, screen_width, screen_height) == (
        f"{preferred_width}x{max_height}+{(screen_width - preferred_width) // 2}+"
        f"{(screen_height - max_height) // 2}"
    )

    content_height = max_height - 1
    assert initial_window_geometry(
        100, 100, screen_width, screen_height, (normal_width, content_height)
    ) == (
        f"{normal_width}x{content_height}+{(screen_width - normal_width) // 2}+"
        f"{(screen_height - content_height) // 2}"
    )
    assert initial_window_geometry(
        100, 100, screen_width, screen_height, (max_width * 2, max_height * 2)
    ) == (
        f"{preferred_width}x{max_height}+{(screen_width - preferred_width) // 2}+"
        f"{(screen_height - max_height) // 2}"
    )

    small_screen_width, small_screen_height = 1000, 700
    assert initial_window_geometry(100, 100, small_screen_width, small_screen_height) == (
        "100x100+450+300"
    )
    assert resolve_min_window_size(small_screen_width, small_screen_height) == (
        APP_WINDOW_FALLBACK_MIN_WIDTH,
        APP_WINDOW_FALLBACK_MIN_HEIGHT,
    )


def test_mousewheel_units_handle_platform_deltas():
    class Event:
        def __init__(self, *, delta=0, num=None):
            self.delta = delta
            self.num = num

    assert mousewheel_units(Event(delta=1)) == -1
    assert mousewheel_units(Event(delta=-1)) == 1
    assert mousewheel_units(Event(delta=120)) == -1
    assert mousewheel_units(Event(delta=-120)) == 1
    assert mousewheel_units(Event(num=4)) == -1
    assert mousewheel_units(Event(num=5)) == 1
    assert mousewheel_units(Event()) == 0


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
        assert root.winfo_height() <= root.winfo_screenheight()
        # Region selector defaults to "Hong Kong" and the tab exposes a
        # result panel that downstream sections push text into.
        assert app.iso_tab.result_panel is not None
        preferred_width, preferred_height = app.iso_tab.preferred_initial_size()
        assert preferred_width >= app.iso_tab._scrollbar.winfo_reqwidth()
        assert preferred_height >= app.iso_tab._metric_notebook.winfo_reqheight()
        assert app.iso_tab._scrollbar.winfo_manager() == "pack"
        assert app.iso_tab._canvas.cget("yscrollcommand")
        assert app.iso_tab._contains_widget(app.iso_tab._region_combo)

        calls = []
        app.iso_tab._canvas.yview_scroll = lambda units, mode: calls.append((units, mode))
        inside_event = type("Event", (), {"widget": app.iso_tab._region_combo, "delta": -1})()
        outside = tk.Label(root)
        outside_event = type("Event", (), {"widget": outside, "delta": -1})()
        assert app.iso_tab._on_mousewheel(inside_event) == "break"
        assert calls == [(1, "units")]
        assert app.iso_tab._on_mousewheel(outside_event) == ""
        assert calls == [(1, "units")]
    finally:
        root.destroy()
