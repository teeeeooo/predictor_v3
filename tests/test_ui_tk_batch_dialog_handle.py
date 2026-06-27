"""Focused tests for the batch dialog lifecycle handle."""

from __future__ import annotations

from apps.calculator.ui.batch_dialogs.dialog_handle import BatchDialogHandle


class _FakeWindow:
    def __init__(self) -> None:
        self.exists = True

    def winfo_exists(self) -> bool:
        return self.exists


class _FakeDialog:
    def __init__(self, events: list[str]) -> None:
        self.window = _FakeWindow()
        self.events = events

    def focus(self) -> None:
        self.events.append("focus")

    def close(self) -> None:
        self.events.append("close")


def test_handle_focuses_existing_live_dialog() -> None:
    events: list[str] = []
    handle: BatchDialogHandle[object, _FakeDialog] = BatchDialogHandle()

    first = handle.open_or_focus(lambda: _FakeDialog(events))
    second = handle.open_or_focus(lambda: _FakeDialog(events))

    assert second is first
    assert events == ["focus"]


def test_handle_reopens_externally_destroyed_dialog() -> None:
    events: list[str] = []
    handle: BatchDialogHandle[object, _FakeDialog] = BatchDialogHandle()

    first = handle.open_or_focus(lambda: _FakeDialog(events))
    first.window.exists = False
    second = handle.open_or_focus(lambda: _FakeDialog(events))

    assert second is not first
    assert events == []


def test_handle_clear_preserves_non_none_snapshot_policy() -> None:
    handle: BatchDialogHandle[str, _FakeDialog] = BatchDialogHandle(snapshot="old")

    handle.clear(None)
    assert handle.snapshot == "old"
    handle.clear("new")
    assert handle.snapshot == "new"


def test_handle_dispose_closes_once_and_clears_reference() -> None:
    events: list[str] = []
    handle: BatchDialogHandle[object, _FakeDialog] = BatchDialogHandle()
    dialog = handle.open_or_focus(lambda: _FakeDialog(events))

    handle.dispose()

    assert events == ["close"]
    assert handle.dialog is None
    assert dialog.window.winfo_exists()
