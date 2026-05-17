"""Reusable spreadsheet-like table model and helpers for PyQt5 UIs.

This module is the first concrete slice of the global contract in
``docs/ui/SPREADSHEET_TABLE_CONTRACT.md``. It is intentionally
view-agnostic: it provides a ``QAbstractTableModel`` subclass and
pure-Python helpers (TSV parse/format, point-dict conversion) that any
``QTableView`` in this project can attach to without further work.

Scope of this first slice:

- Editable cells, stored as strings so user input round-trips without
  coercion loss.
- TSV copy of a selected rectangle and TSV paste anchored at a
  top-left cell (out-of-bounds rows / columns silently dropped, per
  contract §7).
- Cell clear by selection (contract §8).
- Single-level undo: every ``set_cell`` / ``paste_tsv`` /
  ``clear_cells`` call pushes a full-grid snapshot, ``undo()`` pops the
  most recent one. Redo and cross-table undo are out of scope.
- Numeric invalid-cell detection via :meth:`is_cell_invalid`
  (contract §11).
- Conversion to a ``{column_label: (capacity, power)}`` point dict for
  the AHRI / EN14825 / ISO16358 column-shaped layout.

Out of scope (deferred to follow-up slices):

- Redo, cross-table undo, undo persistence.
- Read-only / auto-column flagging and background color rendering.
- ``QStyledItemDelegate`` editor lifecycle and 1-click dropdown
  wiring.
- View-side selection model, keybindings, Tab / Enter navigation,
  paste path isolation in the controller.
- AHRI / EN14825 / ISO16358 UI integration.

PyQt5 import guard: the pure-Python helpers (``parse_tsv``,
``format_tsv``, ``points_from_grid``, ``coerce_numeric``) work without
PyQt5. The ``SpreadsheetTableModel`` class requires PyQt5; when PyQt5
is missing the class is exposed as ``None`` so this module still
imports cleanly in non-GUI environments and tests can skip via
``pytest.importorskip``.
"""

from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

try:
    from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt
    _PYQT_AVAILABLE = True
except ImportError:  # pragma: no cover - exercised only on PyQt5-less envs
    _PYQT_AVAILABLE = False


# ---------------------------------------------------------------------------
# Pure-Python helpers (no PyQt5 dependency)
# ---------------------------------------------------------------------------


def parse_tsv(text: str) -> List[List[str]]:
    """Parse a TSV string into a list-of-lists grid.

    Excel / Sheets clipboard payloads usually end with a trailing
    newline; the trailing blank row is dropped. CRLF / CR line endings
    are normalized to LF. Empty input returns ``[]``.

    Raises:
        TypeError: when ``text`` is not a string.
    """
    if not isinstance(text, str):
        raise TypeError("TSV input must be a string")
    if text == "":
        return []
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    rows = normalized.split("\n")
    if rows and rows[-1] == "":
        rows = rows[:-1]
    return [row.split("\t") for row in rows]


def format_tsv(grid: Sequence[Sequence[Any]]) -> str:
    """Format a 2D iterable of values as a TSV string with trailing ``\\n``.

    ``None`` values are emitted as the empty string. The empty grid
    returns the empty string. Excel / Sheets accept the trailing
    newline on paste.
    """
    rows: List[str] = []
    for row in grid:
        cells = ["" if cell is None else str(cell) for cell in row]
        rows.append("\t".join(cells))
    if not rows:
        return ""
    return "\n".join(rows) + "\n"


def coerce_numeric(value: Any) -> Optional[float]:
    """Return ``float(value)`` if it parses; otherwise ``None``.

    Empty strings and ``None`` return ``None``. Whitespace around a
    numeric value is tolerated. Non-string non-numeric inputs return
    ``None`` instead of raising so the helper can be used in a
    fast-fail validation path without try/except boilerplate.
    """
    if value is None:
        return None
    if not isinstance(value, str):
        try:
            return float(value)
        except (TypeError, ValueError):
            return None
    stripped = value.strip()
    if stripped == "":
        return None
    try:
        return float(stripped)
    except ValueError:
        return None


