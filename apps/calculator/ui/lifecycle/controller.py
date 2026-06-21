"""Visible-content lifecycle composition for calculator profile tabs."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from apps.calculator.ui.window_measurement import (
    TkVisibleContentMeasurement,
    VisibleContentSnapshot,
)
from apps.calculator.ui.window_refit import DynamicContentRefitScheduler
from apps.calculator.ui.window_shell import ContentFitResult, TkContentHuggingShell


AfterFitHook = Callable[[ContentFitResult], None]


class ProfileVisibleContentLifecycleController:
    """Compose measurement, scheduling, and shell fit for one profile view."""

    def __init__(
        self,
        *,
        owner: Any,
        content: Any,
        scrollable: Any,
        nested_notebook: Any | None = None,
        nested_notebook_active: Callable[[], bool] | None = None,
        parent_selected_settle_cycles: int | None = None,
        nested_tab_settle_cycles: int = 1,
        detail_visibility_settle_cycles: int = 1,
        after_fit: AfterFitHook | None = None,
    ) -> None:
        self._owner = owner
        self._parent_selected_settle_cycles = self._optional_positive_cycles(
            "parent_selected_settle_cycles", parent_selected_settle_cycles
        )
        self._nested_tab_settle_cycles = self._positive_cycles(
            "nested_tab_settle_cycles", nested_tab_settle_cycles
        )
        self._detail_visibility_settle_cycles = self._positive_cycles(
            "detail_visibility_settle_cycles", detail_visibility_settle_cycles
        )
        self._scheduler = DynamicContentRefitScheduler(
            owner,
            self._fit_toplevel_to_current_content,
        )
        self._measurement = TkVisibleContentMeasurement(
            content=content,
            scrollbar=scrollable.scrollbar,
            overflow_source=scrollable,
            nested_notebook=nested_notebook,
            nested_notebook_active=nested_notebook_active,
            suppress_measurement=self._scheduler.suppress_requests,
        )
        shell = TkContentHuggingShell(owner.winfo_toplevel())
        self._content_form = shell.register_content(
            snapshot_provider=self._measurement.snapshot,
            after_fit=after_fit or self._reset_scroll_after_fit(scrollable),
        )

    @property
    def scheduler(self) -> DynamicContentRefitScheduler:
        """Expose the composed scheduler for migration diagnostics and tests."""

        return self._scheduler

    @property
    def measurement(self) -> TkVisibleContentMeasurement:
        """Expose the composed measurement for diagnostics and compatibility."""

        return self._measurement

    def preferred_initial_size(self) -> tuple[int, int]:
        return self._measurement.preferred_size()

    def vertical_overflow_delta(self) -> int:
        return self._measurement.vertical_overflow_delta()

    def snapshot(self) -> VisibleContentSnapshot:
        return self._measurement.snapshot()

    def fit_toplevel_to_current_content_once(self) -> None:
        self._fit_toplevel_to_current_content()

    def request_visible_lifecycle_refit(
        self,
        *,
        settle_cycles: int | None = None,
    ) -> bool:
        cycles = 1 if settle_cycles is None else self._positive_cycles(
            "settle_cycles", settle_cycles
        )
        return self._scheduler.request_refit(settle_cycles=cycles)

    def on_parent_tab_selected(self) -> bool:
        cycles = self._parent_selected_settle_cycles
        if cycles is None:
            return False
        return self.request_visible_lifecycle_refit(settle_cycles=cycles)

    def on_nested_tab_changed(self) -> bool:
        return self.request_visible_lifecycle_refit(
            settle_cycles=self._nested_tab_settle_cycles
        )

    def on_detail_visibility_changed(self) -> bool:
        return self.request_visible_lifecycle_refit(
            settle_cycles=self._detail_visibility_settle_cycles
        )

    def _fit_toplevel_to_current_content(self) -> None:
        self._owner.update_idletasks()
        self._content_form.fit()
        self._owner.update_idletasks()

    @staticmethod
    def _reset_scroll_after_fit(scrollable: Any) -> AfterFitHook:
        return lambda _result: scrollable.reset_scroll_position()

    @staticmethod
    def _positive_cycles(name: str, value: int) -> int:
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise ValueError(f"{name} must be a positive integer")
        return value

    @classmethod
    def _optional_positive_cycles(cls, name: str, value: int | None) -> int | None:
        if value is None:
            return None
        return cls._positive_cycles(name, value)
