"""Focused tests for configurable bin-detail schema extraction.

Covers:
- Default cooling schema preservation on BinTraceTable / BinDetailPanel.
- Custom schema injection for table headers, rows, and graph series.
- Heating schema row conversion.
- Export/copy contract remains through ``table_export_data()``.
"""

from __future__ import annotations

import pytest


@pytest.fixture
def tk_root():
    tk = pytest.importorskip("tkinter")
    try:
        root = tk.Tk()
    except tk.TclError as exc:
        pytest.skip(f"Tk not available: {exc}")
    root.withdraw()
    try:
        yield root
    finally:
        root.destroy()


from apps.calculator.ui.sections.bin_detail_schema import (
    BinDetailSchema,
    COOLING_BIN_DETAIL_SCHEMA,
    HEATING_HSPF_BIN_DETAIL_SCHEMA,
)


class TestBinDetailSchema:
    def test_cooling_schema_lengths_match(self) -> None:
        assert len(COOLING_BIN_DETAIL_SCHEMA.column_labels) == len(
            COOLING_BIN_DETAIL_SCHEMA.column_keys
        )

    def test_heating_schema_lengths_match(self) -> None:
        assert len(HEATING_HSPF_BIN_DETAIL_SCHEMA.column_labels) == len(
            HEATING_HSPF_BIN_DETAIL_SCHEMA.column_keys
        )

    def test_schema_post_init_rejects_mismatched_lengths(self) -> None:
        with pytest.raises(ValueError):
            BinDetailSchema(
                column_labels=("A", "B"),
                column_keys=("a",),
                graph_series=(("Hours", "nj"),),
            )

    def test_schema_post_init_rejects_empty_columns(self) -> None:
        with pytest.raises(ValueError):
            BinDetailSchema(
                column_labels=(),
                column_keys=(),
                graph_series=(("Hours", "nj"),),
            )

    def test_schema_post_init_rejects_empty_graph_series(self) -> None:
        with pytest.raises(ValueError):
            BinDetailSchema(
                column_labels=("A",),
                column_keys=("a",),
                graph_series=(),
            )


class TestBinTraceTableDefaultSchema:
    def test_default_headers_are_cooling(self, tk_root) -> None:
        from apps.calculator.ui.sections.bin_trace_table import BinTraceTable

        table = BinTraceTable(tk_root)
        assert table.column_labels == COOLING_BIN_DETAIL_SCHEMA.column_labels

    def test_default_title_is_cooling_schema_title(self, tk_root) -> None:
        from apps.calculator.ui.sections.bin_trace_table import BinTraceTable

        table = BinTraceTable(tk_root)
        assert table.title_label.cget("text") == COOLING_BIN_DETAIL_SCHEMA.table_title

    def test_vertical_and_horizontal_scrollbars_are_always_connected(
        self, tk_root
    ) -> None:
        from apps.calculator.ui.sections.bin_trace_table import BinTraceTable

        table = BinTraceTable(tk_root)

        assert str(table.scrollbar.cget("orient")) == "vertical"
        assert str(table.horizontal_scrollbar.cget("orient")) == "horizontal"
        assert table.table.cget("yscrollcommand")
        assert table.table.cget("xscrollcommand")
        assert table.scrollbar.cget("command")
        assert table.horizontal_scrollbar.cget("command")
        assert table.scrollbar.winfo_manager() == "grid"
        assert table.horizontal_scrollbar.winfo_manager() == "grid"
        assert table.scrollbar.grid_info()["row"] == 0
        assert table.horizontal_scrollbar.grid_info()["row"] == 1

    def test_detail_treeview_uses_shared_visual_style_adapter(self, tk_root) -> None:
        from tkinter import ttk

        from apps.calculator.ui.layout_constants import (
            RESULT_VALUE_BG,
            TABLE_HEADER_BG,
            TABLE_SELECTED_BG,
        )
        from apps.calculator.ui.sections.bin_trace_table import BinTraceTable
        from apps.calculator.ui.table.treeview_style import DETAIL_TREEVIEW_STYLE

        table = BinTraceTable(tk_root)
        style = ttk.Style(tk_root)

        assert table.table.cget("style") == DETAIL_TREEVIEW_STYLE
        assert table.table.outer_edge_policy == "flat_low_contrast"
        assert table.table_style.style_name == DETAIL_TREEVIEW_STYLE
        assert style.lookup(DETAIL_TREEVIEW_STYLE, "background") == RESULT_VALUE_BG
        assert style.lookup(table.table_style.heading_style_name, "background") == (
            TABLE_HEADER_BG
        )
        assert ("selected", TABLE_SELECTED_BG) in style.map(
            DETAIL_TREEVIEW_STYLE, "background"
        )

    def test_default_table_export_data_with_rows(self, tk_root) -> None:
        from apps.calculator.ui.sections.bin_trace_table import BinTraceTable

        table = BinTraceTable(tk_root)
        sample = [
            {
                "bin_no": 1,
                "tj": 20.0,
                "nj": 100.0,
                "lc": 2000.0,
                "capacity": 2500.0,
                "power": 800.0,
                "eer": 3.125,
                "cstl_bin": 50000.0,
                "csec_bin": 16000.0,
            }
        ]
        table.set_data(sample)
        headers, rows = table.table_export_data()
        assert headers == COOLING_BIN_DETAIL_SCHEMA.column_labels
        assert len(rows) == 1
        assert rows[0][0] == "1"
        assert rows[0][5] == "800.00"  # power formatted to 2 decimals

    def test_default_status_when_no_rows(self, tk_root) -> None:
        from apps.calculator.ui.sections.bin_trace_table import BinTraceTable

        table = BinTraceTable(tk_root)
        table.set_data(None)
        headers, rows = table.table_export_data()
        assert headers == ("Status",)
        assert rows[0][0] == "상세 데이터 없음"


