"""Shared validation / error-styling helpers for the calculator UI.

Slice ε of `docs/designs/2026-05-22-calculator-ui-module-boundary.md`.
This module owns:

- :class:`InputValidationError` — the validation exception carrying the
  offending widget reference for red-border styling and focus
  restoration.
- :func:`parse_number` — locale-tolerant numeric parsing (commas
  stripped, whitespace trimmed).
- :func:`bind_error_reset` — connect a ``QLineEdit.textChanged`` slot
  that clears the error border once the user starts editing.
- :func:`apply_error_style` / :func:`clear_error_style` — error
  visualisation that uses :mod:`ui.theme` color tokens (no inline
  hex).
- :func:`get_float_val` — text-to-float read with the same Korean
  error messages and ``allow_empty`` / ``allow_zero`` semantics that
  the previous ``CalculatorWindow._get_float_val`` provided.

PyQt5 is a soft dependency: the helpers act on duck-typed widgets that
expose ``text()`` / ``setStyleSheet()`` / ``textChanged.connect()``.
The module imports PyQt5 only inside the bind helper so that pure
non-Qt callers (unit tests) can exercise the parsing / styling
helpers without PyQt5 installed.
"""

from __future__ import annotations

from typing import Mapping, Optional

from ui.theme import color as theme_color

__all__ = [
    "InputValidationError",
    "parse_number",
    "bind_error_reset",
    "apply_error_style",
    "clear_error_style",
    "get_float_val",
]


class InputValidationError(Exception):
    """Validation failure with optional offending widget reference."""

    def __init__(self, message: str, widget=None):
        super().__init__(message)
        self.widget = widget


def parse_number(text: str) -> float:
    """Parse user-typed numeric text. Strips commas and whitespace."""
    clean_text = text.replace(",", "").strip()
    if not clean_text:
        raise ValueError("빈 값입니다.")
    return float(clean_text)


def bind_error_reset(widget) -> None:
    """Clear the error border the moment the user starts editing."""
    widget.textChanged.connect(lambda: widget.setStyleSheet(""))


def apply_error_style(widget) -> None:
    """Paint a red border + soft red background on an error widget."""
    widget.setStyleSheet(
        f"border: 2px solid {theme_color('color.danger')}; "
        f"background-color: {theme_color('color.bg.cell.invalid')};"
    )


def clear_error_style(widget) -> None:
    """Reset the stylesheet, removing any error border."""
    widget.setStyleSheet("")


def get_float_val(
    widgets: Mapping[str, object],
    key: str,
    field_name: str,
    *,
    allow_empty: bool = False,
    allow_zero: bool = False,
) -> Optional[float]:
    """Read a float from ``widgets[key]``.

    Mirrors the behaviour of the previous
    ``CalculatorWindow._get_float_val(widget, field_name, allow_empty,
    allow_zero)``. The widget reference is attached to any raised
    :class:`InputValidationError` so the caller can apply the error
    style to that exact field.
    """
    widget = widgets[key]
    text = widget.text().strip()
    if not text:
        if allow_empty:
            return None
        raise InputValidationError(
            f"'{field_name}' 항목을 입력해주세요.", widget
        )

    try:
        val = parse_number(text)
    except ValueError:
        raise InputValidationError(
            f"'{field_name}' 필드에 올바른 숫자를 입력해주세요.", widget
        )

    if not allow_zero and val <= 0:
        raise InputValidationError(
            f"'{field_name}' 필드는 0보다 큰 값이어야 합니다.", widget
        )

    return val
