"""Read-only detail table for section-local result snapshots."""

from __future__ import annotations

from collections.abc import Iterable

import tkinter as tk
from tkinter import ttk

from ui_tk.layout_constants import (
    RESULT_STATUS_FG,
    TABLE_BODY_FONT,
    TABLE_CELL_PADX,
    TABLE_CELL_PADY,
    TABLE_DATA_COLUMN_CHARS,
)
from ui_tk.sections.result_snapshot import ResultSnapshot

DETAIL_RESULT_COLUMNS = (
    "Profile/Scenario",
    "Point",
    "Capacity [W]",
    "Power [W]",
    "EER",
    "CSPF/ISEER",
    "CSTL [kWh]",
    "CSEC [kWh]",
    "Status",
)


class DetailResultTable:
    """Section-local read-only detail surface backed by result snapshots."""

    def __init__(self, parent: tk.Widget, *, title: str = "상세 결과") -> None:
        self.layout_policy = "responsive"
        self.surface_role = "detail_result_surface"
        self.column_labels = DETAIL_RESULT_COLUMNS
        self.rows: tuple[tuple[str, ...], ...] = ()

        self._frame = ttk.Frame(parent)
        self.title_label = ttk.Label(self._frame, text=title)
        self.title_label.pack(side=tk.TOP, anchor="w", pady=(0, 4))

        self.table = ttk.Treeview(
            self._frame,
            columns=self.column_labels,
            show="headings",
            height=1,
            selectmode="browse",
        )
        self.table.surface_role = "detail_result_table"
        self.table.pack(side=tk.TOP, fill=tk.X)
        for column in self.column_labels:
            self.table.heading(column, text=column)
            self.table.column(
                column,
                anchor=tk.CENTER,
                width=TABLE_DATA_COLUMN_CHARS * 9,
                minwidth=80,
                stretch=True,
            )
        self.table.column("Profile/Scenario", anchor=tk.W, width=180, minwidth=150)
        self.table.column("Point", anchor=tk.W, width=110, minwidth=90)
        self.table.column("Status", anchor=tk.W, width=150, minwidth=120)
        self.table.bind("<Control-c>", self.copy)
        self.table.bind("<Command-c>", self.copy)

        self.status_label = tk.Label(
            self._frame,
            text="",
            anchor="w",
            foreground=RESULT_STATUS_FG,
            font=TABLE_BODY_FONT,
            padx=TABLE_CELL_PADX,
            pady=TABLE_CELL_PADY,
        )
        self.status_label.surface_role = "detail_result_status"

    def grid(self, **kwargs) -> None:
        self._frame.grid(**kwargs)

    def grid_remove(self) -> None:
        self._frame.grid_remove()

    def is_visible(self) -> bool:
        return bool(self._frame.winfo_manager())

    def set_snapshots(self, snapshots: Iterable[ResultSnapshot]) -> None:
        rows = tuple(_rows_from_snapshots(snapshots))
        self._clear_tree()
        self.rows = rows
        if self.status_label.winfo_manager():
            self.status_label.pack_forget()
        if not self.table.winfo_manager():
            self.table.pack(side=tk.TOP, fill=tk.X)
        self.table.configure(height=max(1, len(rows)))
        for row in rows:
            self.table.insert("", tk.END, values=row)
        if not rows:
            self.set_status("상세 결과 없음")

    def set_status(self, status: str) -> None:
        self._clear_tree()
        self.rows = ()
        self.table.pack_forget()
        self.status_label.configure(text=status)
        if not self.status_label.winfo_manager():
            self.status_label.pack(side=tk.TOP, fill=tk.X)

    def table_rows(self) -> tuple[tuple[str, ...], ...]:
        return self.rows

    def as_text(self) -> str:
        if not self.rows:
            return self.status_label.cget("text")
        lines = ["\t".join(self.column_labels)]
        lines.extend("\t".join(row) for row in self.rows)
        return "\n".join(lines)

    def copy(self, _event: tk.Event | None = None) -> str:
        contents = self.as_text()
        if contents:
            self.table.clipboard_clear()
            self.table.clipboard_append(contents)
        return "break"

    def _clear_tree(self) -> None:
        for item_id in self.table.get_children():
            self.table.delete(item_id)


def _rows_from_snapshots(
    snapshots: Iterable[ResultSnapshot],
) -> list[tuple[str, ...]]:
    rows = []
    for snapshot in snapshots:
        if not snapshot.points and snapshot.status:
            rows.append(_row(snapshot, None))
            continue
        for point in snapshot.points:
            rows.append(_row(snapshot, point))
    return rows


def _row(snapshot: ResultSnapshot, point: dict | None) -> tuple[str, ...]:
    summary = snapshot.summary
    return (
        snapshot.label,
        _text_value(point, "point") if point is not None else "-",
        _number_value(point, "capacity", 1, strip=True) if point is not None else "-",
        _number_value(point, "power", 1, strip=True) if point is not None else "-",
        _number_value(point, "eer", 2, strip=False) if point is not None else "-",
        _number_value(summary, "cspf", 3, strip=False),
        _number_value(summary, "cstl_kwh", 1, strip=False),
        _number_value(summary, "csec_kwh", 1, strip=False),
        snapshot.status or "-",
    )


def _text_value(row: dict | None, key: str) -> str:
    if row is None:
        return "-"
    value = row.get(key)
    return "-" if value is None else str(value)


def _number_value(
    row: dict | None, key: str, decimals: int, *, strip: bool
) -> str:
    if row is None:
        return "-"
    value = row.get(key)
    if value is None:
        return "-"
    try:
        text = f"{float(value):.{decimals}f}"
    except (TypeError, ValueError):
        return "-"
    if strip:
        text = text.rstrip("0").rstrip(".")
    return text or "0"
