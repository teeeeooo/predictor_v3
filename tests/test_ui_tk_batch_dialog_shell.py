"""Unit tests for the generic Toplevel batch dialog shell."""

from __future__ import annotations

import tkinter as tk
import pytest

from ui_tk.batch_dialogs.shell import BatchDialogShell


class FakeProfileAdapter:
    """Mock profile adapter satisfying BatchProfileAdapter protocol."""

    def __init__(self) -> None:
        self.dispose_called = False
        self.build_called = False

    @property
    def title(self) -> str:
        return "Fake Title"

    @property
    def min_size(self) -> tuple[int, int]:
        return (200, 100)

    def build_content(self, parent: tk.Widget) -> tk.Widget:
        self.build_called = True
        frame = tk.Frame(parent)
        return frame

    def dispose(self) -> None:
        self.dispose_called = True

    def snapshot(self) -> list[dict[str, str]]:
        return [{"key": "value"}]


@pytest.fixture
def tk_root():
    tk_module = pytest.importorskip("tkinter")
    try:
        root = tk_module.Tk()
    except tk_module.TclError as exc:
        pytest.skip(f"Tk not available: {exc}")
    root.withdraw()
    try:
        yield root
    finally:
        root.destroy()


def test_shell_snapshot_returns_adapter_snapshot(tk_root):
    adapter = FakeProfileAdapter()
    shell = BatchDialogShell(tk_root, adapter)

    assert shell.snapshot() == [{"key": "value"}]
    shell.close()


def test_shell_close_passes_snapshot_to_callback(tk_root):
    adapter = FakeProfileAdapter()
    closed_snapshot: list[dict[str, str]] | None = None

    def on_close(snapshot: list[dict[str, str]]) -> None:
        nonlocal closed_snapshot
        closed_snapshot = snapshot

    shell = BatchDialogShell(tk_root, adapter, on_close=on_close)
    shell.close()

    assert closed_snapshot == [{"key": "value"}]
    assert adapter.dispose_called is True
