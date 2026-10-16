"""Paged read-only rankings and snapshot detail/export actions."""
from dataclasses import asdict, is_dataclass
import json
from tkinter import ttk, scrolledtext, messagebox

from apps.calculator.ui.layout_constants import BATCH_DIALOG_SAFETY_MIN_SIZE
from apps.calculator.ui.batch_dialogs.shell import BatchDialogShell
from apps.calculator.ui import table_csv_export
from .export import export_rows, export_filename, context_json
from .result_table import ResultPageTable
from .presentation import STATUS


class ResultsPanel(ttk.Frame):
    def __init__(self, parent, session):
        super().__init__(parent)
        self.session, self.page = session, 0
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.caption = ttk.Label(self)
        self.caption.grid(row=0, column=0, sticky="w")
        self.table = ResultPageTable(self)
        self.table.grid(row=1, column=0, sticky="nsew")
        bar = ttk.Frame(self)
        bar.grid(row=2, column=0, sticky="w")
        self.actions = {}
        for label, callback in (("이전 결과", lambda: self.move(-1)), ("다음 결과", lambda: self.move(1)),
                                ("선택 범위 복사", self.copy), ("선택 결과 상세", self.detail), ("전체 결과 CSV 저장", self.export)):
            button = ttk.Button(bar, text=label, command=callback)
            button.pack(side="left")
            self.actions[label] = button
        self.refresh()

    def refresh(self):
        run = self.session.run
        available = run is not None and run.status != "running" and bool(run.results)
        for label in ("선택 범위 복사", "선택 결과 상세", "전체 결과 CSV 저장"):
            self.actions[label].state(["!disabled" if available else "disabled"])
        if run is None:
            self.table.set_page(("순위", "값", "지표"), (), (), None)
            self.caption.configure(text="계산 전")
            return
        columns = ("순위", "값", "지표", "단위", *(p.key for p in run.snapshot.independent_points), "상태")
        rows, identities = [], []
        ranked = run.ranked()
        self.page = min(self.page, max(0, (len(ranked)-1)//100))
        for rank, row in ranked[self.page*100:(self.page+1)*100]:
            measurements = [pool[i] for pool, i in zip(run.snapshot.pools, row.selections)]
            labels = [f"#{value.number}" for value in measurements]
            score = row.score
            values = (rank or "", score.value if score else "", score.metric if score else "",
                      score.units if score else "", *labels,
                      "정상" if score else f"{row.error_code}: {row.error_message}")
            rows.append(values)
            identities.append(row.ordinal)
        self.table.set_page(columns, rows, identities, run.snapshot.id)
        self.caption.configure(text=f"{STATUS[run.status]} · {'부분 결과 · ' if run.partial else ''}{'입력 변경됨 · 재계산 필요 · ' if self.session.stale else ''}"
                               f"성공 {run.succeeded} / 오류 {run.failed} · {run.processed}/{run.snapshot.planned} · 페이지 {self.page+1}")

    def move(self, delta):
        self.page = max(0, self.page+delta)
        self.refresh()

    def copy(self, _event=None):
        return self.table.copy(_event)

    def detail(self):
        selected = self.table.selected_ordinal()
        if selected is None:
            return
        run = self.session.run
        row = next(row for row in run.results if row.ordinal == selected)
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
            headers, rows = export_rows(run)
            table_csv_export.export_table_to_csv(self.winfo_toplevel(), export_filename(run, stale=self.session.stale), headers, rows)
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
