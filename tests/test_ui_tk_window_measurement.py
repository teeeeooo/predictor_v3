"""Tests for Tk visible content measurement adapters."""

from __future__ import annotations

from contextlib import contextmanager

from apps.calculator.ui.window_measurement import TkVisibleContentMeasurement


class FakeContent:
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.update_calls = 0

    def update_idletasks(self) -> None:
        self.update_calls += 1

    def winfo_reqwidth(self) -> int:
        return self.width

    def winfo_reqheight(self) -> int:
        return self.height


class FakeScrollbar:
    def __init__(self, width: int = 15) -> None:
        self.width = width

    def winfo_reqwidth(self) -> int:
        return self.width


class FakeOverflowSource:
    def __init__(self, delta: int = 0) -> None:
        self.delta = delta

    def vertical_overflow_delta(self) -> int:
        return self.delta


class FakeNotebook:
    def __init__(
        self,
        tabs: dict[str, FakeContent],
        *,
        selected: str,
        notebook_height: int,
    ) -> None:
        self._tabs = tabs
        self._selected = selected
        self.notebook_height = notebook_height
        self.selected_history: list[str] = []
        self.update_calls = 0

    def tabs(self) -> tuple[str, ...]:
        return tuple(self._tabs)

    def select(self, tab_id: str | None = None) -> str:
        if tab_id is None:
            return self._selected
        self._selected = tab_id
        self.selected_history.append(tab_id)
        return self._selected

    def nametowidget(self, tab_id: str) -> FakeContent:
        return self._tabs[tab_id]

    def update_idletasks(self) -> None:
        self.update_calls += 1

    def winfo_reqheight(self) -> int:
        return self.notebook_height


def test_visible_measurement_uses_simple_content_size_without_nested_notebook():
    measurement = TkVisibleContentMeasurement(
        content=FakeContent(500, 300),
        scrollbar=FakeScrollbar(15),
        overflow_source=FakeOverflowSource(),
    )

    assert measurement.preferred_size() == (540, 315)


def test_visible_measurement_snapshot_returns_size_overflow_and_diagnostics():
    measurement = TkVisibleContentMeasurement(
        content=FakeContent(500, 300),
        scrollbar=FakeScrollbar(15),
        overflow_source=FakeOverflowSource(42),
    )

    snapshot = measurement.snapshot()

    assert snapshot.preferred_size == (540, 315)
    assert snapshot.vertical_overflow_delta == 42
    assert snapshot.include_overflow_in_fit is False
    assert snapshot.diagnostics["content_reqheight"] == 300
    assert snapshot.diagnostics["vertical_overflow_delta"] == 42


def test_nested_notebook_uses_hidden_tabs_for_width_but_visible_tab_for_height():
    content = FakeContent(400, 500)
    notebook = FakeNotebook(
        {
            "current": FakeContent(450, 180),
            "hidden": FakeContent(520, 280),
        },
        selected="current",
        notebook_height=300,
    )
    suppress_events = []

    @contextmanager
    def suppress_measurement():
        suppress_events.append("enter")
        try:
            yield
        finally:
            suppress_events.append("exit")

    measurement = TkVisibleContentMeasurement(
        content=content,
        scrollbar=FakeScrollbar(15),
        overflow_source=FakeOverflowSource(),
        nested_notebook=notebook,
        nested_notebook_active=lambda: True,
        suppress_measurement=suppress_measurement,
    )

    snapshot = measurement.snapshot()

    assert snapshot.preferred_size == (561, 418)
    assert snapshot.vertical_overflow_delta == 0
    assert snapshot.include_overflow_in_fit is False
    assert snapshot.diagnostics["nested_max_tab_width"] == 520
    assert snapshot.diagnostics["nested_current_tab_height"] == 180
    assert notebook.selected_history == ["current", "hidden", "current"]
    assert suppress_events == ["enter", "exit"]


def test_inactive_nested_notebook_does_not_affect_measurement():
    measurement = TkVisibleContentMeasurement(
        content=FakeContent(400, 500),
        scrollbar=FakeScrollbar(15),
        overflow_source=FakeOverflowSource(),
        nested_notebook=FakeNotebook(
            {"current": FakeContent(450, 180), "hidden": FakeContent(900, 900)},
            selected="current",
            notebook_height=920,
        ),
        nested_notebook_active=lambda: False,
    )

    assert measurement.preferred_size() == (435, 518)


def test_visible_measurement_delegates_vertical_overflow_delta():
    measurement = TkVisibleContentMeasurement(
        content=FakeContent(500, 300),
        scrollbar=FakeScrollbar(15),
        overflow_source=FakeOverflowSource(42),
    )

    assert measurement.vertical_overflow_delta() == 42


def test_compatibility_methods_read_from_snapshots():
    measurement = TkVisibleContentMeasurement(
        content=FakeContent(500, 300),
        scrollbar=FakeScrollbar(15),
        overflow_source=FakeOverflowSource(42),
    )

    assert measurement.preferred_size() == measurement.snapshot().preferred_size
    assert measurement.vertical_overflow_delta() == measurement.snapshot().vertical_overflow_delta