class TestBinTraceTableCustomSchema:
    def test_custom_schema_headers(self, tk_root) -> None:
        from apps.calculator.ui.sections.bin_trace_table import BinTraceTable

        custom = BinDetailSchema(
            column_labels=("Idx", "Temp"),
            column_keys=("idx", "temp"),
            graph_series=(("Temp", "temp"),),
            table_title="Custom",
        )
        table = BinTraceTable(tk_root, schema=custom)
        assert table.column_labels == ("Idx", "Temp")

    def test_custom_schema_row_conversion(self, tk_root) -> None:
        from apps.calculator.ui.sections.bin_trace_table import BinTraceTable

        custom = BinDetailSchema(
            column_labels=("Idx", "Temp"),
            column_keys=("idx", "temp"),
            graph_series=(("Temp", "temp"),),
        )
        table = BinTraceTable(tk_root, schema=custom)
        table.set_data([{"idx": 1, "temp": 25.5}])
        headers, rows = table.table_export_data()
        assert headers == ("Idx", "Temp")
        assert rows[0] == ("1", "25.50")


class TestBinTraceTableHeatingSchema:
    def test_heating_schema_default_title(self, tk_root) -> None:
        from apps.calculator.ui.sections.bin_trace_table import BinTraceTable

        table = BinTraceTable(tk_root, schema=HEATING_HSPF_BIN_DETAIL_SCHEMA)
        assert table.title_label.cget("text") == HEATING_HSPF_BIN_DETAIL_SCHEMA.table_title

    def test_explicit_title_overrides_schema_title(self, tk_root) -> None:
        from apps.calculator.ui.sections.bin_trace_table import BinTraceTable

        table = BinTraceTable(tk_root, schema=HEATING_HSPF_BIN_DETAIL_SCHEMA, title="Custom Title")
        assert table.title_label.cget("text") == "Custom Title"

    def test_heating_schema_row_conversion(self, tk_root) -> None:
        from apps.calculator.ui.sections.bin_trace_table import BinTraceTable

        table = BinTraceTable(tk_root, schema=HEATING_HSPF_BIN_DETAIL_SCHEMA)
        sample = [
            {
                "bin_no": 1,
                "tj": 6.0,
                "nj": 1.0,
                "bl_h": 3342.71,
                "pi_j": 3342.71,
                "P_j": 843.85,
                "case": "formula45_half_full",
                "heat_pump_energy": 843.85,
                "auxiliary_energy": 0.0,
                "E_j": 843.85,
            }
        ]
        table.set_data(sample)
        headers, rows = table.table_export_data()
        assert headers == HEATING_HSPF_BIN_DETAIL_SCHEMA.column_labels
        assert len(rows) == 1
        # Check key fields are present
        assert "6.00" in rows[0]  # tj
        assert "formula45_half_full" in rows[0]  # case


