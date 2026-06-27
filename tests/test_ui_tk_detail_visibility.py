"""Focused tests for section-layer detail panel visibility helper."""

from __future__ import annotations

from apps.calculator.ui.sections.detail_visibility import DetailPanelVisibility


class _FakePanel:
    def __init__(self) -> None:
        self.grid_calls: list[dict[str, object]] = []
        self.remove_calls = 0

    def grid(self, **kwargs: object) -> None:
        self.grid_calls.append(dict(kwargs))

    def grid_remove(self) -> None:
        self.remove_calls += 1


class _FakeButton:
    def __init__(self) -> None:
        self.text = "상세 보기 ↓"

    def configure(self, **kwargs: object) -> None:
        if "text" in kwargs:
            self.text = str(kwargs["text"])


def test_detail_visibility_shows_and_hides_with_button_text() -> None:
    panel = _FakePanel()
    button = _FakeButton()
    changes: list[str] = []
    visibility = DetailPanelVisibility(
        panel=panel,
        button=button,
        grid_options={"row": 3, "column": 0, "sticky": "ew"},
        on_change=lambda: changes.append("changed"),
    )

    visibility.toggle()
    assert visibility.visible is True
    assert panel.grid_calls == [{"row": 3, "column": 0, "sticky": "ew"}]
    assert button.text == "상세 닫기 ↑"
    assert changes == ["changed"]

    visibility.toggle()
    assert visibility.visible is False
    assert panel.remove_calls == 1
    assert button.text == "상세 보기 ↓"
    assert changes == ["changed", "changed"]


def test_detail_visibility_runs_before_show_before_grid() -> None:
    panel = _FakePanel()
    button = _FakeButton()
    events: list[str] = []

    def before_show() -> None:
        events.append(f"before:{len(panel.grid_calls)}")

    visibility = DetailPanelVisibility(
        panel=panel,
        button=button,
        grid_options={"row": 1},
        before_show=before_show,
        on_change=lambda: events.append("changed"),
    )

    visibility.toggle()

    assert events == ["before:0", "changed"]
    assert panel.grid_calls == [{"row": 1}]
