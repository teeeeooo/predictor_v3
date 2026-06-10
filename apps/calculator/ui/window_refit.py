"""Dynamic content refit scheduling for Tkinter windows.

This module owns event-loop orchestration only. Geometry calculation and
application stay in ``apps.calculator.ui.window_geometry``.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Callable, Protocol


class RefitEventOwner(Protocol):
    """Small protocol for Tk widgets used by the refit scheduler."""

    def after_idle(self, callback: Callable[[], None]) -> str: ...

    def update_idletasks(self) -> None: ...


class DynamicContentRefitScheduler:
    """Coalesce dynamic content refit requests into one settled callback."""

    def __init__(
        self,
        owner: RefitEventOwner,
        refit_callback: Callable[[], None],
    ) -> None:
        self._owner = owner
        self._refit_callback = refit_callback
        self._pending = False
        self._running = False
        self._suppress_count = 0
        self._settle_remaining = 0

    @property
    def is_pending(self) -> bool:
        return self._pending

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def is_suppressed(self) -> bool:
        return self._suppress_count > 0

    def request_refit(self, *, settle_cycles: int = 1) -> bool:
        """Request one settled refit.

        Returns ``True`` when a new callback was scheduled. Requests made while
        suppressed, pending, or running are intentionally ignored to avoid
        recursive geometry loops.
        """
        if self.is_suppressed or self._pending or self._running:
            if self._pending:
                self._settle_remaining = max(self._settle_remaining, settle_cycles)
            return False
        self._pending = True
        self._settle_remaining = max(1, settle_cycles)
        self._owner.after_idle(self._schedule_settled_refit)
        return True

    @contextmanager
    def suppress_requests(self):
        """Temporarily ignore refit requests caused by measurement side effects."""
        self._suppress_count += 1
        try:
            yield
        finally:
            self._suppress_count -= 1

    def _schedule_settled_refit(self) -> None:
        if not self._pending:
            return
        self._owner.update_idletasks()
        if self._settle_remaining > 1:
            self._settle_remaining -= 1
            self._owner.after_idle(self._schedule_settled_refit)
            return
        self._owner.after_idle(self._run_refit)

    def _run_refit(self) -> None:
        if not self._pending or self._running:
            return
        self._running = True
        try:
            self._refit_callback()
        finally:
            self._running = False
            self._pending = False
            self._settle_remaining = 0
