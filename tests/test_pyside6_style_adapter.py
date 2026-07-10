"""Focused tests for the PySide6 visual token adapter."""

from __future__ import annotations

from PySide6.QtGui import QColor, QFont

from apps.common.ui import style


def test_qcolor_resolves_visual_token_role():
    value = style.qcolor("surface.default")

    assert isinstance(value, QColor)
    assert value.isValid()


def test_qfont_resolves_plain_font_token():
    value = style.qfont("font.body")

    assert isinstance(value, QFont)
    assert value.pointSize() > 0


def test_status_badge_stylesheet_uses_token_values():
    sheet = style.status_badge_stylesheet("ready")

    assert "border" in sheet
    assert "padding" in sheet


def test_table_background_role_returns_qcolor():
    value = style.table_background_role("result")

    assert isinstance(value, QColor)
    assert value.isValid()


def test_table_group_label_stylesheet_uses_subtle_group_roles():
    sheet = style.table_group_label_stylesheet("result")

    assert "background" in sheet
    assert "border" in sheet


def test_app_stylesheet_includes_focus_hover_and_local_scroll_affordances():
    sheet = style.app_stylesheet()

    assert "QPushButton:hover" in sheet
    assert "QLineEdit:focus" in sheet
    assert "QScrollBar::handle" in sheet
    assert style.color("accent.primary") in sheet