def points_from_grid(
    column_labels: Sequence[str],
    grid: Sequence[Sequence[str]],
    capacity_row: int = 0,
    power_row: int = 1,
) -> Dict[str, Tuple[float, float]]:
    """Convert a (rows × columns) grid into ``{col: (capacity, power)}``.

    Args:
        column_labels: Per-column labels (e.g.
            ``["A_Full", "B_Full", "B_Low", "E_Int", "F_Low"]``).
        grid: 2D sequence of cell values (strings).
        capacity_row: Row index that holds capacity values.
        power_row: Row index that holds power values.

    Returns:
        Mapping of column label to ``(capacity, power)`` tuple of
        floats.

    Raises:
        ValueError: if a capacity or power cell is empty or
            non-numeric, or if any row's width disagrees with
            ``len(column_labels)``.
    """
    required_rows = max(capacity_row, power_row) + 1
    if len(grid) < required_rows:
        raise ValueError(
            f"grid must have at least {required_rows} rows; got {len(grid)}"
        )
    capacity_values = grid[capacity_row]
    power_values = grid[power_row]
    if len(capacity_values) != len(column_labels) or len(power_values) != len(column_labels):
        raise ValueError(
            f"grid row width must equal len(column_labels) = "
            f"{len(column_labels)}; got capacity={len(capacity_values)}, "
            f"power={len(power_values)}"
        )
    out: Dict[str, Tuple[float, float]] = {}
    for col_idx, col_label in enumerate(column_labels):
        cap = coerce_numeric(capacity_values[col_idx])
        pwr = coerce_numeric(power_values[col_idx])
        if cap is None or pwr is None:
            raise ValueError(
                f"column {col_label!r} has non-numeric capacity or power: "
                f"capacity={capacity_values[col_idx]!r}, "
                f"power={power_values[col_idx]!r}"
            )
        out[col_label] = (cap, pwr)
    return out


# ---------------------------------------------------------------------------
# Qt-dependent class
# ---------------------------------------------------------------------------


