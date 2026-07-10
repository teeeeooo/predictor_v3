"""Tkinter theme adapter for the shared predictor visual direction."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from ui_common.visual_tokens import visual_color, visual_spacing


APP_SURFACE = visual_color("surface.default")
PANEL_SURFACE = visual_color("surface.panel")
HEADER_SURFACE = visual_color("surface.header")
HOVER_SURFACE = visual_color("table.calculated")
TEXT_PRIMARY = visual_color("text.default")
TEXT_MUTED = visual_color("text.muted")
TEXT_DISABLED = visual_color("text.disabled")
BORDER = visual_color("border.default")
ACCENT = visual_color("action.primary")
ACCENT_HOVER = visual_color("action.hover")
ACCENT_PRESSED = visual_color("action.pressed")
FOCUS = visual_color("border.focus")


def apply_calculator_theme(root: tk.Misc) -> ttk.Style:
    """Apply one restrained, data-first theme to the calculator widget tree."""
    style = ttk.Style(root)
    if "clam" in style.theme_names():
        style.theme_use("clam")

    root.configure(background=APP_SURFACE)
    style.configure(
        ".",
        background=APP_SURFACE,
        foreground=TEXT_PRIMARY,
        font=("TkDefaultFont", 10),
    )
    style.configure("TFrame", background=APP_SURFACE)
    style.configure("TLabel", background=APP_SURFACE, foreground=TEXT_PRIMARY)
    style.configure(
        "TLabelframe",
        background=PANEL_SURFACE,
        bordercolor=BORDER,
        lightcolor=BORDER,
        darkcolor=BORDER,
        relief="solid",
        borderwidth=1,
        padding=8,
    )
    style.configure(
        "TLabelframe.Label",
        background=PANEL_SURFACE,
        foreground=TEXT_PRIMARY,
        font=("TkDefaultFont", 10, "bold"),
        padding=(4, 0),
    )
    style.configure(
        "TButton",
        background=PANEL_SURFACE,
        foreground=TEXT_PRIMARY,
        bordercolor=BORDER,
        focuscolor=FOCUS,
        relief="solid",
        borderwidth=1,
        padding=(10, 6),
    )
    style.map(
        "TButton",
        background=[("pressed", HEADER_SURFACE), ("active", HOVER_SURFACE)],
        foreground=[("disabled", TEXT_DISABLED)],
        bordercolor=[("focus", FOCUS), ("active", ACCENT)],
    )
    style.configure(
        "Accent.TButton",
        background=ACCENT,
        foreground=visual_color("text.on_accent"),
        bordercolor=ACCENT,
        focuscolor=FOCUS,
        padding=(12, 6),
    )
    style.map(
        "Accent.TButton",
        background=[("pressed", ACCENT_PRESSED), ("active", ACCENT_HOVER)],
        foreground=[("disabled", TEXT_DISABLED)],
    )
    style.configure(
        "TCombobox",
        fieldbackground=PANEL_SURFACE,
        background=PANEL_SURFACE,
        foreground=TEXT_PRIMARY,
        bordercolor=BORDER,
        arrowcolor=ACCENT,
        padding=4,
    )
    style.map(
        "TCombobox",
        bordercolor=[("focus", FOCUS), ("active", ACCENT)],
        fieldbackground=[("readonly", PANEL_SURFACE)],
    )
    style.configure(
        "TNotebook",
        background=APP_SURFACE,
        borderwidth=0,
        tabmargins=(0, 0, 0, 8),
    )
    style.configure(
        "TNotebook.Tab",
        background=HEADER_SURFACE,
        foreground=TEXT_MUTED,
        bordercolor=BORDER,
        padding=(14, 8),
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", PANEL_SURFACE), ("active", HOVER_SURFACE)],
        foreground=[("selected", ACCENT), ("active", TEXT_PRIMARY)],
    )
    style.configure(
        "TCheckbutton",
        background=PANEL_SURFACE,
        foreground=TEXT_PRIMARY,
        focuscolor=FOCUS,
        padding=3,
    )
    style.map("TCheckbutton", foreground=[("disabled", TEXT_DISABLED)])
    for orientation in ("Vertical", "Horizontal"):
        style.configure(
            f"{orientation}.TScrollbar",
            background=HEADER_SURFACE,
            troughcolor=APP_SURFACE,
            bordercolor=APP_SURFACE,
            arrowcolor=TEXT_MUTED,
            width=visual_spacing("space.panel"),
        )
    return style
