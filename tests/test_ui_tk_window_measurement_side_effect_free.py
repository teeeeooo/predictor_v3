"""Focused tests for side-effect-free nested notebook measurement.

Covers:
- Measurement does not programmatically select hidden tabs.
- Current tab height is used for nested notebook measurement.
- Observed width cache updates from current visible tab only.
- Snapshot remains side-effect-free across repeated calls.
"""

from __future__ import annotations

import pytest


class FakeWidget:
    def __init__(self, width: int = 0, height: int = 0) -> None:
        self._width = width
        self._height = height

    def winfo_reqwidth(self) -> int:
        return self._width

    def winfo_reqheight(self) -> int:
        return self._height


class FakeNotebook:
    def __init__(self, tabs: dict[str, FakeWidget], current: str) -> None:
        self._tabs = tabs
        self._current = current
        self._select_calls: list[str] = []
        self._notebook_height = 100

    def tabs(self) -> tuple[str, ...]:
        return tuple(self._tabs.keys())

    def select(self, tab_id: str | None = None) -> str:
        if tab_id is not None:
            self._select_calls.append(tab_id)
            self._current = tab_id
        return self._current

    def nametowidget(self, tab_id: str) -> FakeWidget:
        return self._tabs[tab_id]

    def winfo_reqheight(self) -> int:
        return self._notebook_height

    def update_idletasks(self) -> None:
        pass


class FakeContent:
    def __init__(self, width: int = 400, height: int = 300) -> None:
        self._width = width
        self._height = height

    def update_idletasks(self) -> None:
        pass

    def winfo_reqwidth(self) -> int:
        return self._width

    def winfo_reqheight(self) -> int:
        return self._height


class FakeScrollbar:
    def __init__(self, width: int = 16) -> None:
        self._width = width

    def winfo_reqwidth(self) -> int:
        return self._width


class FakeOverflow:
    def vertical_overflow_delta(self) -> int:
        return 0


class TestSideEffectFreeMeasurement:
    def test_measurement_does_not_select_hidden_tabs(self) -> None:
        from ui_tk.window_measurement import TkVisibleContentMeasurement

        tab_a = FakeWidget(width=300, height=200)
        tab_b = FakeWidget(width=500, height=250)
        notebook = FakeNotebook({"tab_a": tab_a, "tab_b": tab_b}, "tab_a")
        measurement = TkVisibleContentMeasurement(
            content=FakeContent(),
            scrollbar=FakeScrollbar(),
            overflow_source=FakeOverflow(),
            nested_notebook=notebook,
            nested_notebook_active=lambda: True,
        )

        measurement.snapshot()

        # Only the initial select() with no args (to read current tab) should occur.
        # No programmatic select(tab_id) calls with an argument.
        select_with_arg_calls = [c for c in notebook._select_calls if c]
        assert select_with_arg_calls == []

    def test_current_tab_height_is_used(self) -> None:
        from ui_tk.window_measurement import TkVisibleContentMeasurement

        tab_a = FakeWidget(width=300, height=200)
        tab_b = FakeWidget(width=500, height=250)
        notebook = FakeNotebook({"tab_a": tab_a, "tab_b": tab_b}, "tab_a")
        measurement = TkVisibleContentMeasurement(
            content=FakeContent(),
            scrollbar=FakeScrollbar(),
            overflow_source=FakeOverflow(),
            nested_notebook=notebook,
            nested_notebook_active=lambda: True,
        )

        snapshot = measurement.snapshot()
        diagnostics = snapshot.diagnostics
        assert diagnostics["nested_current_tab_height"] == 200
        assert diagnostics["nested_max_tab_height"] == 200

    def test_observed_width_cache_updates(self) -> None:
        from ui_tk.window_measurement import TkVisibleContentMeasurement

        tab_a = FakeWidget(width=300, height=200)
        tab_b = FakeWidget(width=500, height=250)
        notebook = FakeNotebook({"tab_a": tab_a, "tab_b": tab_b}, "tab_a")
        measurement = TkVisibleContentMeasurement(
            content=FakeContent(),
            scrollbar=FakeScrollbar(),
            overflow_source=FakeOverflow(),
            nested_notebook=notebook,
            nested_notebook_active=lambda: True,
        )

        # First snapshot with tab_a (width 300)
        snapshot1 = measurement.snapshot()
        assert snapshot1.diagnostics["nested_max_tab_width"] == 300

        # Simulate tab switch to tab_b (width 500)
        notebook._current = "tab_b"
        snapshot2 = measurement.snapshot()
        assert snapshot2.diagnostics["nested_max_tab_width"] == 500

        # Switch back to tab_a; observed max width remains 500
        notebook._current = "tab_a"
        snapshot3 = measurement.snapshot()
        assert snapshot3.diagnostics["nested_max_tab_width"] == 500

    def test_snapshot_is_side_effect_free_across_repeated_calls(self) -> None:
        from ui_tk.window_measurement import TkVisibleContentMeasurement

        tab_a = FakeWidget(width=300, height=200)
        tab_b = FakeWidget(width=500, height=250)
        notebook = FakeNotebook({"tab_a": tab_a, "tab_b": tab_b}, "tab_a")
        measurement = TkVisibleContentMeasurement(
            content=FakeContent(),
            scrollbar=FakeScrollbar(),
            overflow_source=FakeOverflow(),
            nested_notebook=notebook,
            nested_notebook_active=lambda: True,
        )

        for _ in range(5):
            measurement.snapshot()

        select_with_arg_calls = [c for c in notebook._select_calls if c]
        assert select_with_arg_calls == []

    def test_no_nested_notebook_returns_empty_measurement(self) -> None:
        from ui_tk.window_measurement import TkVisibleContentMeasurement

        measurement = TkVisibleContentMeasurement(
            content=FakeContent(),
            scrollbar=FakeScrollbar(),
            overflow_source=FakeOverflow(),
            nested_notebook=None,
        )

        snapshot = measurement.snapshot()
        assert snapshot.diagnostics["nested_max_tab_width"] == 0
        assert snapshot.diagnostics["nested_current_tab_height"] == 0

    def test_inactive_nested_notebook_returns_empty_measurement(self) -> None:
        from ui_tk.window_measurement import TkVisibleContentMeasurement

        tab_a = FakeWidget(width=300, height=200)
        notebook = FakeNotebook({"tab_a": tab_a}, "tab_a")
        measurement = TkVisibleContentMeasurement(
            content=FakeContent(),
            scrollbar=FakeScrollbar(),
            overflow_source=FakeOverflow(),
            nested_notebook=notebook,
            nested_notebook_active=lambda: False,
        )

        snapshot = measurement.snapshot()
        assert snapshot.diagnostics["nested_max_tab_width"] == 0
        assert snapshot.diagnostics["nested_current_tab_height"] == 0
