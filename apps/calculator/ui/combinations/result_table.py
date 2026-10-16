"""Bounded read-only result pages with the shared rectangular cell interaction."""
from tkinter import ttk

from apps.calculator.ui.batch.viewport import BatchTableViewport
from apps.calculator.ui.table.canvas_result_grid import CanvasResultGrid
from apps.calculator.ui.table.canvas_binding import CanvasTableBinding
from apps.calculator.ui.table.controller import TkTableController
from apps.calculator.ui.table.roles import CellRole
from apps.calculator.ui.layout_constants import TABLE_DATA_COLUMN_CHARS
from apps.calculator.ui.theme import APP_SURFACE


class ResultPageTable(ttk.Frame):
    """Render at most one 100-result page, never the entire run as widgets."""

    def __init__(self, parent):
        super().__init__(parent)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.viewport = BatchTableViewport(self, content_name="ranked_result_page",
            content_background=APP_SURFACE, reserve_vertical_scrollbar=True)
        self.viewport.grid(row=0, column=0, sticky="nsew")
        self.headers = ()
        self.rows = ()
        self.identities = ()
        self.run_id = None
        self.renderer = None
        self.interaction_controller = TkTableController(
            self, presentation=CanvasTableBinding(lambda: self.renderer))
        self.set_page(("순위", "값", "지표"), (), (), None)

    def set_page(self, headers, rows, identities, run_id):
        rows = tuple(tuple(str(value) for value in row) for row in rows)
        identities = tuple(identities)
        if len(rows) > 100:
            raise ValueError("Result pages are limited to 100 rows")
        controller = self.interaction_controller
        if (headers, rows, identities, run_id) == (self.headers, self.rows, self.identities, self.run_id):
            return
        saved = {}
        if run_id == self.run_id:
            for attr in ("anchor", "active"):
                position = getattr(controller, attr)
                if position is not None:
                    saved[attr] = (self.identities[position[0]], self.headers[position[1]])
        if headers != self.headers:
            if self.renderer:
                self.renderer.frame.destroy()
            self.renderer = CanvasResultGrid(self.viewport.content, headers=headers,
                column_widths=(TABLE_DATA_COLUMN_CHARS,) * len(headers),
                identity_columns=frozenset(range(2, len(headers))), surface_role="ranked_result_page",
                viewport=self.viewport)
            self.renderer.pack(anchor="nw")
        self.headers, self.rows, self.identities, self.run_id = headers, rows, identities, run_id
        self.renderer.set_rows(rows)
        for attr in ("anchor", "active"):
            previous = saved.get(attr)
            position = None
            if previous and previous[0] in identities and previous[1] in headers:
                position = (identities.index(previous[0]), headers.index(previous[1]))
            setattr(controller, attr, position)
        controller.refresh()
        if controller.active is None:
            self.viewport.canvas.xview_moveto(0)
            self.viewport.canvas.yview_moveto(0)

    def selected_ordinal(self):
        position = self.interaction_controller.active
        return self.identities[position[0]] if position is not None else None

    def row_count(self):
        return len(self.rows)

    def column_count(self):
        return len(self.headers)

    def cell_roles(self):
        return (CellRole.RESULT,) * self.column_count()

    def cell_role(self, position):
        return CellRole.RESULT

    def text_at_position(self, position):
        return self.rows[position[0]][position[1]]

    def set_positions_batch(self, values):
        return False

    def ensure_row_count(self, count):
        pass

    def snapshot(self):
        return self.rows

    def restore_snapshot(self, snapshot):
        pass

    def focus_widget(self, position):
        self.renderer.reveal(position)
        return self.renderer.frame

    def copy(self, event=None):
        return self.interaction_controller._copy(event)
