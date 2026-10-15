"""Modeless session view and short Tk scheduling; state survives this widget."""
from dataclasses import replace
from tkinter import ttk

from apps.calculator.application.combinations.service import preflight, start, validate_candidate, ValidationError
from apps.calculator.ui.batch.case_table import BatchCaseTable
from apps.calculator.ui.batch.models import BatchProfileSpec, BatchColumnSpec as Column, BatchColumnRole as Role
from apps.calculator.ui.layout_constants import BATCH_DIALOG_SAFETY_MIN_SIZE, APP_WINDOW_FALLBACK_MIN_HEIGHT
from .candidates import CandidatePanel, CandidateTable
from .results import ResultsPanel
from .options import OptionsPanel
from .presentation import field_label, STATUS


class CombinationContent:
    title = "시험값 조합 계산"
    min_size = (BATCH_DIALOG_SAFETY_MIN_SIZE[0], APP_WINDOW_FALLBACK_MIN_HEIGHT)

    def __init__(self, manager, session):
        self.manager, self.session = manager, session
        self.adapter = manager.adapter
        self.pending = None
        self.disposed = False

    def build_content(self, parent):
        self.frame = ttk.Frame(parent)
        self.frame.columnconfigure(0, weight=1)
        # Reserve editing space independently of the current candidate count.
        # Without a uniform group, the result tree's requested height takes
        # most of a capped dialog and leaves only one candidate row visible.
        self.frame.rowconfigure(2, weight=2, uniform="combination_body")
        self.frame.rowconfigure(5, weight=1, uniform="combination_body")
        self.context_combo = ttk.Combobox(self.frame, values=self.manager.labels(), state="readonly")
        self.context_combo.set(self.manager.label(self.session.context))
        self.context_combo.grid(row=0, column=0, sticky="ew")
        self.context_combo.bind("<<ComboboxSelected>>", lambda e: self.manager.select(self.context_combo.current()))
        controls = ttk.Frame(self.frame)
        controls.grid(row=1, column=0, sticky="ew")
        self.reload_button = ttk.Button(controls, text="원본 입력 다시 불러오기", command=self.manager.reload)
        self.reload_button.pack(side="left")
        self.basis = ttk.Combobox(controls, state="readonly", values=self.adapter.bases(self.session.context))
        self.basis.set(self.session.context.basis)
        self.basis.pack(side="left")
        self.basis.bind("<<ComboboxSelected>>", self.change_basis)
        tabs = ttk.Notebook(self.frame)
        tabs.grid(row=2, column=0, sticky="nsew")
        candidate_frame = ttk.Frame(tabs)
        candidate_frame.columnconfigure(0, weight=1)
        candidate_frame.rowconfigure(1, weight=1)
        tabs.add(candidate_frame, text="시험점 후보")
        common_frame = ttk.Frame(tabs)
        tabs.add(common_frame, text="공통 설정")
        common_frame.columnconfigure(0, weight=1)
        common_frame.rowconfigure(0, weight=1)
        self.options_panel = OptionsPanel(tabs, self.manager, self.session.context)
        tabs.add(self.options_panel, text="실행 옵션")
        self.point_combo = ttk.Combobox(candidate_frame, state="readonly")
        self.point_combo.grid(row=0, column=0, sticky="ew")
        self.candidates = CandidatePanel(candidate_frame, self.session, self.refresh)
        self.candidates.grid(row=1, column=0, sticky="nsew")
        self.point_combo.bind("<<ComboboxSelected>>", self.select_point)
        self.points = tuple(self.adapter.draft_points(self.session.context))
        fields = {field for p in self.points for field in (p.capacity_field, p.power_field)}
        common = [dict(field=key, value=value) for key, value in self.session.context.values if key not in fields]
        self.common_keys = [row["field"] for row in common]
        for row in common:
            row["field"] = field_label(row["field"])
        self.common = None
        if common:
            self.common = CandidateTable(common_frame, BatchProfileSpec("combination_common", "공통 설정", (
                Column("field", "설정", Role.RESULT, 28), Column("value", "값", Role.INPUT)), tuple(common)), values_changed_callback=self.change_common)
            self.common.row_limit = len(common)
            self.common.grid(row=0, column=0, sticky="nsew")
        else:
            ttk.Label(common_frame, text="추가 공통 수치 설정이 없습니다.").grid(row=0, column=0, sticky="nw")
        self.status = ttk.Label(self.frame)
        self.status.grid(row=3, column=0, sticky="w")
        bar = ttk.Frame(self.frame)
        bar.grid(row=4, column=0, sticky="ew")
        self.calculate_button = ttk.Button(bar, text="계산", command=self.calculate)
        self.calculate_button.pack(side="left")
        self.cancel_button = ttk.Button(bar, text="취소", command=self.cancel)
        self.cancel_button.pack(side="left")
        self.progress = ttk.Progressbar(bar, mode="determinate")
        self.progress.pack(side="left", fill="x", expand=True)
        self.results = ResultsPanel(self.frame, self.session)
        self.results.grid(row=5, column=0, sticky="nsew")
        self.candidates.show(self.points[0])
        self.point_combo.current(0) if self.point_combo["values"] else None
        self.refresh()
        return self.frame

    def select_point(self, _event=None):
        self.candidates.show(self.points[self.point_combo.current()])

    def change_basis(self, _event=None):
        self.session.context = replace(self.session.context, basis=self.basis.get())
        self.session.changed()
        self.refresh()

    def change_common(self):
        if self.common is None or self.common.locked:
            return
        values = dict(self.session.context.values)
        values.update({key: row["value"] for key, row in zip(self.common_keys, self.common.get_text_rows())})
        self.session.context = replace(self.session.context, values=tuple(values.items()))
        self.session.changed()
        self.refresh()

    def refresh(self):
        try:
            self.points = tuple(self.adapter.points(self.session.context))
            old = self.candidates.point
            updated = next((p for p in self.points if old and p.key == old.key), self.points[0])
            if old != updated:
                self.candidates.show(updated, self.candidates.page)
            labels = []
            factors = []
            for point in self.points:
                pool = self.session.pools.get(point.key, [])
                count = sum(c.included and bool(c.capacity.strip() or c.power.strip() or c.label.strip()) for c in pool)
                invalid = 0
                if point.independent:
                    for row, candidate in enumerate(pool, 1):
                        try:
                            validate_candidate(candidate, point, row)
                        except ValidationError:
                            invalid += 1
                validation = f"입력 오류 {invalid}" if invalid else ("입력 대기" if not count and point.independent else "")
                labels.append(f"{point.key} · {count}/{len(pool)} · {point.role} {point.source} {validation}")
                if point.independent:
                    factors.append(f"{point.key} {count}")
            self.point_combo.configure(values=labels)
            self.point_combo.current(self.points.index(updated))
            snapshot = preflight(self.session, self.adapter)
            self.status.configure(text=" × ".join(factors) + f" = {snapshot.planned:,} / 10,000")
            valid = True
        except (ValueError, TypeError, KeyError) as exc:
            self.status.configure(text=str(exc))
            valid = False
        running = self.session.run is not None and self.session.run.status == "running"
        self.calculate_button.state(["!disabled" if valid and not running else "disabled"])
        self.cancel_button.state(["!disabled" if running else "disabled"])
        self.results.refresh()
        if self.session.run and self.session.run.failure:
            self.status.configure(text=self.session.run.failure)

    def calculate(self):
        self.candidates.commit()
        if self.common is not None:
            self.common.interaction_controller._commit_edit()
        try:
            run = start(self.session, self.adapter)
        except (ValueError, TypeError, KeyError) as exc:
            self.status.configure(text=str(exc))
            return
        self.lock(True)
        self.progress.configure(maximum=run.snapshot.planned, value=0)
        self.results.page = 0
        self.refresh()
        self.pending = self.frame.after(1, lambda: self.tick(run))

    def tick(self, run):
        self.pending = None
        if self.disposed or self.session.run is not run:
            return
        run.step()
        self.progress.configure(value=run.processed)
        self.status.configure(text=f"{STATUS[run.status]}: {run.processed:,}/{run.snapshot.planned:,} · 성공 {run.succeeded} · 오류 {run.failed} {run.failure}")
        if run.status == "running":
            self.pending = self.frame.after(1, lambda: self.tick(run))
        else:
            self.lock(False)
            self.refresh()

    def lock(self, locked):
        self.candidates.lock(locked)
        self.options_panel.lock(locked)
        if self.common is not None:
            self.common.locked = locked
            for i in range(self.common.row_count()):
                self.common.cell_widget((i, 1)).configure(state="readonly" if locked else "normal")
            self.common.interaction_controller.refresh()
        for widget in (self.context_combo, self.basis, self.point_combo):
            widget.configure(state="disabled" if locked else "readonly")
        self.reload_button.state(["disabled" if locked else "!disabled"])

    def cancel(self):
        if self.session.run:
            self.session.run.cancel()

    def snapshot(self):
        self.candidates.commit()
        return self.session

    def dispose(self):
        self.disposed = True
        if self.pending is not None:
            self.frame.after_cancel(self.pending)
            self.pending = None
        if self.session.run and self.session.run.status == "running":
            self.session.run.cancel()
            self.session.run.step()
