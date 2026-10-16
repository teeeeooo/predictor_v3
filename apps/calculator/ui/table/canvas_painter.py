"""Pooled cell drawing shared by compact results and editable matrix views."""
from dataclasses import dataclass


@dataclass(frozen=True)
class CellPaint:
    text: str
    background: str
    anchor: str
    font: str
    foreground: str
    padding: int


@dataclass
class PaintedCell:
    background: int
    text: int
    box: tuple = ()
    style: CellPaint | None = None


class CanvasCellPainter:
    def __init__(self, view):
        self.view = view
        self.cells, self.spares = {}, []

    def draw(self, positions):
        canvas = self.view.frame
        wanted = set(positions)
        for position in self.cells.keys()-wanted:
            cell = self.cells.pop(position)
            canvas.itemconfigure(cell.background, state="hidden")
            canvas.itemconfigure(cell.text, state="hidden")
            self.spares.append(cell)
        for position in sorted(wanted):
            cell = self.cells.get(position)
            if cell is None:
                if self.spares:
                    cell = self.spares.pop()
                    canvas.itemconfigure(cell.background, state="normal")
                    canvas.itemconfigure(cell.text, state="normal")
                else:
                    cell = PaintedCell(canvas.create_rectangle(0, 0, 0, 0, width=0), canvas.create_text(0, 0))
                self.cells[position] = cell
            style = self.view.cell_paint(position)
            box = self.view.cell_bbox(position)
            if style != cell.style:
                canvas.itemconfigure(cell.background, fill=style.background)
                canvas.itemconfigure(cell.text, text=style.text, anchor=style.anchor,
                                     fill=style.foreground, font=style.font)
            if box != cell.box or style != cell.style:
                x1, y1, x2, y2 = box
                x2 -= self.view.policy.divider_width
                y2 -= self.view.policy.divider_width
                x = (x1+style.padding if style.anchor == "w" else
                     x2-style.padding if style.anchor == "e" else (x1+x2)/2)
                canvas.coords(cell.background, x1, y1, x2, y2)
                canvas.coords(cell.text, x, (y1+y2)/2)
            cell.box, cell.style = box, style

    def clear(self):
        self.cells.clear()
        self.spares.clear()
