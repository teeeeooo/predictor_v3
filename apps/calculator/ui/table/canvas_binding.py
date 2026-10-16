"""Canvas event/paint adapter for the existing table interaction controller."""
from weakref import WeakSet


class CanvasTableBinding:
    """Resolve pointer positions logically; bind one Canvas, not each cell.

    Selection, keyboard navigation, roles and clipboard remain controller-owned.
    Editable matrices attach one reusable native Entry to the same binding.
    """

    def __init__(self, renderer):
        self.renderer = renderer
        self._bound = WeakSet()
        self.controller = None

    def refresh(self, controller):
        self.controller = controller
        self._keys = dict(controller._key_handlers())
        renderer = self.renderer()
        editor = getattr(renderer, "editor", None)
        if editor:
            editor.controller = controller
        if renderer is None or renderer.frame in self._bound:
            return
        canvas = renderer.frame
        def clicked(event):
            if getattr(renderer, "header_action", None):
                column = renderer.header_at(event)
                if column is not None:
                    return renderer.header_action(column, bool(event.state & 1))
            return self.controller._dispatch(event, self.controller._click)
        for widget in (canvas, editor.entry) if editor else (canvas,):
            self._bound.add(widget)
            widget.bind("<Button-1>", clicked)
            widget.bind("<B1-Motion>", lambda event: self.controller._drag(event))
            for sequence in self._keys:
                widget.bind(sequence, lambda event, seq=sequence: self._keys[seq](event))
            widget.bind("<FocusOut>", lambda event: self.controller._focus_out(event))
            if editor:
                widget.bind("<KeyPress>", lambda event: self.controller._type_replace(event, self.controller.active)
                            if self.controller.active is not None else None)

    def position_at(self, event):
        renderer = self.renderer()
        if renderer is not None:
            editor = getattr(renderer, "editor", None)
            if editor and event.widget is editor.entry and getattr(event, "type", None) != "6":
                return editor.position
            return renderer.hit_test(event.x_root, event.y_root)
        return None

    def paint_selection(self, bounds, active):
        renderer = self.renderer()
        if renderer is not None:
            renderer.set_selection(bounds, active)
