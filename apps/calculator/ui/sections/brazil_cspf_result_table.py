"""Read-only Brazil CSPF comparison and compliance result surface."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from apps.calculator.application.brazil_cspf.models import BrazilRuleDisplay
from apps.calculator.ui.layout_constants import (
    BRAZIL_CSPF_RESULT_TABLE_HEIGHT,
    BRAZIL_CSPF_RULE_LABEL_WIDTH_CHARS,
    RESULT_COMPARISON_VALUE_COLUMN_MIN_WIDTH_PX,
    RESULT_COMPARISON_VALUE_COLUMN_WIDTH_PX,
    RESULT_SCENARIO_COLUMN_MIN_WIDTH_PX,
    RESULT_SCENARIO_COLUMN_WIDTH_PX,
    RESULT_STATUS_FG,
    TABLE_BODY_FONT,
    TABLE_CELL_PADX,
    TABLE_CELL_PADY,
)
from apps.calculator.ui.table_clipboard import copy_table_to_clipboard


BRAZIL_CSPF_RESULT_COLUMNS: tuple[str, ...] = (
    "Scenario",
    "CSPF",
    "CSTL [kWh]",
    "CSEC [kWh]",
)


class BrazilCspfResultTable:
    """Content-hugging result table with core-owned rule outcomes."""

    def __init__(self, parent: tk.Widget, *, title: str = "Brazil CSPF 결과") -> None:
        self.layout_policy = "content_hug"
        self.surface_role = "brazil_cspf_result_surface"
        self.column_labels = BRAZIL_CSPF_RESULT_COLUMNS
        self.row_labels: tuple[str, ...] = ()
        self.rows: tuple[tuple[str, ...], ...] = ()
        self.rules: tuple[BrazilRuleDisplay, ...] = ()
        self.final_status: str | None = None

        self._frame = ttk.Frame(parent)
        self.title_label = ttk.Label(self._frame, text=title)
        self.title_label.pack(side=tk.TOP, anchor="w", pady=(0, 4))
        self.table = ttk.Treeview(
            self._frame,
            columns=self.column_labels,
            show="headings",
            height=BRAZIL_CSPF_RESULT_TABLE_HEIGHT,
            selectmode="browse",
        )
        self.table.surface_role = "brazil_cspf_comparison_table"
        self.table.pack(side=tk.TOP, anchor="w")
        for column in self.column_labels:
            self.table.heading(column, text=column)
            self.table.column(
                column,
                anchor=tk.CENTER,
                width=RESULT_COMPARISON_VALUE_COLUMN_WIDTH_PX,
                minwidth=RESULT_COMPARISON_VALUE_COLUMN_MIN_WIDTH_PX,
                stretch=False,
            )
        self.table.column(
            "Scenario",
            anchor=tk.W,
            width=RESULT_SCENARIO_COLUMN_WIDTH_PX,
            minwidth=RESULT_SCENARIO_COLUMN_MIN_WIDTH_PX,
            stretch=False,
        )
        self.table.bind("<Control-c>", self.copy)
        self.table.bind("<Command-c>", self.copy)
        self.table.bind("<Control-a>", self.select_all)
        self.table.bind("<Command-a>", self.select_all)

        self.rule_frame = ttk.Frame(self._frame)
        self.rule_comparisons: dict[str, ttk.Label] = {}
        self.rule_statuses: dict[str, tk.Label] = {}
        for rule_label in ("Rule 1", "Rule 2"):
            row = ttk.Frame(self.rule_frame)
            row.pack(side=tk.TOP, anchor="w", fill=tk.X, pady=(4, 0))
            ttk.Label(
                row,
                text=rule_label,
                width=BRAZIL_CSPF_RULE_LABEL_WIDTH_CHARS,
            ).pack(side=tk.LEFT, anchor="w")
            comparison_widget = ttk.Label(row, text="")
            comparison_widget.pack(side=tk.LEFT, anchor="w")
            status_widget = tk.Label(
                row,
                text="",
                anchor="w",
                foreground=RESULT_STATUS_FG,
                font=TABLE_BODY_FONT,
                padx=TABLE_CELL_PADX,
                pady=TABLE_CELL_PADY,
            )
            status_widget.pack(side=tk.LEFT, anchor="w")
            self.rule_comparisons[rule_label] = comparison_widget
            self.rule_statuses[rule_label] = status_widget

        self.final_status_label = tk.Label(
            self._frame,
            text="",
            anchor="w",
            foreground=RESULT_STATUS_FG,
            font=TABLE_BODY_FONT,
            padx=TABLE_CELL_PADX,
            pady=TABLE_CELL_PADY,
        )
        self.final_status_label.surface_role = "brazil_cspf_final_status"
        self.status_label = tk.Label(
            self._frame,
            text="",
            anchor="w",
            foreground=RESULT_STATUS_FG,
            font=TABLE_BODY_FONT,
            padx=TABLE_CELL_PADX,
            pady=TABLE_CELL_PADY,
        )
        self.status_label.surface_role = "brazil_cspf_result_status"

    def grid(self, **kwargs: object) -> None:
        self._frame.grid(**kwargs)

    def set_result(
        self,
        rows: tuple[tuple[str, ...], ...],
        rules: tuple[BrazilRuleDisplay, ...],
        *,
        final_status: str,
        status: str,
    ) -> None:
        self._show_table()
        self._clear_tree()
        self.rows = rows
        self.row_labels = tuple(row[0] for row in rows)
        self.rules = rules
        self.final_status = final_status
        self.table.configure(height=max(1, len(rows)))
        for row in rows:
            self.table.insert("", tk.END, values=row)
        self._show_rules(rules, final_status)
        self._set_status(status)

    def set_status(self, status: str) -> None:
        self._clear_tree()
        self.rows = ()
        self.row_labels = ()
        self.rules = ()
        self.final_status = None
        self.table.pack_forget()
        self.rule_frame.pack_forget()
        self.final_status_label.pack_forget()
        self._set_status(status)

    def clear(self) -> None:
        self._clear_tree()
        self.rows = ()
        self.row_labels = ()
        self.rules = ()
        self.final_status = None
        self.table.pack_forget()
        self.rule_frame.pack_forget()
        self.final_status_label.pack_forget()
        self.status_label.configure(text="")
        self.status_label.pack_forget()

    def as_text(self) -> str:
        if not self.rows:
            return str(self.status_label.cget("text"))
        lines = ["\t".join(self.column_labels)]
        lines.extend("\t".join(row) for row in self.rows)
        for rule in self.rules:
            lines.append(f"{rule.label}\t{rule.comparison}\t판정: {rule.status_text}")
        if self.final_status is not None:
            lines.append(f"최종 판정: {self.final_status}")
        status = str(self.status_label.cget("text"))
        if status:
            lines.append(status)
        return "\n".join(lines)

    def table_export_data(self) -> tuple[tuple[str, ...], tuple[tuple[str, ...], ...]]:
        if not self.rows:
            status = str(self.status_label.cget("text")) or "No result rows"
            return ("Status",), ((status,),)
        export_rows = list(self.rows)
        export_rows.extend(
            (rule.label, rule.comparison, "", rule.status_text) for rule in self.rules
        )
        if self.final_status is not None:
            export_rows.append(("Final", self.final_status, "", ""))
        return self.column_labels, tuple(export_rows)

    def copy_table(self) -> bool:
        headers, rows = self.table_export_data()
        return copy_table_to_clipboard(self.table, headers, rows)

    def copy(self, _event: tk.Event | None = None) -> str:
        self.copy_table()
        return "break"

    def select_all(self, _event: tk.Event | None = None) -> str:
        self.table.selection_set(self.table.get_children())
        return "break"

    def _show_table(self) -> None:
        if not self.table.winfo_manager():
            self.table.pack(side=tk.TOP, anchor="w")

    def _show_rules(
        self, rules: tuple[BrazilRuleDisplay, ...], final_status: str
    ) -> None:
        by_label = {rule.label: rule for rule in rules}
        for label, comparison_widget in self.rule_comparisons.items():
            rule = by_label.get(label)
            comparison_widget.configure(text=rule.comparison if rule else "")
            self.rule_statuses[label].configure(
                text=f"판정: {rule.status_text}" if rule else ""
            )
        self.rule_frame.pack(side=tk.TOP, anchor="w", fill=tk.X)
        self.final_status_label.configure(text=f"최종 판정: {final_status}")
        self.final_status_label.pack(side=tk.TOP, anchor="w", pady=(4, 0))

    def _set_status(self, status: str) -> None:
        self.status_label.configure(text=status)
        if not self.status_label.winfo_manager():
            self.status_label.pack(side=tk.TOP, anchor="w", pady=(4, 0))

    def _clear_tree(self) -> None:
        for item_id in self.table.get_children():
            self.table.delete(item_id)
