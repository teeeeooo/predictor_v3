"""Font-based natural geometry for Canvas results, independent of clipping."""
from bisect import bisect_right
from functools import lru_cache
from itertools import accumulate
import tkinter as tk
from tkinter import font as tkfont


class CanvasResultLayout:
    """Match the existing compact grid's character widths and native padding."""

    def __init__(self, master, widths, policy):
        self.policy = policy
        self.inset = policy.outer_border_width + policy.divider_width
        self.header_font = tkfont.Font(master, font=policy.header_font)
        self.body_font = tkfont.Font(master, font=policy.body_font)
        # Query platform Label defaults once, not a native widget per cell. This
        # keeps the first-show footprint compatible with the existing renderer.
        probe = tk.Label(master)
        try:
            padding = int(probe.cget("padx")) + int(probe.cget("borderwidth"))
            self.text_inset = policy.cell_padx + padding
            column_sizes = []
            for width in widths:
                sizes = []
                for font in (self.header_font, self.body_font):
                    probe.configure(width=width, font=font)
                    sizes.append(probe.winfo_reqwidth())
                column_sizes.append(max(sizes) + 2*policy.cell_padx + policy.divider_width)
            probe.configure(font=self.header_font)
            self.header_height = probe.winfo_reqheight() + 2*policy.header_pady + policy.divider_width
            probe.configure(font=self.body_font)
            self.row_height = probe.winfo_reqheight() + 2*policy.cell_pady + policy.divider_width
        finally:
            probe.destroy()
        self.xs = tuple(accumulate(column_sizes, initial=self.inset))
        self.width = sum(column_sizes)
        self.fit_text = lru_cache(maxsize=2048)(self._fit_text)

    def height(self, rows):
        return self.header_height + rows*self.row_height

    def cell_bbox(self, position):
        row, column = position
        top = self.inset if row == -1 else self.inset + self.header_height + row*self.row_height
        height = self.header_height if row == -1 else self.row_height
        return self.xs[column], top, self.xs[column+1], top+height

    def hit_test(self, x, y, rows):
        column = bisect_right(self.xs, x)-1
        row = int((y-self.inset-self.header_height)//self.row_height)
        if 0 <= column < len(self.xs)-1 and 0 <= row < rows:
            return row, column
        return None

    def visible_positions(self, bounds, rows):
        left, top, right, bottom = bounds
        first_col = max(0, bisect_right(self.xs, left)-2)
        last_col = min(len(self.xs)-1, bisect_right(self.xs, right)+1)
        body_top = self.inset + self.header_height
        first_row = max(0, int((top-body_top)//self.row_height)-1)
        last_row = min(rows, int((bottom-body_top)//self.row_height)+2)
        # One cell of overscan; header has its own, potentially different height.
        if top <= body_top + self.row_height:
            yield from ((-1, col) for col in range(first_col, last_col))
        yield from ((row, col) for row in range(first_row, last_row)
                    for col in range(first_col, last_col))

    def _fit_text(self, text, column, header):
        font = self.header_font if header else self.body_font
        width = self.xs[column+1]-self.xs[column]-2*self.text_inset-self.policy.divider_width
        # Result cells are single-line. Copy/export always retain the full value.
        text = text.replace("\n", " ").replace("\r", " ").replace("\t", " ")
        if font.measure(text) <= width:
            return text
        suffix = "…"
        if font.measure(suffix) > width:
            return ""
        low, high = 0, len(text)
        while low < high:
            mid = (low+high+1)//2
            if font.measure(text[:mid]+suffix) <= width:
                low = mid
            else:
                high = mid-1
        return text[:low]+suffix


class CanvasContentResultLayout(CanvasResultLayout):
    """Equal-width summary columns sized from the current full text.

    Natural width drives content-hug cards; allocated width follows responsive
    cards without feeding their stretched size back into natural measurement.
    """

    def update_content(self, headers, rows):
        widths = [self.header_font.measure(str(label)) for label in headers]
        for row in rows:
            widths = [max(width, self.body_font.measure(str(value)))
                      for width, value in zip(widths, row)]
        self._column_count = len(headers)
        self._natural_cell_width = max(widths) + 2*self.text_inset + self.policy.divider_width
        self.width = self._natural_cell_width*self._column_count
        self.allocate(self.width)

    def allocate(self, width):
        width = max(self.width, width)
        xs = tuple(self.inset + round(width*col/self._column_count)
                   for col in range(self._column_count+1))
        if xs != self.xs:
            self.xs = xs
            self.fit_text.cache_clear()
