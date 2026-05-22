"""Unit tests for ``ui/calculator_errors.py`` (Slice ε helpers)."""

import os

import pytest


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


from ui.calculator_errors import (  # noqa: E402
    InputValidationError,
    apply_error_style,
    bind_error_reset,
    clear_error_style,
    get_float_val,
    parse_number,
)


# ---------- parse_number ----------


def test_parse_number_strips_commas_and_returns_float():
    assert parse_number("1,234.5") == 1234.5


def test_parse_number_trims_surrounding_whitespace():
    assert parse_number(" 10 ") == 10.0


def test_parse_number_handles_negative_and_scientific():
    assert parse_number("-3.5") == -3.5
    assert parse_number("1e3") == 1000.0


def test_parse_number_raises_on_empty_string():
    with pytest.raises(ValueError, match="빈 값"):
        parse_number("")


def test_parse_number_raises_on_whitespace_only():
    with pytest.raises(ValueError, match="빈 값"):
        parse_number("   ")


def test_parse_number_raises_on_non_numeric():
    with pytest.raises(ValueError):
        parse_number("abc")


# ---------- InputValidationError ----------


def test_input_validation_error_keeps_widget_reference():
    sentinel = object()
    err = InputValidationError("nope", widget=sentinel)
    assert str(err) == "nope"
    assert err.widget is sentinel


def test_input_validation_error_widget_defaults_to_none():
    err = InputValidationError("missing")
    assert err.widget is None


# ---------- get_float_val (fake widget — no PyQt required) ----------


class _FakeLineEdit:
    """Minimal duck-typed stand-in for ``QLineEdit`` text reads."""

    def __init__(self, text):
        self._text = text
        self.stylesheet = ""

    def text(self):
        return self._text

    def setStyleSheet(self, value):
        self.stylesheet = value


def test_get_float_val_returns_float_for_positive_value():
    widget = _FakeLineEdit("3500")
    assert get_float_val({"capa": widget}, "capa", "Capa") == 3500.0


def test_get_float_val_strips_commas_and_whitespace():
    widget = _FakeLineEdit(" 1,234.5 ")
    assert get_float_val({"k": widget}, "k", "Field") == 1234.5


def test_get_float_val_empty_raises_with_widget_attached():
    widget = _FakeLineEdit("")
    with pytest.raises(InputValidationError) as exc_info:
        get_float_val({"capa": widget}, "capa", "Capa")
    assert exc_info.value.widget is widget
    assert "Capa" in str(exc_info.value)


def test_get_float_val_empty_with_allow_empty_returns_none():
    widget = _FakeLineEdit("")
    result = get_float_val(
        {"opt": widget}, "opt", "Optional", allow_empty=True
    )
    assert result is None


def test_get_float_val_non_numeric_raises_with_widget_attached():
    widget = _FakeLineEdit("abc")
    with pytest.raises(InputValidationError) as exc_info:
        get_float_val({"capa": widget}, "capa", "Capa")
    assert exc_info.value.widget is widget
    assert "올바른 숫자" in str(exc_info.value)


def test_get_float_val_zero_rejected_when_allow_zero_false():
    widget = _FakeLineEdit("0")
    with pytest.raises(InputValidationError) as exc_info:
        get_float_val({"v": widget}, "v", "V")
    assert exc_info.value.widget is widget
    assert "0보다 큰" in str(exc_info.value)


def test_get_float_val_zero_accepted_when_allow_zero_true():
    widget = _FakeLineEdit("0")
    assert get_float_val({"v": widget}, "v", "V", allow_zero=True) == 0.0


def test_get_float_val_negative_rejected_when_allow_zero_false():
    widget = _FakeLineEdit("-5")
    with pytest.raises(InputValidationError):
        get_float_val({"v": widget}, "v", "V")


# ---------- apply_error_style / clear_error_style (fake widget) ----------


def test_apply_error_style_uses_theme_color_tokens():
    from ui.theme import color

    widget = _FakeLineEdit("")
    apply_error_style(widget)
    assert color("color.danger") in widget.stylesheet
    assert color("color.bg.cell.invalid") in widget.stylesheet
    assert "border" in widget.stylesheet


def test_clear_error_style_resets_to_empty_string():
    widget = _FakeLineEdit("")
    widget.stylesheet = "border: 2px solid #E74C3C;"
    clear_error_style(widget)
    assert widget.stylesheet == ""


# ---------- bind_error_reset (PyQt5 required) ----------


def test_bind_error_reset_clears_style_on_text_change():
    pytest.importorskip("PyQt5")
    from PyQt5.QtWidgets import QApplication, QLineEdit

    app = QApplication.instance() or QApplication([])
    edit = QLineEdit()
    edit.setStyleSheet("border: 2px solid red;")
    bind_error_reset(edit)
    edit.setText("user typing")
    assert edit.styleSheet() == ""
    # Quiet linter: app must remain referenced to avoid GC.
    assert app is QApplication.instance()
