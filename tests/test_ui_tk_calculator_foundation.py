"""Smoke tests for the Tkinter calculator foundation.

These tests confirm that:

- importing the Tkinter shell does not pull in PyQt5;
- the widget tree builds on a withdrawn Tk root in environments where
  Tk is usable (skip otherwise);
- Hong Kong CSPF / HSPF dispatch through the new resolver still
  matches the established smoke values (CSPF = 4.939, HSPF = 3.643).
"""

import sys
import subprocess
import textwrap

import pytest

from core.calculator_dispatcher import create_calculator_for_profile
from ui_tk.profile_resolver import resolve_profile_id
from ui_tk.window_geometry import (
    apply_overflow_correction,
    centered_geometry,
    fit_window_to_preferred_content,
    grow_window_by_vertical_delta,
    initial_window_geometry,
    resolve_min_window_size,
)
from ui_tk.layout_constants import (
    APP_WINDOW_CONTENT_SAFETY_MARGIN_RATIO,
    APP_WINDOW_FALLBACK_MIN_HEIGHT,
    APP_WINDOW_FALLBACK_MIN_WIDTH,
    APP_WINDOW_MAX_HEIGHT_RATIO,
    APP_WINDOW_MAX_WIDTH_RATIO,
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


def test_initial_window_geometry_uses_content_size_with_screen_cap():
    screen_width, screen_height = 1600, 1000
    max_width = min(
        screen_width - int(screen_width * APP_WINDOW_SCREEN_MARGIN_X_RATIO),
        int(screen_width * APP_WINDOW_MAX_WIDTH_RATIO),
    )
    max_height = min(
        screen_height - int(screen_height * APP_WINDOW_SCREEN_MARGIN_Y_RATIO),
        int(screen_height * APP_WINDOW_MAX_HEIGHT_RATIO),
    )

    # Normal requested size passes through.
    assert initial_window_geometry(900, 700, screen_width, screen_height) == (
        "900x700+350+150"
    )

    # Oversized requested is capped to screen.
    assert initial_window_geometry(2200, 1800, screen_width, screen_height) == (
        f"{max_width}x{max_height}+{(screen_width - max_width) // 2}+"
        f"{(screen_height - max_height) // 2}"
    )

    # Preferred content size is respected.
    content_width, content_height = 850, 650
    assert initial_window_geometry(
        100, 100, screen_width, screen_height, (content_width, content_height)
    ) == (
        f"{content_width}x{content_height}+{(screen_width - content_width) // 2}+"
        f"{(screen_height - content_height) // 2}"
    )

    # Preferred content size exceeding screen cap is capped.
    assert initial_window_geometry(
        100, 100, screen_width, screen_height, (max_width * 2, max_height * 2)
    ) == (
        f"{max_width}x{max_height}+{(screen_width - max_width) // 2}+"
        f"{(screen_height - max_height) // 2}"
    )

    # Small requested size is not forced to a ratio minimum.
    small_screen_width, small_screen_height = 1000, 700
    assert initial_window_geometry(300, 250, small_screen_width, small_screen_height) == (
        "300x250+350+225"
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
    # macOS Tk can hang when a full app root is constructed after prior
    # same-process Tk roots; keep this app-shell smoke isolated.
    script = r"""
import sys
import tkinter as tk

try:
    root = tk.Tk()
except tk.TclError:
    raise SystemExit(77)

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
    assert app.iso_tab.result_panel is not None
    assert app.iso_tab.result_panel._text.get("1.0", "end-1c").strip() != ""
    preferred_width, preferred_height = app.iso_tab.preferred_initial_size()
    assert preferred_width >= app.iso_tab._scrollbar.winfo_reqwidth()
    assert preferred_height >= app.iso_tab._metric_notebook.winfo_reqheight()
    assert preferred_width < 800
    assert preferred_height < 600
    delta = app.iso_tab.vertical_overflow_delta()
    if delta <= 0:
        assert not app.iso_tab._scrollbar_visible
    assert app.iso_tab._canvas.cget("yscrollcommand")
    assert app.iso_tab._contains_widget(app.iso_tab._region_combo)

    calls = []
    app.iso_tab._canvas.yview_scroll = lambda units, mode: calls.append((units, mode))
    inside_event = type(
        "Event", (), {"widget": app.iso_tab._region_combo, "delta": -1}
    )()
    outside = tk.Label(root)
    outside_event = type("Event", (), {"widget": outside, "delta": -1})()
    assert app.iso_tab._on_mousewheel(inside_event) == "break"
    if delta > 0:
        assert calls == [(1, "units")]
    else:
        assert calls == []
    assert app.iso_tab._on_mousewheel(outside_event) == ""
    if delta > 0:
        assert calls == [(1, "units")]
    else:
        assert calls == []
finally:
    root.destroy()
"""
    completed = subprocess.run(
        [sys.executable, "-B", "-c", textwrap.dedent(script)],
        capture_output=True,
        text=True,
        timeout=10,
    )
    if completed.returncode == 77:
        pytest.skip("Tk not available")
    assert completed.returncode == 0, completed.stdout + completed.stderr


def test_scrollable_frame_hides_scrollbar_when_content_fits():
    tk = pytest.importorskip("tkinter")
    try:
        root = tk.Tk()
    except tk.TclError as exc:
        pytest.skip(f"Tk not available: {exc}")
    try:
        from ui_tk.scrollable_frame import ScrollableFrame

        sf = ScrollableFrame(root)
        sf.pack(fill="both", expand=True)
        root.geometry("800x600")
        root.update_idletasks()
        assert sf.vertical_overflow_delta() == 0
        assert not sf.scrollbar_visible

        calls = []
        sf.canvas.yview_scroll = lambda units, mode: calls.append((units, mode))
        internal = tk.Label(sf.content, text="internal")
        internal.pack()
        root.update_idletasks()
        event = type("Event", (), {"widget": internal, "delta": -1})()
        assert sf._on_mousewheel(event) == "break"
        assert calls == []
    finally:
        root.destroy()


def test_scrollable_frame_shows_scrollbar_when_content_overflows():
    tk = pytest.importorskip("tkinter")
    try:
        root = tk.Tk()
    except tk.TclError as exc:
        pytest.skip(f"Tk not available: {exc}")
    try:
        from ui_tk.scrollable_frame import ScrollableFrame

        sf = ScrollableFrame(root)
        sf.pack(fill="both", expand=True)
        tk.Label(sf.content, text="tall", height=50).pack()
        root.geometry("300x200")
        root.update_idletasks()
        assert sf.vertical_overflow_delta() > 0
        assert sf.scrollbar_visible

        calls = []
        sf.canvas.yview_scroll = lambda units, mode: calls.append((units, mode))
        event = type("Event", (), {"widget": sf.content, "delta": -1})()
        assert sf._on_mousewheel(event) == "break"
        assert calls == [(1, "units")]
    finally:
        root.destroy()


def test_scrollable_frame_vertical_overflow_delta_matches_bbox():
    tk = pytest.importorskip("tkinter")
    try:
        root = tk.Tk()
    except tk.TclError as exc:
        pytest.skip(f"Tk not available: {exc}")
    try:
        from ui_tk.scrollable_frame import ScrollableFrame

        sf = ScrollableFrame(root)
        sf.pack(fill="both", expand=True)
        root.geometry("400x300")
        root.update_idletasks()
        delta = sf.vertical_overflow_delta()
        assert delta >= 0
        bbox = sf.canvas.bbox("all")
        if bbox is not None:
            expected = max(0, (bbox[3] - bbox[1]) - sf.canvas.winfo_height())
            assert delta == expected
    finally:
        root.destroy()


def test_scrollable_frame_destroy_keeps_sibling_mousewheel_binding():
    tk = pytest.importorskip("tkinter")
    try:
        root = tk.Tk()
    except tk.TclError as exc:
        pytest.skip(f"Tk not available: {exc}")
    try:
        from ui_tk.scrollable_frame import ScrollableFrame

        first = ScrollableFrame(root)
        first.pack(fill="both", expand=True)
        second = ScrollableFrame(root)
        second.pack(fill="both", expand=True)
        target = tk.Label(second.content, text="target", height=50)
        target.pack()
        root.geometry("300x200")
        root.update_idletasks()

        calls = []
        second.canvas.yview_scroll = lambda units, mode: calls.append((units, mode))
        target.event_generate("<Button-5>")
        root.update()
        assert calls == [(1, "units")]

        first.destroy()
        root.update()
        target.event_generate("<Button-5>")
        root.update()
        assert calls == [(1, "units"), (1, "units")]
    finally:
        root.destroy()


def test_overflow_correction_grows_window_once():
    tk = pytest.importorskip("tkinter")
    try:
        root = tk.Tk()
    except tk.TclError as exc:
        pytest.skip(f"Tk not available: {exc}")
    try:
        from ui_tk.tabs.iso16358_tab import Iso16358Tab

        tab = Iso16358Tab(root)
        tab.pack(fill="both", expand=True)
        root.update_idletasks()
        delta = tab.vertical_overflow_delta()
        before = root.geometry()
        before_h = int(before.split("x")[1].split("+")[0])
        apply_overflow_correction(root, tab)
        after = root.geometry()
        after_h = int(after.split("x")[1].split("+")[0])
        if delta > 0:
            assert after_h >= before_h
        else:
            assert after_h == before_h
    finally:
        root.destroy()


def test_fit_window_to_preferred_content_applies_exact_fit():
    tk = pytest.importorskip("tkinter")
    try:
        root = tk.Tk()
    except tk.TclError as exc:
        pytest.skip(f"Tk not available: {exc}")
    try:
        root.geometry("300x250")
        root.update_idletasks()
        fit_window_to_preferred_content(root, (640, 480))
        root.update_idletasks()
        assert root.geometry() == initial_window_geometry(
            640,
            480,
            root.winfo_screenwidth(),
            root.winfo_screenheight(),
        )

        fit_window_to_preferred_content(root, (320, 260))
        root.update_idletasks()
        assert root.geometry() == initial_window_geometry(
            320,
            260,
            root.winfo_screenwidth(),
            root.winfo_screenheight(),
        )
    finally:
        root.destroy()


def test_grow_window_by_vertical_delta_keeps_width_and_grows_height():
    tk = pytest.importorskip("tkinter")
    try:
        root = tk.Tk()
    except tk.TclError as exc:
        pytest.skip(f"Tk not available: {exc}")
    try:
        root.geometry("500x300")
        root.update_idletasks()
        before = root.geometry()
        before_w = int(before.split("x")[0])
        before_h = int(before.split("x")[1].split("+")[0])
        grow_window_by_vertical_delta(root, 80)
        root.update_idletasks()
        after = root.geometry()
        after_w = int(after.split("x")[0])
        after_h = int(after.split("x")[1].split("+")[0])
        assert after_w == before_w
        assert after_h >= before_h
    finally:
        root.destroy()


def test_resize_geometry_changes_do_not_hang():
    """Regression guard: rapid root geometry changes must return promptly."""
    tk = pytest.importorskip("tkinter")
    try:
        root = tk.Tk()
    except tk.TclError as exc:
        pytest.skip(f"Tk not available: {exc}")
    try:
        from ui_tk.calculator_app import CalculatorTkApp

        app = CalculatorTkApp(root=root)
        root.update_idletasks()
        for geom in ("600x500", "800x650", "1000x750", "700x550"):
            root.geometry(geom)
            root.update_idletasks()
            # If we reach here without hanging, the test passes.
            assert root.winfo_width() > 0
            assert root.winfo_height() > 0
    finally:
        root.destroy()
