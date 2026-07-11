"""Read-only Brazil CSPF comparison and compliance result surface."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from apps.calculator.application.brazil_cspf.models import BrazilRuleDisplay
from apps.calculator.ui.layout_constants import (
    RESULT_STATUS_FG,
    RESULT_VALUE_BG,
    TABLE_BODY_FONT,
    TABLE_CELL_PADX,
    TABLE_CELL_PADY,
    TABLE_ERROR_BG,
    TABLE_PASS_BG,
)
from apps.calculator.ui.table.compact_result_grid import CompactResultGrid
from apps.calculator.ui.table.visual_policy import SemanticTone
from apps.calculator.ui.table_clipboard import copy_table_to_clipboard

from .export_adapter import copy_brazil_cspf_export
from .export_document import (
    BRAZIL_CSPF_RESULT_COLUMNS,
    BRAZIL_CSPF_RULE_COLUMNS,
    BrazilCspfExportDocument,
    build_brazil_cspf_export_document,
)


class BrazilCspfResultTable:
    """Cell-rendered result surface with core-owned rule outcomes."""

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
        self.result_grid = CompactResultGrid(
            self._frame,
            headers=BRAZIL_CSPF_RESULT_COLUMNS,
            column_widths=(12, 12, 12, 12),
            surface_role="brazil_cspf_comparison_table",
        )
        self.table = self.result_grid.frame
        self.result_value_labels = self.result_grid.value_labels
        self.rule_frame = ttk.Frame(self._frame)
        self.rule_title = ttk.Label(self.rule_frame, text="판정")
        self.rule_title.pack(side=tk.TOP, anchor="w", pady=(4, 0))
        self.rule_grid = CompactResultGrid(
            self.rule_frame,
            headers=BRAZIL_CSPF_RULE_COLUMNS,
            column_widths=(10, 30, 12, 12, 10),
            identity_columns=frozenset({0, 1}),
            surface_role="brazil_cspf_rule_table",
        )
        self.rule_table = self.rule_grid.frame
        self.rule_value_labels = self.rule_grid.value_labels
        for grid in (self.result_grid, self.rule_grid):
            grid.frame.bind("<Control-c>", self.copy)
            grid.frame.bind("<Command-c>", self.copy)
        self.final_status_label = self._status_label("brazil_cspf_final_status")
        self.status_label = self._status_label("brazil_cspf_result_status")

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
        self.rows = rows
        self.row_labels = tuple(row[0] for row in rows)
        self.rules = rules
        self.final_status = final_status
        self.result_grid.set_rows(
            rows,
            tones={
                (row, column): SemanticTone.PASS
                for row in range(len(rows))
                for column in range(1, len(BRAZIL_CSPF_RESULT_COLUMNS))
            },
        )
        rule_rows = tuple(self._rule_row(rule) for rule in rules)
        judgement_tones = {
            (index, 4): SemanticTone.PASS if rule.passed else SemanticTone.FAIL
            for index, rule in enumerate(rules)
        }
        self.rule_grid.set_rows(
            rule_rows,
            tones=judgement_tones,
        )
        self.result_grid.pack(side=tk.TOP, anchor="w")
        self.rule_grid.pack(side=tk.TOP, anchor="w")
        self.rule_frame.pack(side=tk.TOP, anchor="w", fill=tk.X)
        self.final_status_label.configure(
            text=f"최종 판정: {final_status}",
            background=TABLE_PASS_BG if final_status == "OK" else TABLE_ERROR_BG,
        )
        self.final_status_label.pack(side=tk.TOP, anchor="w", pady=(4, 0))
        self._set_status(status)

    def set_status(self, status: str) -> None:
        self.clear()
        self._set_status(status)

    def clear(self) -> None:
        self.rows = ()
        self.row_labels = ()
        self.rules = ()
        self.final_status = None
        self.result_grid.clear()
        self.rule_grid.clear()
        self.result_grid.pack_forget()
        self.rule_frame.pack_forget()
        self.final_status_label.pack_forget()
        self.status_label.configure(text="")
        self.status_label.pack_forget()

    def as_text(self) -> str:
        if not self.rows:
            return str(self.status_label.cget("text"))
        return self.export_document().as_tsv()

    def table_export_data(self) -> tuple[tuple[str, ...], tuple[tuple[str, ...], ...]]:
        if not self.rows:
            status = str(self.status_label.cget("text")) or "No result rows"
            return ("Status",), ((status,),)
        return self.column_labels, self.rows

    def export_document(self) -> BrazilCspfExportDocument:
        return build_brazil_cspf_export_document(
            self.rows, self.rules, self.final_status or "NG"
        )

    def copy_table(self) -> bool:
        if self.rows:
            return copy_brazil_cspf_export(self.table, self.export_document())
        headers, rows = self.table_export_data()
        return copy_table_to_clipboard(self.table, headers, rows)

    def copy(self, _event: tk.Event | None = None) -> str:
        self.copy_table()
        return "break"

    def select_all(self, _event: tk.Event | None = None) -> str:
        return "break"

    @staticmethod
    def _rule_row(rule: BrazilRuleDisplay) -> tuple[str, ...]:
        return (
            rule.label,
            rule.condition_text or rule.comparison,
            rule.left_value_text,
            rule.right_value_text,
            rule.status_text,
        )

    def _status_label(self, role: str) -> tk.Label:
        label = tk.Label(
            self._frame,
            text="",
            anchor="center",
            foreground=RESULT_STATUS_FG,
            background=RESULT_VALUE_BG,
            font=TABLE_BODY_FONT,
            padx=TABLE_CELL_PADX,
            pady=TABLE_CELL_PADY,
        )
        label.surface_role = role
        return label

    def _set_status(self, status: str) -> None:
        self.status_label.configure(text=status)
        if not self.status_label.winfo_manager():
            self.status_label.pack(side=tk.TOP, anchor="w", pady=(4, 0))
