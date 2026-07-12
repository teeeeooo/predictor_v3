"""Presentation-only Copy/CSV action wiring for Single result owners."""

from __future__ import annotations

from dataclasses import dataclass
import tkinter as tk
from tkinter import ttk

from apps.calculator.ui import table_csv_export


@dataclass(frozen=True)
class ResultActionButtons:
    copy_button: ttk.Button
    export_button: ttk.Button


def add_result_actions(
    action_row: tk.Misc,
    *,
    parent: tk.Misc,
    result_owner: object,
    csv_filename: str,
    surface_prefix: str,
) -> ResultActionButtons:
    """Append visible actions while leaving result shape with its owner."""
    copy_button = ttk.Button(
        action_row,
        text="Copy",
        command=lambda: _copy_result(result_owner),
    )
    copy_button.surface_role = f"{surface_prefix}_copy"
    copy_button.pack(side=tk.LEFT, padx=(6, 0))
    export_button = ttk.Button(
        action_row,
        text="Export CSV",
        command=lambda: _export_result(
            parent, result_owner=result_owner, csv_filename=csv_filename
        ),
    )
    export_button.surface_role = f"{surface_prefix}_export"
    export_button.pack(side=tk.LEFT, padx=(6, 0))
    return ResultActionButtons(copy_button, export_button)


def _copy_result(result_owner: object) -> object:
    copy_result = getattr(result_owner, "copy_result", None)
    if callable(copy_result):
        return copy_result()
    copy_table = getattr(result_owner, "copy_table", None)
    if callable(copy_table):
        return copy_table()
    copy = getattr(result_owner, "copy")
    return copy()


def _export_result(
    parent: tk.Misc, *, result_owner: object, csv_filename: str
) -> bool:
    sectioned_rows = getattr(result_owner, "sectioned_csv_rows", None)
    if callable(sectioned_rows):
        return table_csv_export.export_rows_to_csv(
            parent, csv_filename, sectioned_rows()
        )
    headers, rows = result_owner.table_export_data()
    return table_csv_export.export_table_to_csv(
        parent, csv_filename, headers, rows
    )
