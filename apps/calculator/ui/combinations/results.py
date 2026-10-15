"""Paged read-only rankings and snapshot detail/export actions."""
from dataclasses import asdict, is_dataclass
import json
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

from apps.calculator.ui.table.treeview_style import apply_treeview_style
from apps.calculator.ui.layout_constants import RESULT_COMPARISON_VALUE_COLUMN_WIDTH_PX, BATCH_DIALOG_SAFETY_MIN_SIZE
from apps.calculator.ui.batch_dialogs.shell import BatchDialogShell
from apps.calculator.ui import table_csv_export
from .export import export_rows, context_json
from .presentation import STATUS


class ResultsPanel(ttk.Frame):
    def __init__(self, parent, session):
        super().__init__(parent)
        self.session, self.page = session, 0
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.caption = ttk.Label(self)
        self.caption.grid(row=0, column=0, sticky="w")
        self.tree = ttk.Treeview(self, show="headings", height=6, selectmode="extended")
        self.tree.grid(row=1, column=0, sticky="nsew")
        apply_treeview_style(self.tree)
        for orient, row, column, axis in (("vertical", 1, 1, "y"), ("horizontal", 2, 0, "x")):
            scroll = ttk.Scrollbar(self, orient=orient, command=getattr(self.tree, axis+"view"))
            scroll.grid(row=row, column=column, sticky="ns" if axis=="y" else "ew")
            self.tree.configure(**{axis+"scrollcommand": scroll.set})
        for binding in ("<Control-c>", "<Command-c>"):
            self.tree.bind(binding, self.copy)
        bar = ttk.Frame(self)
        bar.grid(row=3, column=0, sticky="w")
        self.actions = {}
        for label, callback in (("이전 결과", lambda: self.move(-1)), ("다음 결과", lambda: self.move(1)),
                                ("선택 결과 상세", self.detail), ("전체 결과 CSV 저장", self.export)):
            button = ttk.Button(bar, text=label, command=callback)
            button.pack(side="left")
            self.actions[label] = button
        self.refresh()

    def refresh(self):
        run = self.session.run
        available = run is not None and run.status != "running" and bool(run.results)
        for label in ("선택 결과 상세", "전체 결과 CSV 저장"):
            self.actions[label].state(["!disabled" if available else "disabled"])
        if run is None:
            self.caption.configure(text="계산 전")
            return
        selected = self.tree.selection()
        columns = ("순위", "값", "지표", "단위", "기준", *(p.key for p in run.snapshot.independent_points), "상태")
        self.tree.configure(columns=columns)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=RESULT_COMPARISON_VALUE_COLUMN_WIDTH_PX, stretch=False)
        self.tree.delete(*self.tree.get_children())
        ranked = run.ranked()
        self.page = min(self.page, max(0, (len(ranked)-1)//100))
        for rank, row in ranked[self.page*100:(self.page+1)*100]:
            measurements = [pool[i] for pool, i in zip(run.snapshot.pools, row.selections)]
            labels = [f"#{value.number}" + (f" · {value.label}" if value.label else "") for value in measurements]
            score = row.score
            values = (rank or "", score.value if score else "", score.metric if score else "",
                      score.units if score else "", run.snapshot.context.basis, *labels,
                      "정상" if score else f"{row.error_code}: {row.error_message}")
            self.tree.insert("", "end", iid=str(row.ordinal), values=values)
        self.tree.selection_set([key for key in selected if self.tree.exists(key)])
        self.caption.configure(text=f"{STATUS[run.status]} · {'부분 결과 · ' if run.partial else ''}{'입력 변경됨(stale) · ' if self.session.stale else ''}"
                               f"성공 {run.succeeded} / 오류 {run.failed} · {run.processed}/{run.snapshot.planned} · 페이지 {self.page+1}")

    def move(self, delta):
        self.page = max(0, self.page+delta)
        self.refresh()

    def copy(self, _event=None):
        rows = [self.tree.item(key, "values") for key in self.tree.selection()]
        if rows:
            self.clipboard_clear()
            self.clipboard_append("\n".join("\t".join(map(str, row)) for row in rows))
        return "break"

    def detail(self):
        selected = self.tree.selection()
        if not selected:
            return
        run = self.session.run
        row = next(row for row in run.results if row.ordinal == int(selected[0]))
        try:
            result = run.detail(row)
            payload = asdict(result) if is_dataclass(result) else result
            text = json.dumps(payload, ensure_ascii=False, indent=2, default=str)
        except Exception as exc:
            text = f"{type(exc).__name__}: {exc}"
        measurements = {point.key: asdict(pool[i]) for point, pool, i in zip(run.snapshot.independent_points, run.snapshot.pools, row.selections)}
        provenance = f"Run {run.snapshot.id} / 조합 {row.ordinal} / {run.status}\nstale={self.session.stale}, partial={run.partial}\n"
        text = provenance + json.dumps(measurements, ensure_ascii=False, indent=2) + "\n" + context_json(run.snapshot) + "\n\n" + text
        BatchDialogShell(self.winfo_toplevel(), DetailContent(text))

    def export(self):
        run = self.session.run
        if run is None or run.status == "running" or not run.results:
            return
        try:
            headers, rows = export_rows(run, stale=self.session.stale)
            table_csv_export.export_table_to_csv(self.winfo_toplevel(), "calculator_combinations.csv", headers, rows)
        except (OSError, ValueError) as exc:
            messagebox.showerror("CSV 저장 실패", str(exc), parent=self.winfo_toplevel())


class DetailContent:
    title = "실행 당시 입력 · 상세 결과"
    min_size = BATCH_DIALOG_SAFETY_MIN_SIZE

    def __init__(self, text):
        self.text = text

    def build_content(self, parent):
        widget = scrolledtext.ScrolledText(parent, wrap="word")
        widget.insert("1.0", self.text)
        widget.configure(state="disabled")
        return widget

    def snapshot(self):
        return None

    def dispose(self):
        pass
