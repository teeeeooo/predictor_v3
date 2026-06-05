"""Tests for Tkinter content-hugging shell geometry."""

from __future__ import annotations

from ui_tk.window_geometry import capped_window_size
from ui_tk.window_shell import TkContentHuggingShell, visible_content_fit_geometry


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
    assert root.geometry_calls == ["640x500+100+80"]
    assert root.update_calls == 2


def test_tk_content_hugging_shell_skips_noop_geometry_apply():
    root = FakeRoot("640x500+100+80")
    shell = TkContentHuggingShell(root)

    result = shell.fit_visible_content((640, 500))

    assert result.applied is False
    assert result.target_geometry == "640x500+100+80"
    assert root.geometry_calls == []
    assert root.update_calls == 1
