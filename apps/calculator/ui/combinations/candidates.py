"""Bounded candidate projection over the existing spreadsheet controller."""
from tkinter import ttk

from apps.calculator.ui.batch.case_table import BatchCaseTable
from apps.calculator.ui.table.roles import CellRole

from apps.calculator.ui.batch.viewport import BatchTableViewport
from apps.calculator.ui.layout_constants import ISO_SECTION_BLOCK_GAP
from apps.calculator.ui.theme import APP_SURFACE
from .candidate_block import CandidateBlock
from .candidate_columns import PAGE_SIZE


class CandidateTable(BatchCaseTable):
    reserve_vertical_scrollbar = True
    locked = False
    row_limit = PAGE_SIZE

    def cell_role(self, position):
        if self.locked or position[0] >= self.row_limit or position[1] >= self.column_count():
            return CellRole.READONLY
        return self.cell_roles()[position[1]]

    def restore_snapshot(self, snapshot):
        if not self.locked:
            super().restore_snapshot(snapshot)

    def ensure_row_count(self, count):
        super().ensure_row_count(min(self.row_limit, count))

    def set_positions_batch(self, values):
        if self.locked:
            return False
        return super().set_positions_batch({p: v for p, v in values.items() if p[0] < self.row_limit})


class CandidatePanel(ttk.Frame):
    """All test-point blocks in one contained two-axis viewport."""

    def __init__(self, parent, session, changed):
        super().__init__(parent)
        self.session, self.changed = session, changed
        self.blocks = {}
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.paste_hint = ttk.Label(self, text=f"붙여넣기: 시험점별 현재 페이지에 최대 {PAGE_SIZE}열")
        self.paste_hint.grid(row=0, column=0, sticky="w")
        self.viewport = BatchTableViewport(self, content_name="candidate_blocks",
            content_background=APP_SURFACE, reserve_vertical_scrollbar=True)
        self.viewport.grid(row=1, column=0, sticky="nsew")

    def refresh(self, points):
        for key in tuple(self.blocks):
            if key not in {p.key for p in points}:
                self.blocks.pop(key).destroy()
        for i, point in enumerate(points):
            if point.key not in self.blocks:
                self.blocks[point.key] = CandidateBlock(self.viewport.content, self.session, point, self.changed,
                                                       viewport=self.viewport)
                self.blocks[point.key].grid(row=i, column=0, sticky="ew", pady=(0, ISO_SECTION_BLOCK_GAP))
            else:
                self.blocks[point.key].refresh(point)
        self.viewport.track_grid(self.viewport.content)

    def commit(self):
        for block in tuple(self.blocks.values()):
            block.commit()

    def lock(self, locked):
        for block in self.blocks.values():
            block.lock(locked)
