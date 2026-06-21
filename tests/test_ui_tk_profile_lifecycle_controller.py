"""Focused contracts for the shared profile visible-content lifecycle owner."""

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


def _build_controller(tk_root, **policy):
    from tkinter import ttk

    from apps.calculator.ui.lifecycle import (
        ProfileVisibleContentLifecycleController,
    )
    from apps.calculator.ui.scrollable_frame import ScrollableFrame

    owner = ttk.Frame(tk_root)
    owner.pack(fill="both", expand=True)
    scrollable = ScrollableFrame(owner)
    scrollable.pack(fill="both", expand=True)
    ttk.Label(scrollable.content, text="content").pack()
    controller = ProfileVisibleContentLifecycleController(
        owner=owner,
        content=scrollable.content,
        scrollable=scrollable,
        **policy,
    )
    tk_root.update_idletasks()
    return controller, scrollable


def test_named_triggers_use_configured_settle_cycles(tk_root) -> None:
    controller, _scrollable = _build_controller(
        tk_root,
        parent_selected_settle_cycles=2,
        nested_tab_settle_cycles=3,
        detail_visibility_settle_cycles=4,
    )
    calls: list[int] = []
    controller.scheduler.request_refit = (
        lambda *, settle_cycles=1: calls.append(settle_cycles) or True
    )

    assert controller.on_parent_tab_selected() is True
    assert controller.on_nested_tab_changed() is True
    assert controller.on_detail_visibility_changed() is True

    assert calls == [2, 3, 4]


def test_parent_trigger_is_optional(tk_root) -> None:
    controller, _scrollable = _build_controller(tk_root)
    calls: list[int] = []
    controller.scheduler.request_refit = (
        lambda *, settle_cycles=1: calls.append(settle_cycles) or True
    )

    assert controller.on_parent_tab_selected() is False
    assert calls == []


@pytest.mark.parametrize("policy_value", [0, -1, True, 1.5])
def test_invalid_settle_policy_fails_explicitly(tk_root, policy_value) -> None:
    with pytest.raises(ValueError, match="positive integer"):
        _build_controller(tk_root, nested_tab_settle_cycles=policy_value)


def test_preferred_size_fit_and_scroll_reset_share_one_controller(tk_root) -> None:
    controller, scrollable = _build_controller(tk_root)
    resets: list[str] = []
    scrollable.reset_scroll_position = lambda: resets.append("reset")

    preferred = controller.preferred_initial_size()
    controller.fit_toplevel_to_current_content_once()

    assert preferred[0] > 0
    assert preferred[1] > 0
    assert resets == ["reset"]
