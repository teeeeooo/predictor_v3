"""Small Tkinter ``after``-based debounce helper for auto-calculation.

The helper owns callback scheduling only. It does not import table widgets,
invoke calculator core, or format results.
"""

from __future__ import annotations

from typing import Callable, Protocol

__all__ = ["DebouncedAutoCalc"]


class _AfterOwner(Protocol):
    def after(self, delay_ms: int, callback: Callable[[], None]) -> str: ...

    def after_cancel(self, callback_id: str) -> None: ...


class DebouncedAutoCalc:
    """Debounce a callback through a Tk-compatible ``after`` owner."""

    def __init__(
        self,
        owner: _AfterOwner,
        callback: Callable[[], None],
        *,
        delay_ms: int = 200,
    ) -> None:
        if delay_ms < 0:
            raise ValueError("delay_ms must be non-negative")
        self._owner = owner
        self._callback = callback
        self._delay_ms = delay_ms
        self._pending_id: str | None = None
        self._disposed = False

    def schedule(self) -> None:
        """Schedule the callback, replacing a prior pending schedule."""
        if self._disposed:
            return
        self.cancel()
        self._pending_id = self._owner.after(self._delay_ms, self._run_pending)

    def cancel(self) -> None:
        """Cancel any pending callback."""
        if self._pending_id is None:
            return
        self._owner.after_cancel(self._pending_id)
        self._pending_id = None

    def flush_now(self) -> None:
        """Cancel a pending call and execute immediately unless disposed."""
        if self._disposed:
            return
        self.cancel()
        self._callback()

    def dispose(self) -> None:
        """Cancel pending work and suppress all later scheduling."""
        self.cancel()
        self._disposed = True

    def _run_pending(self) -> None:
        self._pending_id = None
        if not self._disposed:
            self._callback()
