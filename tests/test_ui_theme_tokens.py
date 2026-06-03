"""Foundation tests for ``ui/theme.py``.

These tests intentionally do not depend on PyQt5. The theme module must
remain importable on a system without PyQt5 so that schema / non-UI
code can reuse the token registry.
"""

import importlib
import sys

import pytest

from ui import theme


REQUIRED_COLOR_TOKENS = {
    "color.bg.app",
    "color.bg.card",
    "color.bg.header",
    "color.bg.cell.readonly",
    "color.bg.cell.invalid",
    "color.text.primary",
    "color.text.secondary",
    "color.text.disabled",
    "color.accent",
    "color.success",
    "color.warning",
    "color.danger",
}

REQUIRED_FONT_TOKENS = {
    "font.window_title",
    "font.card_title",
    "font.section_label",
    "font.body",
    "font.table.header",
    "font.table.cell",
    "font.caption",
}

REQUIRED_SPACING_TOKENS = {
    "space.outer",
    "space.card",
    "space.section",
    "space.row",
    "space.button",
    "space.cell",
}


def test_theme_module_imports_without_pyqt(monkeypatch):
    """Re-import ``ui.theme`` with PyQt5 hidden to confirm independence."""
    monkeypatch.setitem(sys.modules, "PyQt5", None)
    monkeypatch.delitem(sys.modules, "ui.theme", raising=False)
    module = importlib.import_module("ui.theme")
    assert hasattr(module, "color")
    assert hasattr(module, "spacing")
    assert hasattr(module, "font_token")


def test_required_color_tokens_present():
    missing = REQUIRED_COLOR_TOKENS - set(theme.COLOR_TOKENS)
    assert not missing, f"missing color tokens: {sorted(missing)}"


def test_required_font_tokens_present():
    missing = REQUIRED_FONT_TOKENS - set(theme.FONT_TOKENS)
    assert not missing, f"missing font tokens: {sorted(missing)}"


def test_required_spacing_tokens_present():
    missing = REQUIRED_SPACING_TOKENS - set(theme.SPACING_TOKENS)
    assert not missing, f"missing spacing tokens: {sorted(missing)}"


@pytest.mark.parametrize("name", sorted(REQUIRED_COLOR_TOKENS))
def test_color_value_is_hex_string(name):
    value = theme.color(name)
    assert isinstance(value, str)
    assert theme._HEX_RE.match(value), f"{name} is not 6-digit hex: {value!r}"


@pytest.mark.parametrize("name", sorted(REQUIRED_SPACING_TOKENS))
def test_spacing_value_is_positive_int(name):
    value = theme.spacing(name)
    assert isinstance(value, int)
    assert value > 0, f"{name} must be positive, got {value!r}"


@pytest.mark.parametrize("name", sorted(REQUIRED_FONT_TOKENS))
def test_font_token_structure(name):
    value = theme.font_token(name)
    assert isinstance(value, tuple)
    assert len(value) == 3, f"{name} must be (family, size_pt, weight)"
    family, size_pt, weight = value
    assert family is None or isinstance(family, str)
    assert isinstance(size_pt, int) and size_pt > 0
    assert weight in {"normal", "bold"}


def test_unknown_color_token_raises_keyerror():
    with pytest.raises(KeyError):
        theme.color("color.does.not.exist")


def test_unknown_spacing_token_raises_keyerror():
    with pytest.raises(KeyError):
        theme.spacing("space.does.not.exist")


def test_unknown_font_token_raises_keyerror():
    with pytest.raises(KeyError):
        theme.font_token("font.does.not.exist")
