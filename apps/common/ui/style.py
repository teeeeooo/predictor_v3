"""PySide6 style adapter for toolkit-neutral visual tokens."""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtGui import QColor, QFont

from ui_common.visual_tokens import visual_color, visual_font, visual_radius, visual_spacing


@dataclass(frozen=True)
class StatusStyle:
    """Resolved status colors for badge-like labels."""

    foreground: str
    background: str
    border: str


def color(role: str) -> str:
    """Return a CSS-ready color string for a semantic color role."""
    return visual_color(role)


def qcolor(role: str) -> QColor:
    """Return a QColor for a semantic color role."""
    return QColor(visual_color(role))


def spacing(role: str) -> int:
    """Return pixel spacing for a semantic spacing role."""
    return visual_spacing(role)


def radius(role: str) -> int:
    """Return pixel radius for a semantic radius role."""
    return visual_radius(role)


def qfont(role: str) -> QFont:
    """Return a QFont derived from a toolkit-neutral font token."""
    token = visual_font(role)
    family = token.get("family")
    font = QFont(str(family)) if family else QFont()
    font.setPointSize(int(token["size"]))
    if token.get("weight") == "bold":
        font.setBold(True)
    elif token.get("weight") == "medium":
        font.setWeight(QFont.Medium)
    return font


def app_stylesheet() -> str:
    """Return the baseline stylesheet for PySide6 Predict/Train shells."""
    return f"""
    QWidget {{
        background: {color("surface.default")};
        color: {color("text.default")};
        font-size: {visual_font("font.body")["size"]}pt;
    }}
    QFrame#Panel, QWidget#Panel {{
        background: {color("surface.panel")};
        border: 1px solid {color("border.default")};
        border-radius: {radius("radius.panel")}px;
    }}
    QLabel#PanelTitle {{
        font-weight: 700;
        color: {color("text.default")};
    }}
    QTableView {{
        background: {color("surface.panel")};
        gridline-color: {color("border.default")};
        selection-background-color: {color("table.selected")};
        selection-color: {color("text.default")};
        border: 1px solid {color("border.default")};
    }}
    QHeaderView::section {{
        background: {color("table.header")};
        color: {color("text.default")};
        border: 0;
        border-right: 1px solid {color("border.default")};
        border-bottom: 1px solid {color("border.default")};
        padding: {spacing("space.cell")}px;
        font-weight: 700;
    }}
    QPushButton {{
        background: {color("surface.panel")};
        border: 1px solid {color("border.default")};
        border-radius: {radius("radius.cell")}px;
        padding: {spacing("space.xs")}px {spacing("space.sm")}px;
    }}
    QPushButton:disabled {{
        color: {color("text.disabled")};
        background: {color("table.fixed")};
    }}
    QPushButton#PrimaryButton {{
        background: {color("accent.primary")};
        border-color: {color("accent.primary")};
        color: #FFFFFF;
        font-weight: 700;
    }}
    QPushButton#PrimaryButton:disabled {{
        color: {color("text.disabled")};
        background: {color("table.fixed")};
        border-color: {color("border.default")};
    }}
    """


def panel_stylesheet() -> str:
    """Return a focused panel/card stylesheet."""
    return (
        "QFrame#Panel, QWidget#Panel {"
        f"background: {color('surface.panel')};"
        f"border: 1px solid {color('border.default')};"
        f"border-radius: {radius('radius.panel')}px;"
        "}"
    )


def status_style(kind: str) -> StatusStyle:
    """Return colors for neutral/ready/missing/running/error/warning badges."""
    role = {
        "neutral": "status.neutral",
        "ready": "status.ready",
        "missing": "status.missing",
        "running": "status.running",
        "error": "result.error",
        "warning": "result.warning",
        "good": "result.good",
    }.get(kind, "status.neutral")
    foreground = color(role)
    return StatusStyle(
        foreground=foreground,
        background=_tint(foreground),
        border=foreground,
    )


def status_badge_stylesheet(kind: str) -> str:
    """Return stylesheet for a non-clickable status badge."""
    resolved = status_style(kind)
    return (
        f"color: {resolved.foreground};"
        f"background: {resolved.background};"
        f"border: 1px solid {resolved.border};"
        f"border-radius: {radius('radius.cell')}px;"
        f"padding: {spacing('space.xs')}px {spacing('space.sm')}px;"
    )


def table_background_role(kind: str) -> QColor:
    """Return a table cell background color for input/auto/result states."""
    role = {
        "input": "table.input",
        "fixed": "table.fixed",
        "calculated": "table.calculated",
        "result": "table.result",
        "invalid": "table.invalid",
        "warning": "table.warning",
        "selected": "table.selected",
    }.get(kind, "table.input")
    return qcolor(role)


def _tint(hex_color: str) -> str:
    """Return a light tint for badge backgrounds."""
    q = QColor(hex_color)
    if not q.isValid():
        return color("surface.panel")
    return q.lighter(185).name()
