"""Focused tests for shared Tk window lifecycle repairs.

Covers:
- Content fit does not permanently lock root minsize.
- Hong Kong HSPF section accepts and calls detail visibility callback.
- Iso16358Tab metric notebook tab change requests scheduler-based refit.
"""

from __future__ import annotations

import pytest


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


class TestWindowShellMinsizePolicy:
    def test_fit_visible_content_does_not_update_minsize(self) -> None:
        from ui_tk.window_shell import TkContentHuggingShell

        class FakeRoot:
            def __init__(self) -> None:
                self._geometry = "800x600+100+80"
                self.minsize_calls: list[tuple[int, int]] = []
                self.geometry_calls: list[str] = []
                self.update_calls = 0

            def geometry(self, value: str | None = None) -> str:
                if value is None:
                    return self._geometry
                self.geometry_calls.append(value)
                self._geometry = value
                return self._geometry

            def update_idletasks(self) -> None:
                self.update_calls += 1

            def winfo_screenwidth(self) -> int:
                return 1600

            def winfo_screenheight(self) -> int:
                return 1000

            def minsize(self, width: int, height: int) -> None:
                self.minsize_calls.append((width, height))

        root = FakeRoot()
        shell = TkContentHuggingShell(root)
        shell.fit_visible_content((1200, 900))
        assert root.minsize_calls == []
        # Height is capped by capped_window_size to screen_height * 0.80 = 800
        assert root.geometry_calls == ["1200x800+100+80"]

    def test_fit_visible_content_to_smaller_target_does_not_raise_minsize(self) -> None:
        from ui_tk.window_shell import TkContentHuggingShell

        class FakeRoot:
            def __init__(self) -> None:
                self._geometry = "1200x900+100+80"
                self.minsize_calls: list[tuple[int, int]] = []
                self.geometry_calls: list[str] = []
                self.update_calls = 0

            def geometry(self, value: str | None = None) -> str:
                if value is None:
                    return self._geometry
                self.geometry_calls.append(value)
                self._geometry = value
                return self._geometry

            def update_idletasks(self) -> None:
                self.update_calls += 1

            def winfo_screenwidth(self) -> int:
                return 1600

            def winfo_screenheight(self) -> int:
                return 1000

            def minsize(self, width: int, height: int) -> None:
                self.minsize_calls.append((width, height))

        root = FakeRoot()
        shell = TkContentHuggingShell(root)
        shell.fit_visible_content((640, 480))
        assert root.minsize_calls == []
        assert root.geometry_calls == ["640x480+100+80"]


class TestHspfDetailVisibilityCallback:
    def test_hspf_section_accepts_callback_parameter(self, tk_root) -> None:
        from ui_tk.sections.hong_kong_hspf_section import HongKongHspfSection

        calls = []
        section = HongKongHspfSection(
            tk_root,
            "Hong Kong",
            on_trace_visibility_changed=lambda: calls.append("changed"),
        )
        assert section._on_detail_visibility_changed is not None

    def test_hspf_detail_toggle_calls_callback(self, tk_root) -> None:
        from ui_tk.sections.hong_kong_hspf_section import HongKongHspfSection

        calls = []
        section = HongKongHspfSection(
            tk_root,
            "Hong Kong",
            on_trace_visibility_changed=lambda: calls.append("changed"),
        )
        tk_root.update_idletasks()
        section.detail_toggle.invoke()
        tk_root.update_idletasks()
        assert "changed" in calls

    def test_hspf_detail_toggle_without_callback_does_not_crash(self, tk_root) -> None:
        from ui_tk.sections.hong_kong_hspf_section import HongKongHspfSection

        section = HongKongHspfSection(tk_root, "Hong Kong")
        tk_root.update_idletasks()
        section.detail_toggle.invoke()
        tk_root.update_idletasks()
        assert section.detail_panel.is_visible()


class TestMetricTabChangeRefitScheduling:
    def test_metric_tab_change_requests_refit(self, tk_root) -> None:
        from ui_tk.tabs.iso16358_tab import Iso16358Tab

        tab = Iso16358Tab(tk_root)
        tk_root.update_idletasks()
        # Switch to Hong Kong mode to create the metric notebook
        tab._mode_combo.set("Hong Kong")
        tab._on_mode_changed()
        tk_root.update_idletasks()

        assert tab._metric_notebook is not None
        # Before invoking tab change, scheduler should not be pending
        assert not tab._refit_scheduler.is_pending

        # Simulate tab change event
        tab._on_metric_tab_changed()
        assert tab._refit_scheduler.is_pending

    def test_mode_change_still_requests_refit(self, tk_root) -> None:
        from ui_tk.tabs.iso16358_tab import Iso16358Tab

        tab = Iso16358Tab(tk_root)
        tk_root.update_idletasks()
        assert not tab._refit_scheduler.is_pending
        tab._on_mode_changed()
        assert tab._refit_scheduler.is_pending

    def test_iso_iseer_section_receives_visibility_callback(self, tk_root) -> None:
        from ui_tk.tabs.iso16358_tab import Iso16358Tab

        tab = Iso16358Tab(tk_root)
        tk_root.update_idletasks()
        # ISO/ISEER 2-point is the default mode
        assert tab._two_point_section is not None
        # The section should have received the callback during construction
        assert tab._two_point_section._on_trace_visibility_changed is not None

    def test_saso_section_receives_visibility_callback(self, tk_root) -> None:
        from ui_tk.tabs.iso16358_tab import Iso16358Tab

        tab = Iso16358Tab(tk_root)
        tk_root.update_idletasks()
        tab._mode_combo.set("SASO T3")
        tab._on_mode_changed()
        tk_root.update_idletasks()
        assert tab._saso_t3_section is not None
        assert tab._saso_t3_section._on_trace_visibility_changed is not None

    def test_hong_kong_cspf_receives_visibility_callback(self, tk_root) -> None:
        from ui_tk.tabs.iso16358_tab import Iso16358Tab

        tab = Iso16358Tab(tk_root)
        tk_root.update_idletasks()
        tab._mode_combo.set("Hong Kong")
        tab._on_mode_changed()
        tk_root.update_idletasks()
        cspf_section = tab._hong_kong_sections.get("CSPF")
        assert cspf_section is not None
        assert cspf_section._on_detail_visibility_changed is not None

    def test_hong_kong_hspf_receives_visibility_callback(self, tk_root) -> None:
        from ui_tk.tabs.iso16358_tab import Iso16358Tab

        tab = Iso16358Tab(tk_root)
        tk_root.update_idletasks()
        tab._mode_combo.set("Hong Kong")
        tab._on_mode_changed()
        tk_root.update_idletasks()
        hspf_section = tab._hong_kong_sections.get("HSPF")
        assert hspf_section is not None
        assert hspf_section._on_detail_visibility_changed is not None
