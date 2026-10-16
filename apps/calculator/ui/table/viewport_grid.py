"""Keep fixed grid cells outside a viewport unmapped, without losing data/editors."""
from itertools import accumulate


def _padding(tk, value):
    if isinstance(value, int):
        return 2 * value
    parts = tuple(map(int, tk.splitlist(value)))
    return sum(parts) if len(parts) == 2 else 2 * parts[0]


class ViewportGridCuller:
    """Opt-in for content-sized, unspanned grids; retain their full scroll extent."""

    def __init__(self, canvas):
        self.canvas = canvas
        self.grids = {}
        self.pending = None
        canvas.bind("<Configure>", self.schedule, add="+")
        canvas.bind("<Destroy>", self.dispose, add="+")

    def track(self, grid):
        if grid not in self.grids:
            self.grids[grid] = dict(cells={}, columns=(), rows=(), dirty=True)
            grid.bind("<Configure>", self.schedule, add="+")
            grid.bind("<Destroy>", lambda event: self.grids.pop(event.widget, None), add="+")
        self.grids[grid]["dirty"] = True
        self.schedule()

    def schedule(self, _event=None):
        if self.pending is None:
            self.pending = self.canvas.after_idle(self.refresh)

    def _measure(self, grid, state):
        previous = state["cells"]
        cells, widths, heights = {}, {}, {}
        for cell in grid.winfo_children():
            info = cell.grid_info() or previous.get(cell, {}).get("info")
            if not info:
                continue
            if info["columnspan"] != 1 or info["rowspan"] != 1:
                raise ValueError("Viewport grids require unspanned cells")
            width, height = cell.winfo_reqwidth(), cell.winfo_reqheight()
            if min(width, height) <= 1:
                return False  # A later grid Configure will supply settled geometry.
            column, row = info["column"], info["row"]
            widths[column] = max(widths.get(column, 0), width + _padding(grid.tk, info["padx"]) + 2*info["ipadx"])
            heights[row] = max(heights.get(row, 0), height + _padding(grid.tk, info["pady"]) + 2*info["ipady"])
            cells[cell] = dict(info=info, shown=bool(cell.winfo_manager()))
        for column in state["columns"]:
            grid.columnconfigure(column, minsize=0)
        for row in state["rows"]:
            grid.rowconfigure(row, minsize=0)
        for column, width in widths.items():
            grid.columnconfigure(column, minsize=width)
        for row, height in heights.items():
            grid.rowconfigure(row, minsize=height)
        xs = (0, *accumulate(widths.get(i, 0) for i in range(max(widths, default=-1)+1)))
        ys = (0, *accumulate(heights.get(i, 0) for i in range(max(heights, default=-1)+1)))
        inset = int(grid.cget("borderwidth")) + int(grid.cget("highlightthickness"))
        for cell in cells.values():
            column, row = cell["info"]["column"], cell["info"]["row"]
            cell["box"] = (inset+xs[column], inset+ys[row], inset+xs[column+1], inset+ys[row+1])
        state.update(cells=cells, columns=tuple(widths), rows=tuple(heights), dirty=False)
        return True

    def refresh(self):
        self.pending = None
        canvas = self.canvas
        focus = canvas.focus_get()
        focus_parents = set()
        while focus is not None:
            focus_parents.add(focus)
            focus = getattr(focus, "master", None)
        for grid, state in tuple(self.grids.items()):
            if state["dirty"] and not self._measure(grid, state):
                continue
            left = canvas.winfo_rootx() - grid.winfo_rootx()
            top = canvas.winfo_rooty() - grid.winfo_rooty()
            right, bottom = left+canvas.winfo_width(), top+canvas.winfo_height()
            for widget, cell in state["cells"].items():
                x1, y1, x2, y2 = cell["box"]
                # One cell of overscan avoids empty edges while dragging.
                shown = (widget in focus_parents or
                         (x2+(x2-x1) > left and x1-(x2-x1) < right and
                          y2+(y2-y1) > top and y1-(y2-y1) < bottom))
                if shown != cell["shown"]:
                    widget.grid() if shown else widget.grid_remove()
                    cell["shown"] = shown

    def reveal(self, widget):
        """Keyboard navigation may target an unmapped cell; reveal it before focus."""
        for grid, state in self.grids.items():
            cell = state["cells"].get(widget)
            if cell is None:
                continue
            canvas = self.canvas
            x1, y1, x2, y2 = cell["box"]
            x = grid.winfo_rootx() - canvas.winfo_rootx()
            y = grid.winfo_rooty() - canvas.winfo_rooty()
            bounds = canvas.bbox("all")
            for first, last, size, start, length, view, move in (
                (x+x1, x+x2, canvas.winfo_width(), bounds[0], bounds[2]-bounds[0], canvas.canvasx(0), canvas.xview_moveto),
                (y+y1, y+y2, canvas.winfo_height(), bounds[1], bounds[3]-bounds[1], canvas.canvasy(0), canvas.yview_moveto),
            ):
                delta = first if first < 0 else max(0, last-size)
                if delta and length:
                    move((view+delta-start)/length)
            if not cell["shown"]:
                widget.grid()
                cell["shown"] = True
                # Explicit navigation, never the resize/scroll Configure path.
                widget.update_idletasks()
            self.schedule()
            return

    def dispose(self, event):
        if event.widget is self.canvas:
            if self.pending is not None:
                self.canvas.after_cancel(self.pending)
                self.pending = None
            self.grids.clear()
