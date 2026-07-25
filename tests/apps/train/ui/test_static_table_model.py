"""Qt model boundary tests for empty and stale header queries."""

from PySide6.QtCore import Qt

from apps.train.ui.models.static_table_model import StaticTableModel


def test_zero_dimension_and_stale_header_queries_are_safe():
    empty = StaticTableModel((), ())
    assert empty.rowCount() == 0
    assert empty.columnCount() == 0
    assert empty.headerData(0, Qt.Horizontal) is None
    assert empty.headerData(0, Qt.Vertical) is None
    assert empty.headerData(99, Qt.Horizontal) is None

    populated = StaticTableModel(("a", "b"), (("one", "two"),))
    assert populated.headerData(0, Qt.Horizontal) == "a"
    assert populated.headerData(99, Qt.Horizontal) is None
    assert populated.headerData(2, Qt.Vertical) is None
    assert populated.data(populated.index(0, 1)) == "two"
    assert populated.data(populated.index(1, 1)) is None
