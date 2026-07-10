"""Contract tests for the toolkit-neutral visual token foundation."""

from __future__ import annotations

import importlib
import sys
from collections.abc import Mapping

import pytest


REQUIRED_COLOR_ROLES = {
    "action.primary",
    "surface.header",
    "surface.default",
    "surface.panel",
    "text.default",
    "text.disabled",
    "text.on_accent",
    "text.muted",
    "border.default",
    "border.focus",
    "accent.primary",
    "table.header",
    "table.input",
    "table.fixed",
    "table.calculated",
    "table.result",
    "table.invalid",
    "table.warning",
    "table.selected",
    "table.focus",
    "result.good",
    "result.warning",
    "result.error",
    "status.neutral",
    "status.ready",
    "status.missing",
    "status.running",
}
REQUIRED_SPACING_ROLES = {
    "space.xs",
    "space.sm",
    "space.md",
    "space.lg",
    "space.outer",
    "space.panel",
    "space.row",
    "space.cell",
}
REQUIRED_RADIUS_ROLES = {"radius.cell", "radius.panel", "radius.pill"}
REQUIRED_FONT_ROLES = {
    "font.body",
    "font.label",
    "font.window_title",
    "font.panel_title",
    "font.table.header",
    "font.table.cell",
    "font.caption",
    "font.mono_label",
}


def _tokens():
    return importlib.import_module("ui_common.visual_tokens")


def test_module_import_does_not_require_ui_toolkits(monkeypatch):
    qt_binding = "Py" + "Qt5"
    monkeypatch.setitem(sys.modules, qt_binding, None)
    monkeypatch.setitem(sys.modules, "tkinter", None)
    monkeypatch.delitem(sys.modules, "ui_common.visual_tokens", raising=False)

    module = importlib.import_module("ui_common.visual_tokens")

    assert callable(module.visual_color)
    assert sys.modules[qt_binding] is None
    assert sys.modules["tkinter"] is None


@pytest.mark.parametrize(
    ("kind", "required"),
    [
        ("color", REQUIRED_COLOR_ROLES),
        ("spacing", REQUIRED_SPACING_ROLES),
        ("radius", REQUIRED_RADIUS_ROLES),
        ("font", REQUIRED_FONT_ROLES),
    ],
)
def test_required_roles_exist_and_are_unique(kind, required):
    roles = _tokens().visual_roles(kind)
    assert isinstance(roles, tuple)
    assert required <= set(roles)
    assert len(roles) == len(set(roles))


@pytest.mark.parametrize("role", sorted(REQUIRED_COLOR_ROLES))
def test_visual_color_returns_string(role):
    assert isinstance(_tokens().visual_color(role), str)


@pytest.mark.parametrize("role", sorted(REQUIRED_SPACING_ROLES))
def test_visual_spacing_returns_positive_int(role):
    value = _tokens().visual_spacing(role)
    assert isinstance(value, int)
    assert value > 0


@pytest.mark.parametrize("role", sorted(REQUIRED_RADIUS_ROLES))
def test_visual_radius_returns_non_negative_int(role):
    value = _tokens().visual_radius(role)
    assert isinstance(value, int)
    assert value >= 0


@pytest.mark.parametrize("role", sorted(REQUIRED_FONT_ROLES))
def test_visual_font_returns_plain_mapping(role):
    value = _tokens().visual_font(role)
    assert isinstance(value, Mapping)
    assert {"family", "size", "weight", "role"} <= set(value)


@pytest.mark.parametrize(
    ("helper", "missing_role"),
    [
        ("visual_color", "table.missing"),
        ("visual_spacing", "space.missing"),
        ("visual_radius", "radius.missing"),
        ("visual_font", "font.missing"),
    ],
)
def test_unknown_roles_raise_keyerror(helper, missing_role):
    with pytest.raises(KeyError):
        getattr(_tokens(), helper)(missing_role)


def test_unknown_kind_raises_keyerror():
    with pytest.raises(KeyError):
        _tokens().visual_roles("missing")
