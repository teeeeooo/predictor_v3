"""Drawn editable-matrix family, backed by the existing logical table adapter."""
import tkinter as tk

from apps.calculator.ui.table.canvas_matrix_layout import CanvasMatrixLayout
from apps.calculator.ui.table.canvas_editor import CanvasCellEditor
from apps.calculator.ui.table.canvas_painter import CanvasCellPainter, CellPaint
from apps.calculator.ui.table.visual_policy import DEFAULT_TABLE_VISUAL_POLICY


class CanvasMatrixView:
    def __init__(self, parent, table, *, headers, widths, row_labels=None,
                 corner="", weights=None, breaks=frozenset(), viewport=None,
                 display_text=None):
        self.table, self.headers = table, list(headers)
        self.row_labels, self.corner = row_labels, corner
        self.viewport, self.display_text = viewport, display_text or table.text_at_position
        self.header_action = None
        self.policy = DEFAULT_TABLE_VISUAL_POLICY
        self.frame = tk.Canvas(parent, background=self.policy.divider_color,
                               borderwidth=0, highlightthickness=0, takefocus=True)
        self.frame.surface_role = "table_frame"
        self.frame.outer_edge_policy = "flat_low_contrast"
        self.layout = CanvasMatrixLayout(self.frame, widths, self.policy,
            row_header=row_labels is not None, weights=weights or (0,)*len(widths), breaks=breaks)
        self._selection, self._active = None, None
        self._count = -1
        self._pending, self._disposed = None, False
        self._painter = CanvasCellPainter(self)
        self._painted = self._painter.cells
        self.editor = CanvasCellEditor(self)
        self.frame.bind("<Configure>", self._configured)
        self.frame.bind("<Map>", self.schedule)
        self.frame.bind("<Destroy>", self._dispose)
        self._unsubscribe = viewport.observe_view(self.schedule) if viewport else None
        self.refresh()

    def refresh(self):
        count = self.table.row_count()
        if self._count != count:
            self._count = count
            self.layout.resize_rows(count)
            self.frame.configure(width=self.layout.width, height=self.layout.height(count))
        self.editor.refresh()
        self.schedule()

    def _configured(self, event):
        self.layout.allocate(event.width)
        self.editor.refresh()
        self.schedule()

    def cell_bbox(self, position, *, root=False):
        box = self.layout.cell_bbox(position)
        if root:
            x, y = self.frame.winfo_rootx(), self.frame.winfo_rooty()
            return box[0]+x, box[1]+y, box[2]+x, box[3]+y
        return box

    def _position_at(self, x_root, y_root):
        x, y = x_root-self.frame.winfo_rootx(), y_root-self.frame.winfo_rooty()
        if self.viewport:
            left, top, right, bottom = self.viewport.visible_rect(self.frame)
            if not (left <= x < right and top <= y < bottom):
                return None
        return self.layout.hit_test(x, y, self._count)

    def hit_test(self, x_root, y_root):
        position = self._position_at(x_root, y_root)
        return position if position and min(position) >= 0 else None

    def header_at(self, event):
        position = self._position_at(event.x_root, event.y_root)
        return position[1] if position and position[0] == -1 and position[1] >= 0 else None

    def reveal(self, position):
        if self.viewport:
            self.viewport.reveal_rect(self.frame, self.cell_bbox(position))

    def set_selection(self, bounds, active):
        self._selection, self._active = bounds, active
        self.editor.selection_changed(active)
        self.schedule()

    def cell_background(self, position):
        if min(position) < 0:
            return self.policy.header_background
        if position == self._active:
            return self.policy.overlay_background("active")
        if self._selection:
            top, bottom, left, right = self._selection
            if top <= position[0] <= bottom and left <= position[1] <= right:
                return self.policy.overlay_background("selected")
        return self.table.default_cell_background(position)

    def cell_paint(self, position):
        row, col = position
        header = min(position) < 0
        if row == -1:
            value = self.corner if col == -1 else self.headers[col]
        elif col == -1:
            value = self.row_labels(row)
        else:
            value = self.display_text(position)
        return CellPaint(
            self.layout.fit_text(str(value), col+self.layout.offset, header),
            self.cell_background(position), "w" if col == -1 else "center",
            str(self.layout.header_font if header else self.layout.body_font),
            self.policy.header_foreground if header else self.policy.foreground(
                muted=not self.table.cell_role(position).value == "editable"), self.layout.text_inset)

    def schedule(self, _event=None):
        if not self._disposed and self._pending is None:
            self._pending = self.frame.after_idle(self._draw)

    def _draw(self):
        self._pending = None
        if self.viewport and not self.frame.winfo_ismapped():
            return  # Map schedules a fresh projection; natural size is retained.
        bounds = (self.viewport.visible_rect(self.frame) if self.viewport else
                  (0, 0, self.layout.xs[-1], self.layout.height(self._count)))
        self._painter.draw(self.layout.visible_positions(bounds, self._count))

    @property
    def painted_positions(self):
        return frozenset(self._painted)

    def _dispose(self, event):
        if event.widget is not self.frame:
            return
        self._disposed = True
        if self._pending is not None:
            self.frame.after_cancel(self._pending)
            self._pending = None
        if self._unsubscribe:
            self._unsubscribe()
        self.editor.dispose()
        self.layout.fit_text.cache_clear()
        self._painter.clear()
