"""Reusable bin detail panel for Tkinter calculator result surfaces."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass

import tkinter as tk
from tkinter import ttk

from ui_tk import table_csv_export
from ui_tk.layout_constants import ISO_SECTION_BLOCK_GAP, ISO_SECTION_PADX
from ui_tk.sections.bin_trace_table import BinTraceTable


@dataclass(frozen=True)
class BinDetailSource:
    """Rows and summary values for one selectable detail source."""

    rows: tuple[Mapping[str, object], ...] = ()
    summary: tuple[tuple[str, str], ...] = ()
    status: str | None = None


_GRAPH_SERIES: tuple[tuple[str, str], ...] = (
    ("Bin Hours [h]", "nj"),
    ("Load [W]", "lc"),
    ("Capacity [W]", "capacity"),
    ("Power [W]", "power"),
    ("EER [W/W]", "eer"),
    ("CSTL [Wh]", "cstl_bin"),
    ("CSEC [Wh]", "csec_bin"),
)


class BinDetailPanel:
    """PyQt-style detail surface with selector, summary, graph, and bin table."""

    def __init__(
        self,
        parent: tk.Widget,
        *,
        source_labels: Sequence[str],
        default_source: str,
        csv_filename: str,
        show_source_selector: bool = True,
    ) -> None:
        self._source_order = tuple(source_labels)
        self._default_source = default_source
        self._csv_filename = csv_filename
        self._sources: dict[str, BinDetailSource] = {}
        self._panel_status = "상세 데이터 없음"

        self._frame = ttk.Frame(parent)
        self._frame.columnconfigure(0, weight=1)

        self._selector_row = ttk.Frame(self._frame)
        self._selector_row.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=ISO_SECTION_PADX,
            pady=(ISO_SECTION_BLOCK_GAP, 4),
        )
        self._selector_row.columnconfigure(1, weight=1)
        self.source_label = ttk.Label(self._selector_row, text="상세 항목")
        self.source_combo = ttk.Combobox(
            self._selector_row,
            values=self._source_order,
            state="readonly",
        )
        self.source_combo.set(default_source)
        self.source_combo.bind("<<ComboboxSelected>>", self._on_source_changed)
        self.single_source_label = ttk.Label(self._selector_row, text=default_source)
        if show_source_selector and len(self._source_order) > 1:
            self.source_label.grid(row=0, column=0, sticky="w", padx=(0, 6))
            self.source_combo.grid(row=0, column=1, sticky="w")
        else:
            self.single_source_label.grid(row=0, column=0, sticky="w")

        self.summary_label = ttk.Label(self._frame, text="상세 데이터 없음")
        self.summary_label.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=ISO_SECTION_PADX,
            pady=(0, 6),
        )

        self._graph_row = ttk.Frame(self._frame)
        self._graph_row.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=ISO_SECTION_PADX,
            pady=(0, 4),
        )
        self.graph_label = ttk.Label(self._graph_row, text="그래프 항목")
        self.graph_label.pack(side=tk.LEFT, padx=(0, 6))
        self.graph_combo = ttk.Combobox(
            self._graph_row,
            values=[label for label, _key in _GRAPH_SERIES],
            state="readonly",
            width=18,
        )
        self.graph_combo.set(_GRAPH_SERIES[0][0])
        self.graph_combo.pack(side=tk.LEFT)
        self.graph_combo.bind("<<ComboboxSelected>>", self._on_graph_changed)

        self.graph = BinDetailGraph(self._frame)
        self.graph.grid(
            row=3,
            column=0,
            sticky="ew",
            padx=ISO_SECTION_PADX,
            pady=(0, ISO_SECTION_BLOCK_GAP),
        )

        self.table = BinTraceTable(self._frame, title="상세 표")
        self.table.grid(
            row=4,
            column=0,
            sticky="ew",
            padx=ISO_SECTION_PADX,
            pady=(0, 6),
        )

        self._action_row = ttk.Frame(self._frame)
        self._action_row.grid(
            row=5,
            column=0,
            sticky="w",
            padx=ISO_SECTION_PADX,
            pady=(0, ISO_SECTION_BLOCK_GAP),
        )
        self.copy_button = ttk.Button(
            self._action_row,
            text="상세 복사",
            command=self.copy_table,
        )
        self.copy_button.surface_role = "bin_detail_copy"
        self.copy_button.pack(side=tk.LEFT)
        self.csv_button = ttk.Button(
            self._action_row,
            text="상세 CSV 내보내기",
            command=self.export_csv,
        )
        self.csv_button.surface_role = "bin_detail_csv_export"
        self.csv_button.pack(side=tk.LEFT, padx=(6, 0))

        self._refresh_current_source()

    def grid(self, **kwargs) -> None:
        self._frame.grid(**kwargs)

    def grid_remove(self) -> None:
        self._frame.grid_remove()

    def is_visible(self) -> bool:
        return bool(self._frame.winfo_manager())

    def selected_source(self) -> str:
        return self.source_combo.get() or self._default_source

    def set_sources(
        self,
        sources: Mapping[str, BinDetailSource],
        *,
        source_order: Sequence[str] | None = None,
        selected: str | None = None,
        panel_status: str = "상세 데이터 없음",
    ) -> None:
        self._sources = dict(sources)
        self._panel_status = panel_status
        if source_order is not None:
            self._source_order = tuple(source_order)
            self.source_combo.configure(values=self._source_order)
        current = selected or self.selected_source()
        if current not in self._source_order:
            current = self._source_order[0] if self._source_order else self._default_source
        self.source_combo.set(current)
        self.single_source_label.configure(text=current)
        self._refresh_current_source()

    def set_status(self, status: str) -> None:
        self._sources = {}
        self._panel_status = status
        self._refresh_current_source()

    def copy_table(self) -> bool:
        self._refresh_current_source()
        return self.table.copy_table()

    def export_csv(self) -> bool:
        self._refresh_current_source()
        headers, rows = self.table.table_export_data()
        return table_csv_export.export_table_to_csv(
            self._frame,
            self._csv_filename,
            headers,
            rows,
        )

    def _on_source_changed(self, _event=None) -> None:
        self._refresh_current_source()

    def _on_graph_changed(self, _event=None) -> None:
        self.graph.set_series_key(self._selected_graph_key())

    def _refresh_current_source(self) -> None:
        source = self._sources.get(self.selected_source())
        if source is None:
            self.summary_label.configure(text=self._panel_status)
            self.table.set_status(self._panel_status)
            self.graph.set_data(())
            return
        summary = "   ".join(f"{label}: {value}" for label, value in source.summary)
        self.summary_label.configure(text=summary or (source.status or self._panel_status))
        if source.status is not None:
            self.table.set_status(source.status)
            self.graph.set_data(())
            return
        self.table.set_data(source.rows)
        self.graph.set_data(source.rows)
        self.graph.set_series_key(self._selected_graph_key())

    def _selected_graph_key(self) -> str:
        selected = self.graph_combo.get()
        for label, key in _GRAPH_SERIES:
            if label == selected:
                return key
        return _GRAPH_SERIES[0][1]


class BinDetailGraph:
    """Small dependency-free Canvas line graph for cooling bin details."""

    def __init__(self, parent: tk.Widget) -> None:
        self._rows: tuple[Mapping[str, object], ...] = ()
        self._series_key = _GRAPH_SERIES[0][1]
        self.canvas = tk.Canvas(
            parent,
            height=190,
            background="white",
            highlightthickness=1,
            highlightbackground="gray80",
        )
        self.canvas.surface_role = "bin_detail_graph"
        self.canvas.bind("<Configure>", lambda _event: self._draw())

    def grid(self, **kwargs) -> None:
        self.canvas.grid(**kwargs)

    def set_data(self, rows: Iterable[Mapping[str, object]]) -> None:
        self._rows = tuple(rows)
        self._draw()

    def set_series_key(self, key: str) -> None:
        self._series_key = key
        self._draw()

    def _draw(self) -> None:
        canvas = self.canvas
        canvas.delete("all")
        width = max(canvas.winfo_width(), 240)
        height = max(canvas.winfo_height(), 160)
        margin_left = 70
        margin_right = 24
        margin_top = 24
        margin_bottom = 42
        plot_width = max(width - margin_left - margin_right, 1)
        plot_height = max(height - margin_top - margin_bottom, 1)

        points, x_axis_label, x_min, x_max, y_min, y_max = self._plot_points(
            plot_width,
            plot_height,
            margin_left,
            margin_top,
        )
        if not points:
            canvas.create_text(
                width / 2,
                height / 2,
                text="상세 데이터 없음",
                fill="gray35",
            )
            return

        axis_color = "gray25"
        canvas.create_line(
            margin_left,
            margin_top,
            margin_left,
            margin_top + plot_height,
            fill=axis_color,
        )
        canvas.create_line(
            margin_left,
            margin_top + plot_height,
            margin_left + plot_width,
            margin_top + plot_height,
            fill=axis_color,
        )
        baseline_y = margin_top + plot_height
        canvas.create_text(
            margin_left + plot_width / 2,
            height - 10,
            text=x_axis_label,
            fill="gray25",
        )
        if x_min is not None and x_max is not None:
            canvas.create_text(
                margin_left,
                baseline_y + 14,
                text=_tick_text(x_min),
                fill="gray35",
            )
            canvas.create_text(
                margin_left + plot_width,
                baseline_y + 14,
                text=_tick_text(x_max),
                fill="gray35",
            )
        if y_min is not None and y_max is not None:
            canvas.create_text(
                margin_left - 6,
                margin_top,
                anchor="e",
                text=_scale_value_text(self._series_key, y_max),
                fill="gray35",
            )
            canvas.create_text(
                margin_left - 6,
                baseline_y,
                anchor="e",
                text=_scale_value_text(self._series_key, y_min),
                fill="gray35",
            )
        canvas.create_line(*_flatten(points), fill="blue", width=2, smooth=False)
        for x, y in points:
            canvas.create_oval(x - 2, y - 2, x + 2, y + 2, fill="blue", outline="")
        canvas.create_text(
            margin_left,
            margin_top - 12,
            anchor="w",
            text=self._series_scale_label(y_min, y_max),
            fill="gray25",
        )

    def _plot_points(
        self,
        plot_width: int,
        plot_height: int,
        margin_left: int,
        margin_top: int,
    ) -> tuple[
        list[tuple[float, float]],
        str,
        float | None,
        float | None,
        float | None,
        float | None,
    ]:
        rows = [row for row in self._rows if _number(row.get(self._series_key)) is not None]
        if not rows:
            return [], "Outdoor Temp [°C]", None, None, None, None
        x_values = [_number(row.get("tj")) for row in rows]
        x_axis_label = "Outdoor Temp [°C]"
        if any(value is None for value in x_values):
            x_values = [float(index) for index, _row in enumerate(rows)]
            x_axis_label = "Bin index"
        y_values = [_number(row.get(self._series_key)) for row in rows]
        if not y_values or any(value is None for value in y_values):
            return [], x_axis_label, None, None, None, None
        min_x = min(x_values)
        max_x = max(x_values)
        min_y = min(y_values)
        max_y = max(y_values)
        scale_min_y = min_y
        scale_max_y = max_y
        if max_x == min_x:
            max_x = min_x + 1
        if scale_max_y == scale_min_y:
            scale_max_y = scale_min_y + 1
        points = []
        for x_value, y_value in zip(x_values, y_values):
            x = margin_left + ((x_value - min_x) / (max_x - min_x)) * plot_width
            y = (
                margin_top
                + plot_height
                - ((y_value - scale_min_y) / (scale_max_y - scale_min_y)) * plot_height
            )
            points.append((x, y))
        return points, x_axis_label, min_x, max_x, min_y, max_y

    def _series_label(self) -> str:
        for label, key in _GRAPH_SERIES:
            if key == self._series_key:
                return label
        return "Bin Hours [h]"

    def _series_scale_label(self, min_y: float | None, max_y: float | None) -> str:
        label = self._series_label()
        if min_y is None or max_y is None:
            return label
        min_text = _scale_value_text(self._series_key, min_y)
        max_text = _scale_value_text(self._series_key, max_y)
        return f"{label} (min {min_text}, max {max_text})"


def _number(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value))
    except (TypeError, ValueError):
        return None


def _flatten(points: Sequence[tuple[float, float]]) -> tuple[float, ...]:
    return tuple(coordinate for point in points for coordinate in point)


def _tick_text(value: float) -> str:
    if value.is_integer():
        return str(int(value))
    return f"{value:.1f}"


def _scale_value_text(series_key: str, value: float) -> str:
    if series_key == "eer":
        return f"{value:.2f}"
    if value.is_integer():
        return str(int(value))
    return f"{value:.1f}"
