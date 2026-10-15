"""One test point's column actions and session/page projection."""
from dataclasses import replace
import tkinter as tk
from tkinter import ttk

from apps.calculator.application.combinations.models import Candidate
from apps.calculator.application.combinations.service import validate_candidate, ValidationError
from apps.calculator.ui.layout_constants import CONTROL_GROUP_GAP
from apps.calculator.ui.metric_input_table import MetricInputTable
from .candidate_columns import CandidateColumns, PAGE_SIZE


def point_title(point):
    return {"35_full": "STD", "35_half": "HALF"}.get(point.key, point.key)


class CandidateBlock(ttk.Frame):
    def __init__(self, parent, session, point, changed):
        super().__init__(parent)
        self.session, self.point, self.changed = session, point, changed
        self.page = 0
        self.table = None
        self.inactive_header = None
        self.locked = False
        self.rendered_count = 0
        self.columnconfigure(0, weight=1)
        bar = ttk.Frame(self)
        bar.grid(row=2, column=0, sticky="w")
        self.buttons = []
        for label, callback in (("열 추가", self.add), ("선택 열 삭제", self.remove),
                                ("포함/제외", self.toggle), ("이전 페이지", lambda: self.move(-1)),
                                ("다음 페이지", lambda: self.move(1))):
            button = ttk.Button(bar, text=label, command=callback)
            button.pack(side="left")
            self.buttons.append(button)
        self.names_var = tk.BooleanVar(self, False)
        self.names_button = ttk.Checkbutton(bar, text="시험명", variable=self.names_var, command=self.show_names)
        self.names_button.pack(side="left", padx=(CONTROL_GROUP_GAP, 0))
        self.caption = ttk.Label(self)
        self.caption.grid(row=1, column=0, sticky="w")
        self.show()

    def commit(self):
        if self.table:
            self.table.interaction_controller._commit_edit()
            self.sync()

    def show(self):
        if self.inactive_header:
            self.inactive_header.destroy()
            self.inactive_header = None
        if self.table:
            self.table.destroy()
            self.table = None
        if self.point.independent:
            pool = self.session.pools.setdefault(self.point.key, [Candidate()])
            self.page = min(self.page, (len(pool)-1)//PAGE_SIZE)
            start = self.page * PAGE_SIZE
            candidates = pool[start:start+PAGE_SIZE]
            self.rendered_count = len(candidates)
            self.table = CandidateColumns(self, self.point, candidates, start, self.sync, title=point_title(self.point))
            self.table.grid(row=0, column=0, sticky="w")
            if self.names_var.get():
                self.table.names(True)
        else:
            self.inactive_header = MetricInputTable(self, columns=(), rows=(),
                editable_cells={}, corner_label=point_title(self.point))
            self.inactive_header.grid(row=0, column=0, sticky="w")
        self.lock(self.locked)
        self.refresh()

    def sync(self):
        if not self.table or self.locked:
            return
        pool = self.session.pools[self.point.key]
        offset = self.page * PAGE_SIZE
        replacement = self.table.candidates
        previous = pool[offset:offset+self.rendered_count]
        pool[offset:offset+self.rendered_count] = replacement
        self.rendered_count = len(replacement)
        if replacement != previous:
            self.session.changed()
            self.changed()

    def refresh(self, point=None):
        if point is not None and point != self.point:
            self.commit()
            self.point = point
            self.show()
            return
        if not self.point.independent:
            self.caption.configure(text=f"{self.point.role} · {self.point.source or '독립 시험점 아님'}")
            return
        pool = self.session.pools[self.point.key]
        count, errors = 0, []
        for i, candidate in enumerate(pool, 1):
            try:
                count += validate_candidate(candidate, self.point, i) is not None
            except ValidationError:
                errors.append(i)
        start = self.page * PAGE_SIZE
        status = f" · 오류 후보 #{errors[0]} 외 {len(errors)-1}개" if errors else ""
        self.caption.configure(text=f"후보 #{start+1}–#{min(start+PAGE_SIZE, len(pool))} · 유효 {count} / 전체 {len(pool)} · 페이지 {self.page+1} · 붙여넣기 최대 100열{status}")
        for button, disabled in ((self.buttons[3], self.page == 0),
                                 (self.buttons[4], start+PAGE_SIZE >= len(pool))):
            button.state(["disabled" if disabled or self.locked else "!disabled"])

    def selected(self):
        return sorted({column for _, column in self.table.interaction_controller.selected_positions()})

    def add(self):
        if self.locked or not self.point.independent:
            return
        self.commit()
        pool = self.session.pools[self.point.key]
        pool.append(Candidate())
        self.page = (len(pool)-1)//PAGE_SIZE
        self.session.changed()
        self.show()
        self.table.select_column(self.table.column_count()-1)
        self.changed()

    def remove(self):
        if self.locked or not self.table:
            return
        self.commit()
        selected = self.selected()
        if not selected:
            return
        pool = self.session.pools[self.point.key]
        for index in reversed(selected):
            del pool[self.page*PAGE_SIZE+index]
        if not pool:
            pool.append(Candidate())
        self.session.changed()
        self.show()
        self.changed()

    def toggle(self):
        if self.locked or not self.table:
            return
        self.commit()
        before = self.table.snapshot()
        updated = list(before)
        for index in self.selected():
            updated[index] = replace(updated[index], included=not updated[index].included)
        if tuple(updated) != before:
            self.table.restore_snapshot(updated)
            self.table.interaction_controller._undo.push(before)

    def move(self, delta):
        if self.locked or not self.table:
            return
        self.commit()
        last = (len(self.session.pools[self.point.key])-1)//PAGE_SIZE
        target = max(0, min(last, self.page+delta))
        if target != self.page:
            self.page = target
            self.show()

    def show_names(self):
        if self.table:
            self.table.names(self.names_var.get())

    def lock(self, locked):
        self.locked = locked
        for widget in (*self.buttons, self.names_button):
            widget.state(["disabled" if locked or not self.point.independent else "!disabled"])
        if self.table:
            self.table.lock(locked)
        self.refresh()
