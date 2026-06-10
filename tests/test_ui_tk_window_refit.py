"""Tests for common Tk dynamic content refit scheduling."""

from __future__ import annotations

from apps.calculator.ui.window_refit import DynamicContentRefitScheduler


class FakeRefitOwner:
    def __init__(self) -> None:
        self.callbacks = []
        self.update_calls = 0

    def after_idle(self, callback):
        self.callbacks.append(callback)
        return f"idle-{len(self.callbacks)}"

    def update_idletasks(self) -> None:
        self.update_calls += 1


def test_refit_scheduler_coalesces_duplicate_requests():
    owner = FakeRefitOwner()
    calls = []
    scheduler = DynamicContentRefitScheduler(owner, lambda: calls.append("fit"))

    assert scheduler.request_refit() is True
    assert scheduler.request_refit() is False

    assert len(owner.callbacks) == 1
    owner.callbacks.pop(0)()
    assert calls == []
    assert len(owner.callbacks) == 1

    owner.callbacks.pop(0)()
    assert calls == ["fit"]
    assert scheduler.is_pending is False
    assert scheduler.is_running is False


def test_refit_scheduler_suppresses_measurement_side_effect_requests():
    owner = FakeRefitOwner()
    calls = []
    scheduler = DynamicContentRefitScheduler(owner, lambda: calls.append("fit"))

    with scheduler.suppress_requests():
        assert scheduler.is_suppressed is True
        assert scheduler.request_refit() is False

    assert scheduler.is_suppressed is False
    assert owner.callbacks == []
    assert calls == []


def test_refit_scheduler_blocks_reentrant_requests_during_fit():
    owner = FakeRefitOwner()
    calls = []
    scheduler = None

    def fit():
        calls.append("fit")
        assert scheduler.request_refit() is False

    scheduler = DynamicContentRefitScheduler(owner, fit)

    assert scheduler.request_refit() is True
    owner.callbacks.pop(0)()
    owner.callbacks.pop(0)()

    assert calls == ["fit"]
    assert owner.callbacks == []
    assert scheduler.is_pending is False
    assert scheduler.is_running is False


def test_refit_scheduler_allows_new_request_after_fit_completes():
    owner = FakeRefitOwner()
    calls = []
    scheduler = DynamicContentRefitScheduler(owner, lambda: calls.append("fit"))

    assert scheduler.request_refit() is True
    owner.callbacks.pop(0)()
    owner.callbacks.pop(0)()

    assert scheduler.request_refit() is True
    owner.callbacks.pop(0)()
    owner.callbacks.pop(0)()

    assert calls == ["fit", "fit"]


def test_refit_scheduler_supports_extra_settle_cycles():
    owner = FakeRefitOwner()
    calls = []
    scheduler = DynamicContentRefitScheduler(owner, lambda: calls.append("fit"))

    assert scheduler.request_refit(settle_cycles=2) is True
    owner.callbacks.pop(0)()
    assert calls == []
    owner.callbacks.pop(0)()
    assert calls == []
    owner.callbacks.pop(0)()

    assert calls == ["fit"]


def test_refit_scheduler_pending_request_can_extend_settle_cycles():
    owner = FakeRefitOwner()
    calls = []
    scheduler = DynamicContentRefitScheduler(owner, lambda: calls.append("fit"))

    assert scheduler.request_refit() is True
    assert scheduler.request_refit(settle_cycles=2) is False
    owner.callbacks.pop(0)()
    assert calls == []
    owner.callbacks.pop(0)()
    assert calls == []
    owner.callbacks.pop(0)()

    assert calls == ["fit"]
