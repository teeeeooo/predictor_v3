"""Natural and allocated geometry for editable matrices, including row headers."""
from bisect import bisect_left, bisect_right
from itertools import accumulate

from apps.calculator.ui.table.canvas_result_layout import CanvasResultLayout
from apps.calculator.ui.layout_constants import TABLE_SECTION_BREAK_GAP


class CanvasMatrixLayout(CanvasResultLayout):
    def __init__(self, master, widths, policy, *, row_header, weights, breaks):
        super().__init__(master, widths, policy)
        self.offset = int(row_header)
        self.weights, self.breaks = weights, breaks
        self._natural_widths = tuple(b-a for a, b in zip(self.xs, self.xs[1:]))
        self.inset = 0
        self.xs = tuple(accumulate(self._natural_widths, initial=0))
        self.tops, self.bottoms = (), ()
        self.row_height = max(self.row_height, self.header_height)
        self.resize_rows(0)

    def resize_rows(self, count):
        tops, bottoms = [0], [self.header_height]
        for row in range(count):
            tops.append(bottoms[-1] + (TABLE_SECTION_BREAK_GAP if row in self.breaks else 0))
            bottoms.append(tops[-1]+self.row_height)
        self.tops, self.bottoms = tuple(tops), tuple(bottoms)

    def height(self, rows):
        return self.header_height + rows*self.row_height + sum(TABLE_SECTION_BREAK_GAP for r in self.breaks if r < rows)

    def allocate(self, width):
        extra = max(0, width-self.width)
        total = sum(self.weights)
        accumulated = 0
        sizes = []
        for natural, weight in zip(self._natural_widths, self.weights):
            before = round(extra*accumulated/total) if total else 0
            accumulated += weight
            after = round(extra*accumulated/total) if total else 0
            sizes.append(natural+after-before)
        xs = tuple(accumulate(sizes, initial=0))
        if xs != self.xs:
            self.xs = xs
            self.fit_text.cache_clear()

    def cell_bbox(self, position):
        row, column = position
        column += self.offset
        return self.xs[column], self.tops[row+1], self.xs[column+1], self.bottoms[row+1]

    def hit_test(self, x, y, rows):
        column = bisect_right(self.xs, x)-1
        physical_row = bisect_right(self.tops, y)-1
        if (0 <= column < len(self.xs)-1 and 0 <= physical_row <= rows
                and y < self.bottoms[physical_row]):
            return physical_row-1, column-self.offset
        return None

    def visible_positions(self, bounds, rows):
        left, top, right, bottom = bounds
        first_col = max(0, bisect_right(self.xs, left)-2)
        last_col = min(len(self.xs)-1, bisect_right(self.xs, right)+1)
        first_row = max(0, bisect_right(self.bottoms, top)-1)
        last_row = min(rows+1, bisect_left(self.tops, bottom)+1)
        yield from ((row-1, col-self.offset) for row in range(first_row, last_row)
                    for col in range(first_col, last_col))