if _PYQT_AVAILABLE:

    class SpreadsheetTableModel(QAbstractTableModel):
        """Editable ``QAbstractTableModel`` for spreadsheet-like input.

        Cell values are stored as strings. Numeric validity is exposed
        through :meth:`is_cell_invalid` so delegates can paint an error
        indicator without blocking further edits (contract §11).
        """

        def __init__(
            self,
            row_labels: Sequence[str],
            column_labels: Sequence[str],
            parent=None,
        ):
            super().__init__(parent)
            if not row_labels:
                raise ValueError("row_labels must be non-empty")
            if not column_labels:
                raise ValueError("column_labels must be non-empty")
            self._row_labels: List[str] = list(row_labels)
            self._column_labels: List[str] = list(column_labels)
            self._cells: List[List[str]] = [
                ["" for _ in column_labels] for _ in row_labels
            ]
            # Snapshot-based undo. Each entry is (label, grid_snapshot).
            self._undo_stack: List[Tuple[str, List[List[str]]]] = []
            self._max_undo_depth = 64

        # ---- Qt overrides ----

        def rowCount(self, parent=QModelIndex()):
            return 0 if parent.isValid() else len(self._row_labels)

        def columnCount(self, parent=QModelIndex()):
            return 0 if parent.isValid() else len(self._column_labels)

        def data(self, index, role=Qt.DisplayRole):
            if not index.isValid():
                return None
            if role in (Qt.DisplayRole, Qt.EditRole):
                return self._cells[index.row()][index.column()]
            return None

        def setData(self, index, value, role=Qt.EditRole):
            if role != Qt.EditRole or not index.isValid():
                return False
            self._push_snapshot("edit")
            self._cells[index.row()][index.column()] = (
                "" if value is None else str(value)
            )
            self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])
            return True

        def flags(self, index):
            base = super().flags(index)
            if index.isValid():
                return base | Qt.ItemIsEditable
            return base

        def headerData(self, section, orientation, role=Qt.DisplayRole):
            if role != Qt.DisplayRole:
                return None
            if orientation == Qt.Horizontal and 0 <= section < len(self._column_labels):
                return self._column_labels[section]
            if orientation == Qt.Vertical and 0 <= section < len(self._row_labels):
                return self._row_labels[section]
            return None

        # ---- Plain Python helpers ----

        @property
        def row_labels(self) -> List[str]:
            return list(self._row_labels)

        @property
        def column_labels(self) -> List[str]:
            return list(self._column_labels)

        def set_cell(self, row: int, col: int, value: Any) -> None:
            self._check_bounds(row, col)
            self._push_snapshot("set_cell")
            self._cells[row][col] = "" if value is None else str(value)
            idx = self.index(row, col)
            self.dataChanged.emit(idx, idx, [Qt.DisplayRole, Qt.EditRole])

        def get_cell(self, row: int, col: int) -> str:
            self._check_bounds(row, col)
            return self._cells[row][col]

        def to_grid(self) -> List[List[str]]:
            return [list(row) for row in self._cells]

        def is_cell_invalid(self, row: int, col: int) -> bool:
            self._check_bounds(row, col)
            value = self._cells[row][col]
            if value == "":
                return False
            return coerce_numeric(value) is None

        def selected_to_tsv(self, selection: Iterable[Tuple[int, int]]) -> str:
            cells = list(selection)
            if not cells:
                return ""
            rows = [r for r, _ in cells]
            cols = [c for _, c in cells]
            top, bottom = min(rows), max(rows)
            left, right = min(cols), max(cols)
            # Validate bounding rectangle corners.
            self._check_bounds(top, left)
            self._check_bounds(bottom, right)
            grid = [self._cells[r][left:right + 1] for r in range(top, bottom + 1)]
            return format_tsv(grid)

        def paste_tsv(self, top_row: int, top_col: int, tsv: str) -> int:
            grid = parse_tsv(tsv)
            if not grid:
                return 0
            self._push_snapshot("paste")
            cells_written = 0
            last_row = top_row
            last_col = top_col
            for r_offset, row in enumerate(grid):
                target_row = top_row + r_offset
                if target_row < 0 or target_row >= len(self._row_labels):
                    continue
                for c_offset, value in enumerate(row):
                    target_col = top_col + c_offset
                    if target_col < 0 or target_col >= len(self._column_labels):
                        continue
                    self._cells[target_row][target_col] = value
                    cells_written += 1
                    last_row = max(last_row, target_row)
                    last_col = max(last_col, target_col)
            if cells_written:
                top_idx = self.index(max(top_row, 0), max(top_col, 0))
                bottom_idx = self.index(last_row, last_col)
                self.dataChanged.emit(
                    top_idx, bottom_idx, [Qt.DisplayRole, Qt.EditRole]
                )
            else:
                # No effect → remove the snapshot we just pushed.
                self._undo_stack.pop()
            return cells_written

        def clear_cells(self, selection: Iterable[Tuple[int, int]]) -> int:
            cells = list(selection)
            if not cells:
                return 0
            for row, col in cells:
                self._check_bounds(row, col)
            self._push_snapshot("clear")
            cleared = 0
            rows = [r for r, _ in cells]
            cols = [c for _, c in cells]
            for row, col in cells:
                if self._cells[row][col] != "":
                    self._cells[row][col] = ""
                    cleared += 1
            if cleared:
                top_idx = self.index(min(rows), min(cols))
                bottom_idx = self.index(max(rows), max(cols))
                self.dataChanged.emit(
                    top_idx, bottom_idx, [Qt.DisplayRole, Qt.EditRole]
                )
            else:
                self._undo_stack.pop()
            return cleared

        # ---- Undo ----

        def can_undo(self) -> bool:
            return bool(self._undo_stack)

        def undo(self) -> bool:
            if not self._undo_stack:
                return False
            _label, snapshot = self._undo_stack.pop()
            self.beginResetModel()
            self._cells = snapshot
            self.endResetModel()
            return True

        def reset_undo(self) -> None:
            """Clear the undo stack — call this on data-context change."""
            self._undo_stack.clear()

        # ---- Point-dict conversion ----

        def as_point_dict(
            self,
            capacity_row: int = 0,
            power_row: int = 1,
        ) -> Dict[str, Tuple[float, float]]:
            return points_from_grid(
                self._column_labels,
                self._cells,
                capacity_row=capacity_row,
                power_row=power_row,
            )

        # ---- internals ----

        def _check_bounds(self, row: int, col: int) -> None:
            if not (0 <= row < len(self._row_labels)):
                raise IndexError(
                    f"row {row} out of range for {len(self._row_labels)} rows"
                )
            if not (0 <= col < len(self._column_labels)):
                raise IndexError(
                    f"col {col} out of range for {len(self._column_labels)} columns"
                )

        def _push_snapshot(self, label: str) -> None:
            snapshot = [list(row) for row in self._cells]
            self._undo_stack.append((label, snapshot))
            if len(self._undo_stack) > self._max_undo_depth:
                self._undo_stack = self._undo_stack[-self._max_undo_depth:]

else:
    SpreadsheetTableModel = None  # type: ignore[assignment]
