"""Bounded candidate projection over the existing spreadsheet controller."""
from tkinter import ttk

from apps.calculator.ui.batch.viewport import BatchTableViewport
from apps.calculator.ui.layout_constants import ISO_SECTION_BLOCK_GAP
from apps.calculator.ui.theme import APP_SURFACE
from .candidate_block import CandidateBlock
from .candidate_columns import PAGE_SIZE


class CandidatePanel(ttk.Frame):
    """All test-point blocks in one contained two-axis viewport."""

    def __init__(self, parent, session, changed, *, header_factory=None):
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
        self.header = header_factory(self.viewport.content, self.viewport) if header_factory else None
        self._first_point_row = int(self.header is not None and self.header.has_fields)
        if self._first_point_row:
            self.header.grid(row=0, column=0, sticky="w")

    def refresh(self, points):
        for key in tuple(self.blocks):
            if key not in {p.key for p in points}:
                self.blocks.pop(key).destroy()
        for i, point in enumerate(points):
            if point.key not in self.blocks:
                self.blocks[point.key] = CandidateBlock(self.viewport.content, self.session, point, self.changed,
                                                       viewport=self.viewport)
                self.blocks[point.key].grid(row=i+self._first_point_row, column=0, sticky="ew", pady=(0, ISO_SECTION_BLOCK_GAP))
            else:
                self.blocks[point.key].refresh(point)
        self.viewport.track_grid(self.viewport.content)

    def commit(self):
        for block in tuple(self.blocks.values()):
            block.commit()

    def lock(self, locked):
        for block in self.blocks.values():
            block.lock(locked)
