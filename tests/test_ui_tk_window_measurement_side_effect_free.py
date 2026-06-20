"""Focused tests for side-effect-free nested notebook measurement.

Covers:
- Measurement does not programmatically select hidden tabs.
- Current tab width/height is used for nested notebook measurement.
- Width shrinks when switching to narrow tab.
- Height shrinks when detail closes (simulated).
- Chrome estimate is computed once.
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
        self._notebook_width = 400

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

    def winfo_reqwidth(self) -> int:
        return self._notebook_width

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
        from apps.calculator.ui.window_measurement import TkVisibleContentMeasurement

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

    def test_current_tab_width_and_height_are_used(self) -> None:
        from apps.calculator.ui.window_measurement import TkVisibleContentMeasurement

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
        assert diagnostics["nested_current_tab_width"] == 300
        assert diagnostics["nested_current_tab_height"] == 200
        assert diagnostics["nested_max_tab_width"] == 300
        assert diagnostics["nested_max_tab_height"] == 250

    def test_chrome_height_uses_tallest_tab_when_notebook_request_is_sticky(
        self,
    ) -> None:
        from apps.calculator.ui.window_measurement import TkVisibleContentMeasurement

        short_tab = FakeWidget(width=300, height=200)
        tall_tab = FakeWidget(width=500, height=500)
        notebook = FakeNotebook(
            {"short": short_tab, "tall": tall_tab}, "short"
        )
        notebook._notebook_height = 525
        measurement = TkVisibleContentMeasurement(
            content=FakeContent(width=500, height=525),
            scrollbar=FakeScrollbar(),
            overflow_source=FakeOverflow(),
            nested_notebook=notebook,
            nested_notebook_active=lambda: True,
        )

        snapshot = measurement.snapshot()

        assert snapshot.diagnostics["nested_max_tab_height"] == 500
        assert snapshot.diagnostics["chrome_height_estimate"] == 25
        assert snapshot.preferred_size[1] == 236

    def test_width_shrinks_when_switching_to_narrow_tab(self) -> None:
        from apps.calculator.ui.window_measurement import TkVisibleContentMeasurement

        tab_a = FakeWidget(width=500, height=250)
        tab_b = FakeWidget(width=300, height=200)
        notebook = FakeNotebook({"tab_a": tab_a, "tab_b": tab_b}, "tab_a")
        # Content width matches notebook width (sticky at wide tab_a width)
        notebook._notebook_width = 500
        content = FakeContent(width=500, height=300)
        measurement = TkVisibleContentMeasurement(
            content=content,
            scrollbar=FakeScrollbar(),
            overflow_source=FakeOverflow(),
            nested_notebook=notebook,
            nested_notebook_active=lambda: True,
        )

        # First snapshot with wide tab_a (width 500)
        snapshot1 = measurement.snapshot()
        assert snapshot1.diagnostics["nested_max_tab_width"] == 500
        # Chrome width estimate = 500 - 500 = 0
        assert snapshot1.diagnostics["chrome_width_estimate"] == 0
        # Corrected width = content_w - notebook_w + chrome + current_tab
        # = 500 - 500 + 0 + 500 = 500
        # preferred_size[0] = int(500 * 1.05) + 16 = 541
        assert snapshot1.preferred_size[0] == 541

        # Switch to narrow tab_b (width 300) — width should shrink
        notebook._current = "tab_b"
        notebook._notebook_width = 500  # sticky at previous width
        snapshot2 = measurement.snapshot()
        assert snapshot2.diagnostics["nested_max_tab_width"] == 300
        # Corrected width = 500 - 500 + 0 + 300 = 300
        # preferred_size[0] = int(300 * 1.05) + 16 = 331
        assert snapshot2.preferred_size[0] == 331
        assert snapshot2.preferred_size[0] < snapshot1.preferred_size[0]

        # Switch back to tab_a — width should grow again
        notebook._current = "tab_a"
        snapshot3 = measurement.snapshot()
        assert snapshot3.diagnostics["nested_max_tab_width"] == 500
        assert snapshot3.preferred_size[0] == 541

    def test_height_shrinks_when_detail_closes(self) -> None:
        from apps.calculator.ui.window_measurement import TkVisibleContentMeasurement

        tab_a = FakeWidget(width=300, height=500)
        notebook = FakeNotebook({"tab_a": tab_a}, "tab_a")
        # Notebook height is sticky at detail-open height (tab + 500)
        notebook._notebook_height = 525
        # Content height includes the notebook
        content = FakeContent(width=400, height=525)
        measurement = TkVisibleContentMeasurement(
            content=content,
            scrollbar=FakeScrollbar(),
            overflow_source=FakeOverflow(),
            nested_notebook=notebook,
            nested_notebook_active=lambda: True,
        )

        # First measurement: detail open (tab height 500)
        snapshot1 = measurement.snapshot()
        # Chrome height estimate = 525 - 500 = 25
        assert snapshot1.diagnostics["chrome_height_estimate"] == 25
        # Corrected height = content_h - notebook_h + chrome + current_tab
        # = 525 - 525 + 25 + 500 = 525
        # preferred_size[1] = content_height + vertical_margin
        # vertical_margin = min(int(525 * 0.05), 18) = min(26, 18) = 18
        assert snapshot1.preferred_size[1] == 525 + 18

        # Simulate detail close: tab shrinks to 200, notebook stays sticky
        tab_a._height = 200
        notebook._notebook_height = 525  # sticky
        snapshot2 = measurement.snapshot()
        # Corrected height = 525 - 525 + 25 + 200 = 225
        # vertical_margin = min(int(225 * 0.05), 18) = 11
        # Height should shrink from 525 + 18 = 543 to 225 + 11 = 236
        assert snapshot2.preferred_size[1] == 225 + 11
        assert snapshot2.preferred_size[1] < snapshot1.preferred_size[1]

    def test_chrome_height_estimate_computed_once(self) -> None:
        from apps.calculator.ui.window_measurement import TkVisibleContentMeasurement

        tab_a = FakeWidget(width=300, height=200)
        notebook = FakeNotebook({"tab_a": tab_a}, "tab_a")
        notebook._notebook_height = 225
        measurement = TkVisibleContentMeasurement(
            content=FakeContent(),
            scrollbar=FakeScrollbar(),
            overflow_source=FakeOverflow(),
            nested_notebook=notebook,
            nested_notebook_active=lambda: True,
        )

        snapshot1 = measurement.snapshot()
        assert snapshot1.diagnostics["chrome_height_estimate"] == 25

        # Change notebook height (sticky); chrome estimate should stay the same
        notebook._notebook_height = 300
        snapshot2 = measurement.snapshot()
        assert snapshot2.diagnostics["chrome_height_estimate"] == 25

    def test_chrome_width_estimate_computed_once(self) -> None:
        from apps.calculator.ui.window_measurement import TkVisibleContentMeasurement

        tab_a = FakeWidget(width=300, height=200)
        notebook = FakeNotebook({"tab_a": tab_a}, "tab_a")
        notebook._notebook_width = 325
        measurement = TkVisibleContentMeasurement(
            content=FakeContent(),
            scrollbar=FakeScrollbar(),
            overflow_source=FakeOverflow(),
            nested_notebook=notebook,
            nested_notebook_active=lambda: True,
        )

        snapshot1 = measurement.snapshot()
        # Chrome width estimate = 325 - 300 = 25
        assert snapshot1.diagnostics["chrome_width_estimate"] == 25

        # Change notebook width (sticky); chrome estimate should stay the same
        notebook._notebook_width = 400
        snapshot2 = measurement.snapshot()
        assert snapshot2.diagnostics["chrome_width_estimate"] == 25

    def test_snapshot_is_side_effect_free_across_repeated_calls(self) -> None:
        from apps.calculator.ui.window_measurement import TkVisibleContentMeasurement

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
        from apps.calculator.ui.window_measurement import TkVisibleContentMeasurement

        measurement = TkVisibleContentMeasurement(
            content=FakeContent(),
            scrollbar=FakeScrollbar(),
            overflow_source=FakeOverflow(),
            nested_notebook=None,
        )

        snapshot = measurement.snapshot()
        assert snapshot.diagnostics["nested_max_tab_width"] == 0
        assert snapshot.diagnostics["nested_current_tab_width"] == 0
        assert snapshot.diagnostics["nested_current_tab_height"] == 0

    def test_inactive_nested_notebook_returns_empty_measurement(self) -> None:
        from apps.calculator.ui.window_measurement import TkVisibleContentMeasurement

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
        assert snapshot.diagnostics["nested_current_tab_width"] == 0
        assert snapshot.diagnostics["nested_current_tab_height"] == 0
