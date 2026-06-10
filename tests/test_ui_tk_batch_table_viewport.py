from ui_tk.batch.viewport import BatchTableViewport


class _FakeWidget:
    def __init__(self, master=None):
        self.master = master


class _FakeCanvas:
    def __init__(self, *, bbox=(0, 0, 100, 200), height=50):
        self._bbox = bbox
        self._height = height
        self.scroll_calls = []

    def bbox(self, _tag):
        return self._bbox

    def winfo_height(self):
        return self._height

    def yview_scroll(self, units, mode):
        self.scroll_calls.append((units, mode))


class _FakeToplevel:
    def __init__(self):
        self.unbind_calls = []

    def unbind(self, sequence, funcid):
        self.unbind_calls.append((sequence, funcid))


def _make_viewport(*, bbox=(0, 0, 100, 200), height=50):
    viewport = object.__new__(BatchTableViewport)
    viewport.canvas = _FakeCanvas(bbox=bbox, height=height)
    viewport.content = _FakeWidget(master=viewport)
    viewport._mousewheel_toplevel = _FakeToplevel()
    viewport._mousewheel_bindings = (
        ("<MouseWheel>", "mousewheel-id"),
        ("<Button-4>", "button4-id"),
        ("<Button-5>", "button5-id"),
    )
    return viewport


def test_batch_table_viewport_routes_entry_and_label_wheel_to_canvas():
    viewport = _make_viewport()
    cell = _FakeWidget(master=viewport.content)
    entry = _FakeWidget(master=cell)
    result_label = _FakeWidget(master=cell)

    entry_event = type("Event", (), {"widget": entry, "delta": -1})()
    label_event = type("Event", (), {"widget": result_label, "num": 4})()

    assert viewport._on_mousewheel(entry_event) == "break"
    assert viewport._on_mousewheel(label_event) == "break"
    assert viewport.canvas.scroll_calls == [(1, "units"), (-1, "units")]


def test_batch_table_viewport_ignores_external_wheel_and_breaks_without_overflow():
    viewport = _make_viewport()
    internal = _FakeWidget(master=viewport.content)
    external = _FakeWidget()

    external_event = type("Event", (), {"widget": external, "delta": -1})()
    assert viewport._on_mousewheel(external_event) == ""

    viewport.canvas = _FakeCanvas(bbox=(0, 0, 100, 50), height=50)
    internal_event = type("Event", (), {"widget": internal, "delta": -1})()
    assert viewport._on_mousewheel(internal_event) == "break"
    assert viewport.canvas.scroll_calls == []


def test_batch_table_viewport_reports_overflow_delta_from_canvas_bbox():
    viewport = _make_viewport(bbox=(0, 10, 100, 210), height=75)

    assert viewport.vertical_overflow_delta() == 125

    viewport.canvas = _FakeCanvas(bbox=None, height=75)
    assert viewport.vertical_overflow_delta() == 0


def test_batch_table_viewport_unbinds_only_on_own_destroy_event():
    viewport = _make_viewport()
    child_event = type("Event", (), {"widget": viewport.content})()

    viewport._unbind_mousewheel(child_event)

    assert viewport._mousewheel_bindings
    assert viewport._mousewheel_toplevel.unbind_calls == []

    own_event = type("Event", (), {"widget": viewport})()
    viewport._unbind_mousewheel(own_event)

    assert viewport._mousewheel_bindings == ()
    assert viewport._mousewheel_toplevel.unbind_calls == [
        ("<MouseWheel>", "mousewheel-id"),
        ("<Button-4>", "button4-id"),
        ("<Button-5>", "button5-id"),
    ]
