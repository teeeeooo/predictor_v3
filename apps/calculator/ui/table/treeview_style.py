"""Shared Tk style adapter for large scrollable Calculator data tables."""

from __future__ import annotations

from dataclasses import dataclass
import tkinter as tk
from tkinter import font as tkfont, ttk

from apps.calculator.ui.table.visual_policy import (
    DEFAULT_TABLE_VISUAL_POLICY,
    SemanticTone,
    TkTableVisualPolicy,
)

DETAIL_TREEVIEW_STYLE = "CalculatorDetail.Treeview"


@dataclass(frozen=True)
class TreeviewStyleBinding:
    """Test-visible result of binding the shared policy to one Treeview."""

    style_name: str
    heading_style_name: str
    row_height: int


def apply_treeview_style(
    tree: ttk.Treeview,
    *,
    style_name: str = DETAIL_TREEVIEW_STYLE,
    policy: TkTableVisualPolicy = DEFAULT_TABLE_VISUAL_POLICY,
) -> TreeviewStyleBinding:
    """Apply shared Calculator table visuals without owning table data."""
    style = ttk.Style(tree)
    row_height = tkfont.Font(root=tree, font=policy.body_font).metrics("linespace") + (
        2 * policy.cell_pady
    )
    heading_style = f"{style_name}.Heading"
    style.configure(
        style_name,
        background=policy.background(SemanticTone.DEFAULT),
        fieldbackground=policy.background(SemanticTone.DEFAULT),
        foreground=policy.foreground(),
        font=policy.body_font,
        rowheight=row_height,
        bordercolor=policy.divider_color,
        lightcolor=policy.divider_color,
        darkcolor=policy.divider_color,
        borderwidth=policy.outer_border_width,
        relief=tk.FLAT,
    )
    style.map(
        style_name,
        background=[("selected", policy.overlay_background("selected"))],
        foreground=[("selected", policy.foreground())],
    )
    style.configure(
        heading_style,
        background=policy.header_background,
        foreground=policy.header_foreground,
        font=policy.header_font,
        padding=(policy.cell_padx, policy.header_pady),
        bordercolor=policy.divider_color,
        lightcolor=policy.divider_color,
        darkcolor=policy.divider_color,
        borderwidth=policy.divider_width,
        relief=tk.FLAT,
    )
    style.map(heading_style, background=[("active", policy.header_background)])
    tree.configure(style=style_name)
    binding = TreeviewStyleBinding(style_name, heading_style, row_height)
    tree.table_style_binding = binding
    tree.outer_edge_policy = "flat_low_contrast"
    return binding
