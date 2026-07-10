from apps.calculator.ui.batch.viewport import BatchTableViewport


class _FakeWidget:
    def __init__(self, master=None, *, reqwidth=1):
        self.master = master
        self._reqwidth = reqwidth

    def winfo_reqwidth(self):
        return self._reqwidth

    def winfo_reqheight(self):
        return 240

    def update_idletasks(self):
        return None


class _FakeCanvas:
    def __init__(self, *, bbox=(0, 0, 100, 200), width=100, height=50):
        self._bbox = bbox
        self._width = width
        self._height = height
        self.scroll_calls = []
        self.horizontal_scroll_calls = []
        self.itemconfigure_calls = []

    def bbox(self, _tag):
        return self._bbox

    def winfo_height(self):
        return self._height

    def winfo_width(self):
        return self._width

    def yview_scroll(self, units, mode):
        self.scroll_calls.append((units, mode))

    def xview_scroll(self, units, mode):
        self.horizontal_scroll_calls.append((units, mode))

    def itemconfigure(self, item, **kwargs):
        self.itemconfigure_calls.append((item, kwargs))


class _FakeToplevel:
    def __init__(self):
        self.unbind_calls = []

    def unbind(self, sequence, funcid):
        self.unbind_calls.append((sequence, funcid))


def _make_viewport(*, bbox=(0, 0, 100, 200), width=100, height=50):
    viewport = object.__new__(BatchTableViewport)
    viewport.canvas = _FakeCanvas(bbox=bbox, width=width, height=height)
    viewport.content = _FakeWidget(master=viewport)
    viewport._content_window = "content-window"
    viewport._mousewheel_toplevel = _FakeToplevel()
    viewport._mousewheel_bindings = (
        ("<MouseWheel>", "mousewheel-id"),
        ("<Button-4>", "button4-id"),
        ("<Button-5>", "button5-id"),
        ("<Shift-MouseWheel>", "shift-mousewheel-id"),
        ("<Shift-Button-4>", "shift-button4-id"),
        ("<Shift-Button-5>", "shift-button5-id"),
    )
    return viewport


def test_batch_table_viewport_preserves_requested_content_width():
    viewport = _make_viewport()
    viewport.content = _FakeWidget(master=viewport, reqwidth=640)

    viewport._sync_content_width(480)
    viewport._sync_content_width(800)

    assert viewport.canvas.itemconfigure_calls == [
        ("content-window", {"width": 640}),
        ("content-window", {"width": 800}),
    ]


def test_batch_table_viewport_reports_natural_content_size():
    viewport = _make_viewport()
    viewport.content = _FakeWidget(master=viewport, reqwidth=640)

    assert viewport.preferred_content_size() == (640, 240)


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


def test_batch_table_viewport_reports_and_routes_horizontal_overflow():
    viewport = _make_viewport(bbox=(0, 0, 640, 200), width=320, height=200)
    entry = _FakeWidget(master=viewport.content)
    event = type("Event", (), {"widget": entry, "delta": -1})()

    assert viewport.horizontal_overflow_delta() == 320
    assert viewport._on_shift_mousewheel(event) == "break"
    assert viewport.canvas.horizontal_scroll_calls == [(1, "units")]


def test_batch_table_viewport_keeps_horizontal_wheel_local():
    viewport = _make_viewport(bbox=(0, 0, 100, 50), width=100, height=50)
    internal = _FakeWidget(master=viewport.content)
    external = _FakeWidget()

    assert viewport._on_shift_mousewheel(
        type("Event", (), {"widget": external, "delta": -1})()
    ) == ""
    assert viewport._on_shift_mousewheel(
        type("Event", (), {"widget": internal, "delta": -1})()
    ) == "break"
    assert viewport.canvas.horizontal_scroll_calls == []


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
        ("<Shift-MouseWheel>", "shift-mousewheel-id"),
        ("<Shift-Button-4>", "shift-button4-id"),
        ("<Shift-Button-5>", "shift-button5-id"),
    ]
