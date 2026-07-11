"""Small Tk grid construction primitives shared by table view families."""

from __future__ import annotations

import tkinter as tk

from apps.calculator.ui.table.visual_policy import (
    AlignmentRole,
    DEFAULT_TABLE_VISUAL_POLICY,
    SemanticTone,
    TkTableVisualPolicy,
)


def create_grid_surface(
    parent: tk.Misc,
    *,
    name: str,
    focusable: bool = False,
    policy: TkTableVisualPolicy = DEFAULT_TABLE_VISUAL_POLICY,
) -> tk.Frame:
    surface = tk.Frame(
        parent,
        name=name,
        background=policy.divider_color,
        borderwidth=policy.outer_border_width,
        relief=tk.FLAT,
        takefocus=1 if focusable else 0,
        highlightthickness=policy.divider_width if focusable else 0,
        highlightcolor=policy.focus_border_color,
        highlightbackground=policy.divider_color,
    )
    surface.visual_policy = policy
    surface.outer_edge_policy = "flat_low_contrast"
    surface.focus_policy = "visible" if focusable else "cell_owned"
    return surface


def create_cell_container(
    parent: tk.Misc,
    *,
    row: int,
    column: int,
    background: str,
    surface_role: str,
    section_break: int = 0,
    policy: TkTableVisualPolicy = DEFAULT_TABLE_VISUAL_POLICY,
) -> tk.Frame:
    cell = tk.Frame(parent, background=background, borderwidth=0, relief=tk.FLAT)
    cell.grid(
        row=row,
        column=column,
        sticky="nsew",
        padx=(0, policy.divider_width),
        pady=(section_break, policy.divider_width),
    )
    cell.surface_role = surface_role
    cell.semantic_background = background
    return cell


def create_text_label(
    parent: tk.Misc,
    *,
    text: str,
    width: int | None,
    alignment: AlignmentRole,
    header: bool = False,
    tone: SemanticTone = SemanticTone.DEFAULT,
    muted: bool = False,
    policy: TkTableVisualPolicy = DEFAULT_TABLE_VISUAL_POLICY,
) -> tk.Label:
    background = (
        policy.header_background
        if header
        else policy.background(tone, editable=False)
    )
    options: dict[str, object] = {
        "text": text,
        "anchor": policy.anchor(alignment),
        "background": background,
        "foreground": policy.foreground(muted=muted),
        "font": policy.header_font if header else policy.body_font,
    }
    if width is not None:
        options["width"] = width
    label = tk.Label(parent, **options)
    label.pack(
        fill=tk.BOTH,
        expand=True,
        padx=policy.cell_padx,
        pady=policy.header_pady if header else policy.cell_pady,
    )
    label.alignment_role = alignment.value
    label.semantic_tone = tone.value
    return label