class TestBinDetailPanelDefaultSchema:
    def test_default_graph_series_labels(self, tk_root) -> None:
        from apps.calculator.ui.sections.bin_detail_panel import BinDetailPanel

        panel = BinDetailPanel(
            tk_root,
            source_labels=("Test",),
            default_source="Test",
            csv_filename="test.csv",
            show_source_selector=False,
        )
        expected_labels = [label for label, _key in COOLING_BIN_DETAIL_SCHEMA.graph_series]
        assert list(panel.graph_combo.cget("values")) == expected_labels

    def test_default_graph_series_first_selected(self, tk_root) -> None:
        from apps.calculator.ui.sections.bin_detail_panel import BinDetailPanel

        panel = BinDetailPanel(
            tk_root,
            source_labels=("Test",),
            default_source="Test",
            csv_filename="test.csv",
            show_source_selector=False,
        )
        assert panel.graph_combo.get() == COOLING_BIN_DETAIL_SCHEMA.graph_series[0][0]


class TestBinDetailPanelCustomSchema:
    def test_custom_graph_series_labels(self, tk_root) -> None:
        from apps.calculator.ui.sections.bin_detail_panel import BinDetailPanel

        custom = BinDetailSchema(
            column_labels=("A",),
            column_keys=("a",),
            graph_series=(("Custom1", "c1"), ("Custom2", "c2")),
        )
        panel = BinDetailPanel(
            tk_root,
            source_labels=("Test",),
            default_source="Test",
            csv_filename="test.csv",
            show_source_selector=False,
            schema=custom,
        )
        expected_labels = ["Custom1", "Custom2"]
        assert list(panel.graph_combo.cget("values")) == expected_labels

    def test_custom_graph_series_first_selected(self, tk_root) -> None:
        from apps.calculator.ui.sections.bin_detail_panel import BinDetailPanel

        custom = BinDetailSchema(
            column_labels=("A",),
            column_keys=("a",),
            graph_series=(("Custom1", "c1"), ("Custom2", "c2")),
        )
        panel = BinDetailPanel(
            tk_root,
            source_labels=("Test",),
            default_source="Test",
            csv_filename="test.csv",
            show_source_selector=False,
            schema=custom,
        )
        assert panel.graph_combo.get() == "Custom1"


class TestBinDetailPanelHeatingSchema:
    def test_heating_graph_series_labels(self, tk_root) -> None:
        from apps.calculator.ui.sections.bin_detail_panel import BinDetailPanel

        panel = BinDetailPanel(
            tk_root,
            source_labels=("HSPF",),
            default_source="HSPF",
            csv_filename="hspf.csv",
            show_source_selector=False,
            schema=HEATING_HSPF_BIN_DETAIL_SCHEMA,
        )
        expected_labels = [label for label, _key in HEATING_HSPF_BIN_DETAIL_SCHEMA.graph_series]
        assert list(panel.graph_combo.cget("values")) == expected_labels


class TestBinDetailGraphCustomSeries:
    def test_custom_series_label_lookup(self) -> None:
        from apps.calculator.ui.sections.bin_detail_panel import BinDetailGraph

        custom_series = (("Alpha", "a"), ("Beta", "b"))
        graph = BinDetailGraph.__new__(BinDetailGraph)
        graph._graph_series = custom_series
        graph._series_key = "b"
        assert graph._series_label() == "Beta"

    def test_custom_series_fallback_label(self) -> None:
        from apps.calculator.ui.sections.bin_detail_panel import BinDetailGraph

        custom_series = (("Alpha", "a"), ("Beta", "b"))
        graph = BinDetailGraph.__new__(BinDetailGraph)
        graph._graph_series = custom_series
        graph._series_key = "unknown"
        assert graph._series_label() == "Alpha"
