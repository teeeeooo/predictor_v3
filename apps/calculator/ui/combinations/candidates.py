"""Bounded candidate projection over the existing spreadsheet controller."""
from dataclasses import replace
from tkinter import ttk

from apps.calculator.application.combinations.models import Candidate
from apps.calculator.application.combinations.service import validate_candidate, ValidationError
from apps.calculator.ui.batch.case_table import BatchCaseTable
from apps.calculator.ui.batch.models import BatchProfileSpec, BatchColumnSpec as Column, BatchColumnRole as Role
from apps.calculator.ui.table.roles import CellRole

PAGE_SIZE = 100


class CandidateTable(BatchCaseTable):
    reserve_vertical_scrollbar = True
    locked = False

    def cell_role(self, position):
        if self.locked or position[0] >= PAGE_SIZE or position[1] >= self.column_count():
            return CellRole.READONLY
        return self.cell_roles()[position[1]]

    def restore_snapshot(self, snapshot):
        if not self.locked:
            super().restore_snapshot(snapshot)

    def ensure_row_count(self, count):
        super().ensure_row_count(min(PAGE_SIZE, count))

    def set_positions_batch(self, values):
        if self.locked:
            return False
        return super().set_positions_batch({p: v for p, v in values.items() if p[0] < PAGE_SIZE})


class CandidatePanel(ttk.Frame):
    def __init__(self, parent, session, changed):
        super().__init__(parent)
        self.session, self.changed = session, changed
        self.point = None
        self.page = 0
        self.table = None
        self.rendered_count = 0
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        bar = ttk.Frame(self)
        bar.grid(row=0, column=0, sticky="ew")
        self.buttons = []
        for label, callback in (("행 추가", self.add), ("선택 행 삭제", self.remove),
                                ("선택 포함/제외", self.toggle), ("이전 입력", lambda: self.move(-1)),
                                ("다음 입력", lambda: self.move(1))):
            button = ttk.Button(bar, text=label, command=callback)
            button.pack(side="left")
            self.buttons.append(button)
        self.caption = ttk.Label(self)
        self.caption.grid(row=2, column=0, sticky="w")

    def commit(self):
        if self.table:
            self.table.interaction_controller._commit_edit()
            self.sync()

    def show(self, point, page=0):
        self.commit()
        self.point, self.page = point, page
        if self.table:
            self.table.destroy()
            self.table = None
        if not point.independent:
            self.caption.configure(text=f"{point.key}: {point.role} {point.source}")
            for button in self.buttons:
                button.state(["disabled"])
            return
        for button in self.buttons:
            button.state(["!disabled"])
        pool = self.session.pools.setdefault(point.key, [Candidate()])
        start = page * PAGE_SIZE
        rows = [self.row(candidate, start + i + 1) for i, candidate in enumerate(pool[start:start + PAGE_SIZE])]
        self.rendered_count = len(rows)
        spec = BatchProfileSpec("combination_candidates", point.key, (
            Column("included", "포함", Role.STATUS, 5), Column("label", "시험명", Role.INPUT),
            Column("capacity", f"Capacity [{point.capacity_unit}]", Role.INPUT),
            Column("power", "Power [W]", Role.INPUT), Column("status", "입력 상태", Role.STATUS, 25)), tuple(rows))
        self.table = CandidateTable(self, spec, values_changed_callback=self.sync)
        self.table.grid(row=1, column=0, sticky="nsew")
        self.caption.configure(text=f"입력 페이지 {page + 1} · 행 {start + 1}–{min(start + PAGE_SIZE, len(pool))} / {len(pool)} · 붙여넣기는 이 페이지의 100행까지")

    def row(self, candidate, number):
        try:
            value = validate_candidate(candidate, self.point, number)
            status = "정상" if value else ("제외" if not candidate.included else "빈 행")
        except ValidationError as exc:
            status = str(exc)
        return dict(included="✓" if candidate.included else "—", label=candidate.label,
                    capacity=candidate.capacity, power=candidate.power, status=status)

    def sync(self):
        if self.table is None or self.point is None or self.table.locked:
            return
        pool = self.session.pools[self.point.key]
        offset = self.page * PAGE_SIZE
        previous = pool[offset:offset + self.rendered_count]
        replacement = []
        for i, row in enumerate(self.table.get_text_rows()):
            old = previous[i] if i < len(previous) else Candidate()
            new = replace(old, label=row["label"], capacity=row["capacity"], power=row["power"])
            replacement.append(new)
            self.table.set_row_results(i, {"status": self.row(new, offset+i+1)["status"],
                                           "included": "✓" if new.included else "—"})
        pool[offset:offset+self.rendered_count] = replacement
        self.rendered_count = len(replacement)
        if replacement != previous:
            self.session.changed()
            self.changed()

    def selected(self):
        return sorted({r + self.page * PAGE_SIZE for r, _ in self.table.interaction_controller.selected_positions()})

    def add(self):
        self.commit()
        pool = self.session.pools[self.point.key]
        pool.append(Candidate())
        self.session.changed()
        self.show(self.point, (len(pool)-1)//PAGE_SIZE)
        self.changed()

    def remove(self):
        self.commit()
        pool = self.session.pools[self.point.key]
        indices = self.selected()
        self.table.destroy()
        self.table = None
        for index in reversed(indices):
            del pool[index]
        if not pool:
            pool.append(Candidate())
        self.session.changed()
        self.show(self.point, min(self.page, (len(pool)-1)//PAGE_SIZE))
        self.changed()

    def toggle(self):
        self.commit()
        pool = self.session.pools[self.point.key]
        for index in self.selected():
            pool[index] = replace(pool[index], included=not pool[index].included)
        self.session.changed()
        self.show(self.point, self.page)
        self.changed()

    def move(self, delta):
        self.commit()
        last = (len(self.session.pools[self.point.key])-1)//PAGE_SIZE
        self.show(self.point, max(0, min(last, self.page+delta)))

    def lock(self, locked):
        for button in self.buttons:
            button.state(["disabled" if locked or not self.point.independent else "!disabled"])
        if self.table:
            self.table.locked = locked
            for row in range(self.table.row_count()):
                for col in (1, 2, 3):
                    self.table.cell_widget((row, col)).configure(state="readonly" if locked else "normal")
            self.table.interaction_controller.refresh()
