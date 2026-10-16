"""One test point's column actions and session/page projection."""
from dataclasses import replace
from tkinter import ttk

from apps.calculator.application.combinations.models import Candidate
from apps.calculator.application.combinations.service import validate_candidate, ValidationError
from apps.calculator.ui.layout_constants import CONTROL_GROUP_GAP, CONTROL_COMPACT_GAP
from apps.calculator.ui.metric_input_table import MetricInputTable
from .candidate_columns import CandidateColumns, PAGE_SIZE

from .presentation import point_title


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
        self.toolbar = ttk.Frame(self)
        self.toolbar.grid(row=1, column=0, sticky="w")
        self.caption = ttk.Label(self.toolbar)
        self.caption.pack(side="left", padx=(0, CONTROL_GROUP_GAP))
        self.buttons = []
        for label, callback in (("+ 열 추가", self.add), ("삭제", self.remove),
                                ("포함/제외", self.toggle), ("‹", lambda: self.move(-1)),
                                ("›", lambda: self.move(1))):
            if label == "›":
                self.page_caption = ttk.Label(self.toolbar)
                self.page_caption.pack(side="left", padx=CONTROL_COMPACT_GAP)
            button = ttk.Button(self.toolbar, text=label, command=callback, style="Compact.TButton")
            button.pack(side="left", padx=(CONTROL_GROUP_GAP if label == "‹" else CONTROL_COMPACT_GAP, 0))
            self.buttons.append(button)
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
            self.page_caption.configure(text="–")
            return
        pool = self.session.pools[self.point.key]
        count, errors = 0, []
        for i, candidate in enumerate(pool, 1):
            try:
                count += validate_candidate(candidate, self.point, i) is not None
            except ValidationError:
                errors.append(i)
        start = self.page * PAGE_SIZE
        status = f" · 오류 #{errors[0]}" + (f" 외 {len(errors)-1}" if len(errors) > 1 else "") if errors else ""
        self.caption.configure(text=f"후보 {start+1}–{min(start+PAGE_SIZE, len(pool))} · 유효 {count}/{len(pool)}{status}")
        self.page_caption.configure(text=f"{self.page+1}/{(len(pool)-1)//PAGE_SIZE+1}")
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

    def lock(self, locked):
        self.locked = locked
        for widget in self.buttons:
            widget.state(["disabled" if locked or not self.point.independent else "!disabled"])
        if self.table:
            self.table.lock(locked)
        self.refresh()
