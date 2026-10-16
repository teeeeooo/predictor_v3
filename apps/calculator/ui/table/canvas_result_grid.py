"""Read-only result view: one native Canvas, pooled visible cell items."""
from dataclasses import dataclass
import tkinter as tk

from apps.calculator.ui.table.canvas_result_layout import CanvasResultLayout
from apps.calculator.ui.table.visual_policy import (
    AlignmentRole, DEFAULT_TABLE_VISUAL_POLICY, SemanticTone,
)
from apps.calculator.ui.table_clipboard import copy_table_to_clipboard, encode_table_tsv


@dataclass
class _PaintedCell:
    background: int
    text: int
    box: tuple = ()
    style: tuple = ()


class CanvasResultGrid:
    """Same logical result API as CompactResultGrid; no per-cell Tk widgets.

    The optional viewport owns clipping/scroll notification. The Canvas always
    requests the entire logical grid size, preserving natural window fitting.
    """

    def __init__(self, parent, *, headers, column_widths=None,
                 identity_columns=frozenset({0}), policy=DEFAULT_TABLE_VISUAL_POLICY,
                 surface_role="compact_result_grid", viewport=None):
        if not headers or (column_widths is not None and len(column_widths) != len(headers)):
            raise ValueError("result headers and column widths must be nonempty and match")
        self.headers, self.rows = tuple(headers), ()
        self.policy, self.identity_columns = policy, identity_columns
        self.column_widths = column_widths or (12,)*len(headers)
        self.surface_role, self.viewport = surface_role, viewport
        self.frame = tk.Canvas(parent, background=policy.divider_color,
            borderwidth=policy.outer_border_width, highlightthickness=policy.divider_width,
            highlightcolor=policy.focus_border_color, highlightbackground=policy.divider_color,
            takefocus=True)
        self.frame.surface_role = surface_role
        self.frame.visual_policy = policy
        self.frame.outer_edge_policy = "flat_low_contrast"
        self.frame.focus_policy = "visible"
        self.layout = CanvasResultLayout(self.frame, self.column_widths, policy)
        self.frame.configure(width=self.layout.width, height=self.layout.height(0))
        self._tones = {}
        self._selection, self._active = None, None
        self._painted, self._spares = {}, []
        self._pending = None
        self._disposed = False
        self.frame.bind("<Configure>", self.schedule)
        self.frame.bind("<Map>", self.schedule)
        self.frame.bind("<Destroy>", self._dispose)
        self.frame.bind("<Button-1>", lambda _event: self.frame.focus_force())
        self.frame.bind("<Control-c>", self.copy)
        self.frame.bind("<Command-c>", self.copy)
        self._unsubscribe = viewport.observe_view(self.schedule) if viewport else None
        self.schedule()

    def pack(self, **kwargs):
        self.frame.pack(**kwargs)

    def pack_forget(self):
        self.frame.pack_forget()

    def winfo_manager(self):
        return self.frame.winfo_manager()

    def set_rows(self, rows, *, tones=None):
        rows = tuple(tuple(row) for row in rows)
        if any(len(row) != len(self.headers) for row in rows):
            raise ValueError("result row width must match headers")
        height_changed = len(rows) != len(self.rows)
        self.rows, self._tones = rows, dict(tones or {})
        if height_changed:
            self.frame.configure(height=self.layout.height(len(rows)))
        self.schedule()

    def clear(self):
        self.set_rows(())
        self.set_selection(None, None)

    def logical_data(self):
        return self.headers, self.rows

    def as_tsv(self):
        return encode_table_tsv(self.headers, self.rows)

    def copy(self, _event=None):
        copy_table_to_clipboard(self.frame, self.headers, self.rows)
        return "break"

    def cell_tone(self, position):
        return self._tones.get(position, SemanticTone.DEFAULT)

    def cell_alignment(self, position):
        row, column = position
        if row == -1:
            return AlignmentRole.HEADER_IDENTITY if column in self.identity_columns else AlignmentRole.HEADER_VALUE
        return AlignmentRole.IDENTITY_TEXT if column in self.identity_columns else AlignmentRole.NUMERIC_RESULT

    def cell_background(self, position):
        row, column = position
        if row == -1:
            return self.policy.header_background
        if position == self._active:
            return self.policy.overlay_background("active")
        if self._selection:
            top, bottom, left, right = self._selection
            if top <= row <= bottom and left <= column <= right:
                return self.policy.overlay_background("selected")
        return self.policy.background(self.cell_tone(position))

    def set_selection(self, bounds, active):
        self._selection, self._active = bounds, active
        self.schedule()

    def hit_test(self, x_root, y_root):
        x, y = x_root-self.frame.winfo_rootx(), y_root-self.frame.winfo_rooty()
        if self.viewport:
            left, top, right, bottom = self.viewport.visible_rect(self.frame)
            if not (left <= x < right and top <= y < bottom):
                return None
        return self.layout.hit_test(x, y, len(self.rows))

    def cell_bbox(self, position, *, root=False):
        box = self.layout.cell_bbox(position)
        if root:
            x, y = self.frame.winfo_rootx(), self.frame.winfo_rooty()
            return box[0]+x, box[1]+y, box[2]+x, box[3]+y
        return box

    def reveal(self, position):
        if self.viewport:
            self.viewport.reveal_rect(self.frame, self.cell_bbox(position))

    @property
    def painted_positions(self):
        return frozenset(self._painted)

    def schedule(self, _event=None):
        if not self._disposed and self._pending is None:
            self._pending = self.frame.after_idle(self._draw)

    def _draw(self):
        self._pending = None
        bounds = (self.viewport.visible_rect(self.frame) if self.viewport else
                  (0, 0, self.layout.width+2*self.layout.inset,
                   self.layout.height(len(self.rows))+2*self.layout.inset))
        wanted = set(self.layout.visible_positions(bounds, len(self.rows)))
        for position in self._painted.keys()-wanted:
            cell = self._painted.pop(position)
            self.frame.itemconfigure(cell.background, state="hidden")
            self.frame.itemconfigure(cell.text, state="hidden")
            self._spares.append(cell)
        for position in sorted(wanted):
            cell = self._painted.get(position)
            if cell is None:
                if self._spares:
                    cell = self._spares.pop()
                    self.frame.itemconfigure(cell.background, state="normal")
                    self.frame.itemconfigure(cell.text, state="normal")
                else:
                    cell = _PaintedCell(self.frame.create_rectangle(0, 0, 0, 0, width=0),
                                        self.frame.create_text(0, 0))
                self._painted[position] = cell
            self._paint_cell(cell, position)

    def _paint_cell(self, cell, position):
        row, column = position
        header = row == -1
        value = self.headers[column] if header else self.rows[row][column]
        anchor = self.policy.anchor(self.cell_alignment(position))
        text = self.layout.fit_text("" if value is None else str(value), column, header)
        style = (self.cell_background(position), text, anchor, header)
        box = self.cell_bbox(position)
        if style != cell.style:
            self.frame.itemconfigure(cell.background, fill=style[0])
            self.frame.itemconfigure(cell.text, text=text, anchor=anchor,
                fill=self.policy.header_foreground if header else self.policy.foreground(),
                font=self.layout.header_font if header else self.layout.body_font)
        if box != cell.box or style[2:] != cell.style[2:]:
            x1, y1, x2, y2 = box
            x2 -= self.policy.divider_width
            y2 -= self.policy.divider_width
            x = (x1+self.layout.text_inset if anchor == "w" else
                 x2-self.layout.text_inset if anchor == "e" else (x1+x2)/2)
            self.frame.coords(cell.background, x1, y1, x2, y2)
            self.frame.coords(cell.text, x, (y1+y2)/2)
        cell.box, cell.style = box, style

    def _dispose(self, event):
        if event.widget is not self.frame:
            return
        self._disposed = True
        if self._pending is not None:
            self.frame.after_cancel(self._pending)
            self._pending = None
        if self._unsubscribe:
            self._unsubscribe()
        self.layout.fit_text.cache_clear()
        self._painted.clear()
        self._spares.clear()
