"""Canvas event/paint adapter for the existing table interaction controller."""
from weakref import WeakSet


class CanvasTableBinding:
    """Resolve pointer positions logically; bind one Canvas, not each cell.

    Selection, keyboard navigation, roles and clipboard remain controller-owned.
    This pilot binds read-only result surfaces; native input bindings are retained.
    """

    def __init__(self, renderer):
        self.renderer = renderer
        self._bound = WeakSet()

    def refresh(self, controller):
        renderer = self.renderer()
        if renderer is None or renderer.frame in self._bound:
            return
        canvas = renderer.frame
        self._bound.add(canvas)
        def clicked(event):
            canvas.focus_set()
            return controller._dispatch(event, controller._click)
        canvas.bind("<Button-1>", clicked)
        canvas.bind("<B1-Motion>", controller._drag)
        for sequence, handler in controller._key_handlers():
            canvas.bind(sequence, handler)
        canvas.bind("<FocusOut>", controller._focus_out)

    def position_at(self, event):
        renderer = self.renderer()
        if renderer is not None:
            return renderer.hit_test(event.x_root, event.y_root)
        return None

    def paint_selection(self, bounds, active):
        renderer = self.renderer()
        if renderer is not None:
            renderer.set_selection(bounds, active)
