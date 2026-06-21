"""Bordered Tkinter input matrix with explicit editable-cell mapping.

This widget owns presentation and text parsing only. It does not import
calculator core or profile routing; visual values come from its Tkinter owner.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable, Iterable, Mapping

from apps.calculator.ui.layout_constants import (
    TABLE_BODY_FONT,
    TABLE_CELL_PADX,
    TABLE_CELL_PADY,
    TABLE_DATA_COLUMN_CHARS,
    TABLE_DATA_COLUMN_WEIGHT,
    TABLE_GRID_COLOR,
    TABLE_HEADER_BG,
    TABLE_HEADER_FG,
    TABLE_HEADER_FONT,
    TABLE_HEADER_PADY,
    TABLE_ROW_HEADER_CHARS,
    TABLE_ROW_HEADER_WEIGHT,
    TABLE_STATIC_FG,
    TABLE_SECTION_BREAK_GAP,
)
from apps.calculator.ui.table_grid_model import parse_numeric_cell
from apps.calculator.ui.table.cell_background import cell_background
from apps.calculator.ui.table.roles import CellRole

__all__ = ["MetricInputTable"]


ValuesChangedCallback = Callable[[], None]
CellAddress = tuple[str, str]


class MetricInputTable(ttk.Frame):
    """A bordered matrix table containing editable and static cells."""

    def __init__(
        self,
        master: tk.Misc,
        *,
        columns: tuple[tuple[str, str], ...],
        rows: tuple[tuple[str, str], ...],
        editable_cells: Mapping[CellAddress, str],
        row_header_chars: int = TABLE_ROW_HEADER_CHARS,
        data_column_chars: int = TABLE_DATA_COLUMN_CHARS,
        layout_policy: str = "content_hug",
        values_changed_callback: ValuesChangedCallback | None = None,
        section_break_before_rows: Iterable[str] | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(master, **kwargs)
        if layout_policy not in {"responsive", "content_hug"}:
            raise ValueError(
                "MetricInputTable layout_policy must be 'responsive' or 'content_hug'"
            )
        self.section_break_before_rows = set(section_break_before_rows or [])
        self.columns = columns
        self.rows = rows
        self.editable_cells = dict(editable_cells)
        self.row_header_chars = row_header_chars
        self.data_column_chars = data_column_chars
        self.layout_policy = layout_policy
        self._values_changed_callback = values_changed_callback
        self._values: dict[str, str] = {
            field_key: "" for field_key in self.editable_cells.values()
        }
        self._variables: dict[str, tk.StringVar] = {}
        self._entries: dict[str, tk.Entry] = {}
        self.editable_entries = self._entries
        self._readonly_cell_labels: dict[str, tk.Label] = {}
        self._readonly_presentation_addresses: set[CellAddress] = set()
        self._batch_depth = 0
        self._batch_changed = False
        self.table_frame: tk.Frame
        self.header_cells: dict[str, tk.Frame] = {}
        self.row_header_cells: dict[str, tk.Frame] = {}
        self.editable_cell_frames: dict[str, tk.Frame] = {}
        self.static_cell_frames: dict[CellAddress, tk.Frame] = {}
        self.cell_frames: dict[CellAddress, tk.Frame] = {}
        self.static_cell_labels: dict[CellAddress, tk.Label] = {}
        if len(set(self.editable_cells.values())) != len(self.editable_cells):
            raise ValueError("metric input field keys must be unique")
        self.field_order: tuple[str, ...] = ()
        self.editable_addresses: tuple[CellAddress, ...] = ()
        self._invalid_fields: dict[str, str] = {}
        self._build_table()

    def _build_table(self) -> None:
        is_content_hug = self.layout_policy == "content_hug"
        self.columnconfigure(0, weight=0 if is_content_hug else 1)
        self.table_frame = tk.Frame(
            self,
            name="matrix_surface",
            background=TABLE_GRID_COLOR,
            borderwidth=1,
            relief=tk.SOLID,
        )
        self.table_frame.grid(
            row=0,
            column=0,
            sticky="w" if is_content_hug else "ew",
        )
        self.table_frame.surface_role = "table_frame"
        self.table_frame.layout_policy = self.layout_policy
        self._configure_column_weights()
        self._add_header_cell(column=0, key=None, label="")
        for column_number, (_key, label) in enumerate(self.columns, start=1):
            self._add_header_cell(column=column_number, key=_key, label=label)
        for row_number, (row_key, label) in enumerate(self.rows, start=1):
            self._add_row_header(row=row_number, key=row_key, label=label)
            for column_number, (column_key, _label) in enumerate(
                self.columns, start=1
            ):
                address = (row_key, column_key)
                field_key = self.editable_cells.get(address)
                if field_key is None:
                    self._add_static_cell(
                        row=row_number, column=column_number, address=address
                    )
                    continue
                self._add_editable_cell(
                    row=row_number,
                    column=column_number,
                    address=address,
                    field_key=field_key,
                )

    def _configure_column_weights(self) -> None:
        if self.layout_policy == "content_hug":
            row_header_weight = 0
            data_column_weight = 0
        else:
            row_header_weight = TABLE_ROW_HEADER_WEIGHT
            data_column_weight = TABLE_DATA_COLUMN_WEIGHT
        self.table_frame.columnconfigure(0, weight=row_header_weight)
        for column in range(1, len(self.columns) + 1):
            self.table_frame.columnconfigure(column, weight=data_column_weight)

    def _add_header_cell(self, *, column: int, key: str | None, label: str) -> None:
        cell = self._make_cell_frame(
            row=0, column=column, role="header_cell", background=TABLE_HEADER_BG
        )
        if key is not None:
            cell.surface_key = key
            self.header_cells[key] = cell
        tk.Label(
            cell,
            text=label,
            width=self.row_header_chars if key is None else self.data_column_chars,
            background=TABLE_HEADER_BG,
            foreground=TABLE_HEADER_FG,
            font=TABLE_HEADER_FONT,
        ).pack(fill=tk.BOTH, expand=True, padx=TABLE_CELL_PADX, pady=TABLE_HEADER_PADY)

    def update_column_header(self, column_key: str, new_label: str) -> None:
        """Update the text label of a column header dynamically."""
        cell = self.header_cells.get(column_key)
        if cell:
            for child in cell.winfo_children():
                if isinstance(child, tk.Label):
                    child.configure(text=new_label)

    def _add_row_header(self, *, row: int, key: str, label: str) -> None:
        cell = self._make_cell_frame(
            row=row, column=0, role="row_header_cell", background=TABLE_HEADER_BG, row_key=key
        )
        cell.surface_key = key
        self.row_header_cells[key] = cell
        tk.Label(
            cell,
            text=label,
            width=self.row_header_chars,
            anchor="w",
            background=TABLE_HEADER_BG,
            foreground=TABLE_HEADER_FG,
            font=TABLE_HEADER_FONT,
        ).pack(fill=tk.BOTH, expand=True, padx=TABLE_CELL_PADX, pady=TABLE_HEADER_PADY)

    def _add_static_cell(
        self, *, row: int, column: int, address: CellAddress
    ) -> None:
        cell = self._make_cell_frame(
            row=row,
            column=column,
            role="static_cell",
            background=cell_background(editable=False),
            row_key=address[0],
        )
        cell.surface_address = address
        self.cell_frames[address] = cell
        self.static_cell_frames[address] = cell
        label = tk.Label(
            cell,
            text="-",
            width=self.data_column_chars,
            background=cell_background(editable=False),
            foreground=TABLE_STATIC_FG,
            font=TABLE_BODY_FONT,
        )
        label.pack(fill=tk.BOTH, expand=True, padx=TABLE_CELL_PADX, pady=TABLE_CELL_PADY)
        self.static_cell_labels[address] = label

    def _add_editable_cell(
        self, *, row: int, column: int, address: CellAddress, field_key: str
    ) -> None:
        cell = self._make_cell_frame(
            row=row,
            column=column,
            role="editable_cell",
            background=cell_background(editable=True),
            row_key=address[0],
        )
        cell.surface_address = address
        self.cell_frames[address] = cell
        self.editable_cell_frames[field_key] = cell
        variable = tk.StringVar(master=self)
        variable.trace_add(
            "write",
            lambda *_args, field_key=field_key: self._handle_change(field_key),
        )
        entry = tk.Entry(
            cell,
            textvariable=variable,
            width=self.data_column_chars,
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=0,
            justify=tk.CENTER,
            background=cell_background(editable=True),
            font=TABLE_BODY_FONT,
        )
        entry.pack(fill=tk.BOTH, expand=True, padx=TABLE_CELL_PADX, pady=TABLE_CELL_PADY)
        entry.surface_role = "editable_entry"
        entry.bind(
            "<Return>",
            lambda _event, field_key=field_key: self._focus_next(field_key),
        )
        readonly_label = tk.Label(
            cell,
            text="",
            width=self.data_column_chars,
            background=cell_background(editable=False),
            foreground=TABLE_STATIC_FG,
            font=TABLE_BODY_FONT,
        )
        readonly_label.surface_role = "readonly_cell_label"
        self._variables[field_key] = variable
        self._entries[field_key] = entry
        self._readonly_cell_labels[field_key] = readonly_label
        self.field_order += (field_key,)
        self.editable_addresses += (address,)

    def _make_cell_frame(
        self,
        *,
        row: int,
        column: int,
        role: str,
        background: str,
        row_key: str | None = None,
    ) -> tk.Frame:
        cell = tk.Frame(self.table_frame, background=background, borderwidth=0)
        if row_key is not None and row_key in self.section_break_before_rows:
            pady = (TABLE_SECTION_BREAK_GAP, 1)
        else:
            pady = (0, 1)
        cell.grid(row=row, column=column, sticky="nsew", padx=(0, 1), pady=pady)
        cell.surface_role = role
        return cell

    def _handle_change(self, field_key: str) -> None:
        value = self._variables[field_key].get()
        if value == self._values[field_key]:
            return
        self._values[field_key] = value
        if self._batch_depth:
            self._batch_changed = True
            return
        if self._values_changed_callback is not None:
            self._values_changed_callback()

    def _focus_next(self, field_key: str) -> str:
        index = self.field_order.index(field_key)
        following = self.field_order[(index + 1) % len(self.field_order)]
        self._entries[following].focus_set()
        return "break"

    def set_values_changed_callback(
        self, callback: ValuesChangedCallback | None
    ) -> None:
        self._values_changed_callback = callback

    def set_value(self, field_key: str, value: str) -> bool:
        if field_key not in self._values:
            raise KeyError(f"Unknown metric input field key: {field_key!r}")
        if not isinstance(value, str):
            raise TypeError("metric input values must be strings")
        if self._values[field_key] == value:
            return False
        self._variables[field_key].set(value)
        return True

    def set_values(self, values: Mapping[str, str]) -> bool:
        changed = False
        for field_key, value in values.items():
            if self.set_value(field_key, value):
                changed = True
        return changed

    def set_values_batch(self, values: Mapping[str, str]) -> bool:
        """Set several editable values and notify at most once."""
        outermost = self._batch_depth == 0
        if outermost:
            self._batch_changed = False
        self._batch_depth += 1
        try:
            changed = self.set_values(values)
        finally:
            self._batch_depth -= 1
        if outermost and self._batch_changed:
            self._batch_changed = False
            if self._values_changed_callback is not None:
                self._values_changed_callback()
        return changed

    def field_key_for_address(self, address: CellAddress) -> str | None:
        return self.editable_cells.get(address)

    def text_at_address(self, address: CellAddress) -> str:
        field_key = self.field_key_for_address(address)
        if field_key is None:
            return "-"
        return self._values[field_key]

    def set_address_values_batch(self, values: Mapping[CellAddress, str]) -> bool:
        editable_values = {
            field_key: value
            for address, value in values.items()
            if (field_key := self.field_key_for_address(address)) is not None
        }
        return self.set_values_batch(editable_values)

    def set_readonly_addresses(
        self,
        addresses: Iterable[CellAddress],
        *,
        display_values: Mapping[CellAddress, str] | None = None,
    ) -> bool:
        """Show editable addresses with static/read-only cell presentation."""
        display_values = display_values or {}
        readonly_addresses = {
            address for address in addresses if address in self.editable_cells
        }
        changed = readonly_addresses != self._readonly_presentation_addresses
        self._readonly_presentation_addresses = readonly_addresses
        for address, field_key in self.editable_cells.items():
            display_value = display_values.get(address, self._values[field_key])
            changed = (
                self._apply_cell_presentation(
                    field_key=field_key,
                    readonly=address in readonly_addresses,
                    display_value=display_value,
                )
                or changed
            )
        return changed

    def get_numeric_values(self, fields: Iterable[str] | None = None) -> dict[str, float]:
        """Return numeric values for editable cells or raise on invalid input.

        Invalid fields are marked with visible invalid state.
        Valid fields have their invalid state cleared.
        """
        target_fields = list(fields) if fields is not None else list(self._values.keys())
        for f in target_fields:
            if f not in self._values:
                raise KeyError(f"Unknown metric input field key: {f!r}")

        if fields is None:
            self.clear_invalid_fields()
        else:
            self.clear_invalid_fields(target_fields)

        invalid: dict[str, str] = {}
        numeric: dict[str, float] = {}
        for field_key in target_fields:
            value = self._values[field_key]
            try:
                numeric[field_key] = parse_numeric_cell(value)
            except ValueError:
                invalid[field_key] = "숫자 입력 필요"

        if invalid:
            current_invalid = self.invalid_fields()
            current_invalid.update(invalid)
            self.set_invalid_fields(current_invalid)
            raise ValueError(
                f"Invalid numeric input in {len(invalid)} field(s)"
            )
        return numeric

    def get_text_values(self) -> dict[str, str]:
        return dict(self._values)

    # ---- TkTableSurface-compatible adapter methods (position-based) ----

    def row_count(self) -> int:
        return len(self.rows)

    def column_count(self) -> int:
        return len(self.columns)

    def cell_roles(self) -> tuple[CellRole, ...]:
        return tuple(
            CellRole.EDITABLE
            if (
                (row_key, column_key) in self.editable_cells
                and (row_key, column_key) not in self._readonly_presentation_addresses
            )
            else CellRole.READONLY
            for row_key, _row_label in self.rows
            for column_key, _column_label in self.columns
        )

    def cell_role(self, position: tuple[int, int]) -> CellRole:
        address = self._address_at_position(position)
        if (
            address in self.editable_cells
            and address not in self._readonly_presentation_addresses
        ):
            return CellRole.EDITABLE
        return CellRole.READONLY

    def text_at_position(self, position: tuple[int, int]) -> str:
        return self.text_at_address(self._address_at_position(position))

    def set_positions_batch(self, values: Mapping[tuple[int, int], str]) -> bool:
        address_values = {
            self._address_at_position(pos): val for pos, val in values.items()
        }
        return self.set_address_values_batch(address_values)

    def snapshot(self) -> dict[str, str]:
        return dict(self._values)

    def restore_snapshot(self, snapshot: Mapping[str, str]) -> None:
        self.set_values_batch(dict(snapshot))

    def cell_frame(self, position: tuple[int, int]) -> tk.Frame:
        address = self._address_at_position(position)
        return self.cell_frames[address]

    def cell_widget(self, position: tuple[int, int]) -> tk.Widget:
        address = self._address_at_position(position)
        field_key = self._field_key_at_position(position)
        if field_key is not None:
            if address in self._readonly_presentation_addresses:
                return self._readonly_cell_labels[field_key]
            return self.editable_entries[field_key]
        label = self.static_cell_labels.get(address)
        if label is not None:
            return label
        return self.cell_frames[address]

    def focus_widget(self, position: tuple[int, int]) -> tk.Widget:
        return self.cell_widget(position)

    def default_cell_background(self, position: tuple[int, int]) -> str:
        field_key = self._field_key_at_position(position)
        return self.role_cell_background(
            position,
            invalid=field_key is not None and field_key in self._invalid_fields,
        )

    def role_cell_background(
        self, position: tuple[int, int], *, invalid: bool = False
    ) -> str:
        return cell_background(
            editable=self.cell_role(position) is CellRole.EDITABLE,
            invalid=invalid,
        )

    def ensure_row_count(self, count: int) -> None:
        # Fixed-row surface: no-op.  Main tables never dynamically add rows.
        pass

    # ---- Invalid field state API ----

    def set_invalid_fields(self, errors: Mapping[str, str]) -> None:
        """Mark editable fields as invalid with optional messages.

        Unknown field keys raise ``KeyError``.
        Read-only/static field keys are ignored.
        """
        for field_key in errors:
            if field_key not in self._values:
                raise KeyError(f"Unknown metric input field key: {field_key!r}")
        self._invalid_fields = dict(errors)
        self._apply_all_visual_states()

    def clear_invalid_fields(self, fields: Iterable[str] | None = None) -> None:
        """Clear invalid state for specific fields or all fields."""
        if fields is None:
            self._invalid_fields.clear()
            self._apply_all_visual_states()
            return
        for field_key in fields:
            if field_key not in self._values:
                raise KeyError(f"Unknown metric input field key: {field_key!r}")
            self._invalid_fields.pop(field_key, None)
        self._apply_all_visual_states()

    def invalid_fields(self) -> dict[str, str]:
        """Return a copy of current invalid field state."""
        return dict(self._invalid_fields)

    def is_field_invalid(self, field_key: str) -> bool:
        """Return whether a field is currently marked invalid."""
        if field_key not in self._values:
            raise KeyError(f"Unknown metric input field key: {field_key!r}")
        return field_key in self._invalid_fields

    def invalid_message(self, field_key: str) -> str | None:
        """Return the invalid message for a field, or None if not invalid."""
        if field_key not in self._values:
            raise KeyError(f"Unknown metric input field key: {field_key!r}")
        return self._invalid_fields.get(field_key)

    def _apply_field_visual_state(self, field_key: str) -> None:
        """Set entry background for one field based on invalid state."""
        entry = self.editable_entries[field_key]
        entry.configure(
            background=cell_background(
                editable=True,
                invalid=field_key in self._invalid_fields,
            )
        )

    def _apply_all_visual_states(self) -> None:
        """Apply visual state to all editable entries."""
        for field_key in self.editable_entries:
            self._apply_field_visual_state(field_key)

    def _apply_cell_presentation(
        self,
        *,
        field_key: str,
        readonly: bool,
        display_value: str,
    ) -> bool:
        entry = self.editable_entries[field_key]
        readonly_label = self._readonly_cell_labels[field_key]
        cell = self.editable_cell_frames[field_key]
        if readonly:
            previous_text = readonly_label.cget("text")
            readonly_label.configure(
                text=display_value,
                background=cell_background(editable=False),
            )
            entry.configure(state=tk.NORMAL)
            if entry.winfo_manager():
                entry.pack_forget()
            if not readonly_label.winfo_manager():
                readonly_label.pack(
                    fill=tk.BOTH,
                    expand=True,
                    padx=TABLE_CELL_PADX,
                    pady=TABLE_CELL_PADY,
                )
            cell.configure(background=cell_background(editable=False))
            return previous_text != display_value

        was_readonly_visible = bool(readonly_label.winfo_manager())
        if was_readonly_visible:
            readonly_label.pack_forget()
        if not entry.winfo_manager():
            entry.pack(
                fill=tk.BOTH,
                expand=True,
                padx=TABLE_CELL_PADX,
                pady=TABLE_CELL_PADY,
            )
        entry.configure(state=tk.NORMAL)
        self._apply_field_visual_state(field_key)
        cell.configure(
            background=cell_background(
                editable=True,
                invalid=field_key in self._invalid_fields,
            )
        )
        return was_readonly_visible

    def _address_at_position(self, position: tuple[int, int]) -> CellAddress:
        row, column = position
        if not (0 <= row < len(self.rows)):
            raise IndexError(f"row index {row} out of range for {len(self.rows)} rows")
        if not (0 <= column < len(self.columns)):
            raise IndexError(f"column index {column} out of range for {len(self.columns)} columns")
        return (self.rows[row][0], self.columns[column][0])

    def _field_key_at_position(self, position: tuple[int, int]) -> str | None:
        address = self._address_at_position(position)
        return self.editable_cells.get(address)
