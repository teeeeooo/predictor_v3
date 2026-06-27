"""Section-layer helper for calculator detail panel visibility."""

from __future__ import annotations

from collections.abc import Callable, Mapping
import tkinter as tk


class DetailPanelVisibility:
    """Own detail panel show/hide state, button text, and change callback."""

    def __init__(
        self,
        *,
        panel: tk.Widget,
        button: tk.Widget,
        grid_options: Mapping[str, object],
        before_show: Callable[[], None] | None = None,
        on_change: Callable[[], None] | None = None,
    ) -> None:
        self._panel = panel
        self._button = button
        self._grid_options = dict(grid_options)
        self._before_show = before_show
        self._on_change = on_change
        self.visible = False

    def toggle(self) -> None:
        self.visible = not self.visible
        if self.visible:
            if self._before_show is not None:
                self._before_show()
            self._panel.grid(**self._grid_options)
            self._button.configure(text="상세 닫기 ↑")
        else:
            self._panel.grid_remove()
            self._button.configure(text="상세 보기 ↓")
        if self._on_change is not None:
            self._on_change()
