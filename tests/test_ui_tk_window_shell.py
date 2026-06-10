"""Tests for Tkinter content-hugging shell geometry."""

from __future__ import annotations

import pytest

from apps.calculator.ui.window_geometry import capped_window_size
from dataclasses import dataclass

from apps.calculator.ui.window_shell import TkContentHuggingShell, visible_content_fit_geometry


@dataclass(frozen=True)
class FakeSnapshot:
    preferred_size: tuple[int, int]
    vertical_overflow_delta: int = 0
    include_overflow_in_fit: bool = False


class FakeRoot:
    def __init__(
        self,
        geometry: str = "800x600+100+80",
        *,
        screen_width: int = 1600,
        screen_height: int = 1000,
    ) -> None:
        self._geometry = geometry
        self._screen_width = screen_width
        self._screen_height = screen_height
        self.geometry_calls: list[str] = []
        self.minsize_calls: list[tuple[int, int]] = []
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
        return self._screen_width

    def winfo_screenheight(self) -> int:
        return self._screen_height

    def minsize(self, width: int, height: int) -> None:
        self.minsize_calls.append((width, height))


def test_visible_content_fit_geometry_uses_preferred_visible_size():
    assert visible_content_fit_geometry(
        current_geometry="900x700+120+90",
        preferred_content_size=(640, 420),
        screen_width=1600,
        screen_height=1000,
    ) == "640x420+120+90"


def test_visible_content_fit_geometry_includes_overflow_before_single_apply():
    assert visible_content_fit_geometry(
        current_geometry="900x700+120+90",
        preferred_content_size=(640, 420),
        screen_width=1600,
        screen_height=1000,
        vertical_overflow_delta=80,
    ) == "640x500+120+90"


def test_visible_content_fit_geometry_clamps_to_screen_policy():
    screen_width = 1200
    screen_height = 800
    expected_w, expected_h = capped_window_size(
        1800,
        1200,
        screen_width,
        screen_height,
    )

    assert visible_content_fit_geometry(
        current_geometry="800x600+100+760",
        preferred_content_size=(1800, 1200),
        screen_width=screen_width,
        screen_height=screen_height,
    ) == f"{expected_w}x{expected_h}+100+64"


def test_tk_content_hugging_shell_applies_geometry_once():
    root = FakeRoot()
    shell = TkContentHuggingShell(root)

    result = shell.fit_visible_content(
        (640, 420),
        vertical_overflow_delta=80,
    )

    assert result.applied is True
    assert result.target_geometry == "640x500+100+80"
    assert root.minsize_calls == []
    assert root.geometry_calls == ["640x500+100+80"]
    assert root.update_calls == 2


def test_tk_content_hugging_shell_skips_noop_geometry_apply():
    root = FakeRoot("640x500+100+80")
    shell = TkContentHuggingShell(root)

    result = shell.fit_visible_content((640, 500))

    assert result.applied is False
    assert result.target_geometry == "640x500+100+80"
    assert root.minsize_calls == []
    assert root.geometry_calls == []
    assert root.update_calls == 1


def test_shell_registers_provider_based_content_form():
    root = FakeRoot()
    shell = TkContentHuggingShell(root)
    after_fit_results = []
    form = shell.register_content(
        preferred_size_provider=lambda: (640, 420),
        overflow_provider=lambda: 80,
        after_fit=after_fit_results.append,
    )

    result = form.fit()

    assert result.target_geometry == "640x500+100+80"
    assert root.minsize_calls == []
    assert root.geometry_calls == ["640x500+100+80"]
    assert after_fit_results == [result]


def test_shell_uses_snapshot_provider_for_one_measurement_object():
    root = FakeRoot()
    shell = TkContentHuggingShell(root)
    calls = []

    def snapshot_provider() -> FakeSnapshot:
        calls.append("snapshot")
        return FakeSnapshot((640, 420), vertical_overflow_delta=80)

    form = shell.register_content(snapshot_provider=snapshot_provider)

    result = form.fit()

    assert calls == ["snapshot"]
    assert result.target_geometry == "640x420+100+80"
    assert root.geometry_calls == ["640x420+100+80"]


def test_shell_snapshot_can_include_overflow_when_policy_allows_it():
    root = FakeRoot()
    shell = TkContentHuggingShell(root)
    form = shell.register_content(
        snapshot_provider=lambda: FakeSnapshot(
            (640, 420),
            vertical_overflow_delta=80,
            include_overflow_in_fit=True,
        )
    )

    result = form.fit()

    assert result.target_geometry == "640x500+100+80"
    assert root.geometry_calls == ["640x500+100+80"]


def test_shell_registers_widget_content_default_measurement():
    class FakeContent:
        def __init__(self) -> None:
            self.update_calls = 0

        def update_idletasks(self) -> None:
            self.update_calls += 1

        def winfo_reqwidth(self) -> int:
            return 620

        def winfo_reqheight(self) -> int:
            return 410

    root = FakeRoot()
    content = FakeContent()
    form = TkContentHuggingShell(root).register_content(content=content)

    result = form.fit()

    assert result.target_geometry == "620x410+100+80"
    assert root.geometry_calls == ["620x410+100+80"]
    assert content.update_calls == 1


def test_shell_requires_content_or_measurement_provider():
    shell = TkContentHuggingShell(FakeRoot())

    with pytest.raises(
        ValueError,
        match="content, snapshot_provider, or preferred_size_provider",
    ):
        shell.register_content()
