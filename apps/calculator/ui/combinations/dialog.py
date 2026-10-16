"""Modeless session view and short Tk scheduling; state survives this widget."""
from dataclasses import replace
from tkinter import ttk

from apps.calculator.application.combinations.service import preflight, start
from apps.calculator.ui.layout_constants import (
    BATCH_DIALOG_SAFETY_MIN_SIZE, APP_WINDOW_FALLBACK_MIN_HEIGHT, COMBINATION_DIALOG_PREFERRED_WIDTH,
)
from .candidates import CandidatePanel
from .results import ResultsPanel
from .settings import SettingsPanel
from .presentation import context_tab_labels, STATUS


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
        self.frame.preferred_content_size = self.preferred_content_size
        self.frame.columnconfigure(0, weight=1)
        # Reserve editing space independently of the current candidate count.
        # Without a uniform group, the result table's requested height takes
        # most of a capped dialog and leaves only one candidate row visible.
        self.frame.rowconfigure(2, weight=2, uniform="combination_body")
        self.frame.rowconfigure(5, weight=1, uniform="combination_body")
        self.context_tabs = ttk.Notebook(self.frame, height=0)
        for label in context_tab_labels(self.manager.contexts):
            self.context_tabs.add(ttk.Frame(self.context_tabs), text=label)
        self.context_index = next(i for i, ctx in enumerate(self.manager.contexts)
                                  if ctx.identity == self.session.context.identity)
        self.context_tabs.select(self.context_index)
        self.context_tabs.grid(row=0, column=0, sticky="ew")
        self.context_tabs.bind("<<NotebookTabChanged>>", self.change_context)
        controls = ttk.Frame(self.frame)
        controls.grid(row=1, column=0, sticky="ew")
        self.reload_button = ttk.Button(controls, text="메인 입력으로 초기화", command=self.manager.reload)
        self.reload_button.pack(side="left")
        ttk.Label(controls, text="현재 탭의 후보·결과 초기화").pack(side="left")
        self.candidates = CandidatePanel(self.frame, self.session, self.refresh,
            header_factory=lambda parent, viewport: SettingsPanel(parent, self.session, viewport=viewport,
                changed=self.change_common, options_changed=self.manager.change_options))
        self.candidates.grid(row=2, column=0, sticky="nsew")
        self.settings = self.candidates.header
        self.points = tuple(self.adapter.draft_points(self.session.context))
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
        self.candidates.refresh(self.points)
        self.refresh()
        return self.frame

    def change_context(self, _event=None):
        if self.disposed:
            return
        index = self.context_tabs.index("current")
        if index != self.context_index:
            self.manager.select(index)

    def preferred_content_size(self):
        return max(COMBINATION_DIALOG_PREFERRED_WIDTH, self.frame.winfo_reqwidth()), self.frame.winfo_reqheight()

    def change_common(self, changes):
        if self.disposed or self.settings.locked:
            return
        values = dict(self.session.context.values)
        values.update(changes)
        self.session.context = replace(self.session.context, values=tuple(values.items()))
        self.session.changed()
        self.refresh()

    def refresh(self):
        try:
            self.points = tuple(self.adapter.points(self.session.context))
            self.candidates.refresh(self.points)
            factors = []
            for point in self.points:
                pool = self.session.pools.get(point.key, [])
                count = sum(c.included and bool(c.capacity.strip() or c.power.strip() or c.label.strip()) for c in pool)
                if point.independent:
                    factors.append(f"{point.key} {count}")
            snapshot = preflight(self.session, self.adapter)
            self.status.configure(text=" × ".join(factors) + f" = {snapshot.planned:,} / 10,000")
            valid = True
        except (ValueError, TypeError, KeyError) as exc:
            self.status.configure(text=str(exc).replace(" · 행 ", " · 후보 #"))
            valid = False
        running = self.session.run is not None and self.session.run.status == "running"
        self.settings.refresh(self.points)
        self.calculate_button.state(["!disabled" if valid and not running else "disabled"])
        self.cancel_button.state(["!disabled" if running else "disabled"])
        self.reload_button.state(["!disabled" if not running and self.manager.reload_source() is not None else "disabled"])
        self.results.refresh()
        if self.session.run and self.session.run.failure:
            self.status.configure(text=self.session.run.failure)

    def calculate(self):
        self.candidates.commit()
        self.settings.commit()
        try:
            run = start(self.session, self.adapter)
        except (ValueError, TypeError, KeyError) as exc:
            self.status.configure(text=str(exc).replace(" · 행 ", " · 후보 #"))
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
        self.settings.lock(locked, self.points)
        for index in range(len(self.manager.contexts)):
            self.context_tabs.tab(index, state="disabled" if locked and index != self.context_index else "normal")
        self.reload_button.state(["disabled" if locked else "!disabled"])

    def cancel(self):
        if self.session.run:
            self.session.run.cancel()

    def snapshot(self):
        self.candidates.commit()
        self.settings.commit()
        return self.session

    def dispose(self):
        self.disposed = True
        if self.pending is not None:
            self.frame.after_cancel(self.pending)
            self.pending = None
        if self.session.run and self.session.run.status == "running":
            self.session.run.cancel()
            self.session.run.step()
