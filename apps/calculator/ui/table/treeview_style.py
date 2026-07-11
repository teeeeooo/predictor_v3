"""Shared Tk style adapter for large scrollable Calculator data tables."""

from __future__ import annotations

from dataclasses import dataclass
import tkinter as tk
from tkinter import font as tkfont, ttk

from apps.calculator.ui.layout_constants import (
    RESULT_VALUE_BG,
    TABLE_BODY_FONT,
    TABLE_CELL_PADX,
    TABLE_CELL_PADY,
    TABLE_GRID_COLOR,
    TABLE_HEADER_BG,
    TABLE_HEADER_FG,
    TABLE_HEADER_FONT,
    TABLE_HEADER_PADY,
    TABLE_SELECTED_BG,
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
) -> TreeviewStyleBinding:
    """Apply shared Calculator table visuals without owning table data."""
    style = ttk.Style(tree)
    row_height = tkfont.Font(root=tree, font=TABLE_BODY_FONT).metrics("linespace") + (
        2 * TABLE_CELL_PADY
    )
    heading_style = f"{style_name}.Heading"
    style.configure(
        style_name,
        background=RESULT_VALUE_BG,
        fieldbackground=RESULT_VALUE_BG,
        foreground=TABLE_HEADER_FG,
        font=TABLE_BODY_FONT,
        rowheight=row_height,
        bordercolor=TABLE_GRID_COLOR,
        lightcolor=TABLE_GRID_COLOR,
        darkcolor=TABLE_GRID_COLOR,
        borderwidth=0,
        relief=tk.FLAT,
    )
    style.map(
        style_name,
        background=[("selected", TABLE_SELECTED_BG)],
        foreground=[("selected", TABLE_HEADER_FG)],
    )
    style.configure(
        heading_style,
        background=TABLE_HEADER_BG,
        foreground=TABLE_HEADER_FG,
        font=TABLE_HEADER_FONT,
        padding=(TABLE_CELL_PADX, TABLE_HEADER_PADY),
        bordercolor=TABLE_GRID_COLOR,
        lightcolor=TABLE_GRID_COLOR,
        darkcolor=TABLE_GRID_COLOR,
        borderwidth=1,
        relief=tk.FLAT,
    )
    style.map(heading_style, background=[("active", TABLE_HEADER_BG)])
    tree.configure(style=style_name)
    binding = TreeviewStyleBinding(style_name, heading_style, row_height)
    tree.table_style_binding = binding
    tree.outer_edge_policy = "flat_low_contrast"
    return binding
