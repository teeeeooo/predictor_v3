"""Focused tests for Hong Kong HSPF detail/bin panel wiring.

Covers:
- HSPF section defaults and summary.
- Detail toggle open/close.
- Heating schema graph labels and table headers.
- Bin detail rows from core result.
- Copy/CSV export contract.
- Invalid input stale clear.
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


class TestHongKongHspfSectionDefaults:
    def test_section_defaults_calculate_hspf_summary(self, tk_root) -> None:
        from apps.calculator.ui.sections.hong_kong_hspf_section import HongKongHspfSection

        section = HongKongHspfSection(tk_root, "Hong Kong")
        tk_root.update_idletasks()
        summary = dict(section._detail_summary)
        assert "HSPF" in summary
        # Default inputs should produce the known MVP value ~3.643
        assert float(summary["HSPF"]) == pytest.approx(3.643, abs=0.001)


class TestHongKongHspfDetailPanel:
    def test_detail_panel_initially_hidden(self, tk_root) -> None:
        from apps.calculator.ui.sections.hong_kong_hspf_section import HongKongHspfSection

        section = HongKongHspfSection(tk_root, "Hong Kong")
        tk_root.update_idletasks()
        assert not section.detail_panel.is_visible()

    def test_detail_toggle_opens_detail_panel(self, tk_root) -> None:
        from apps.calculator.ui.sections.hong_kong_hspf_section import HongKongHspfSection

        section = HongKongHspfSection(tk_root, "Hong Kong")
        tk_root.update_idletasks()
        assert section.detail_toggle.cget("text") == "상세 보기 ↓"
        section.detail_toggle.invoke()
        tk_root.update_idletasks()
        assert section.detail_panel.is_visible()
        assert section.detail_toggle.cget("text") == "상세 닫기 ↑"

    def test_detail_toggle_closes_detail_panel(self, tk_root) -> None:
        from apps.calculator.ui.sections.hong_kong_hspf_section import HongKongHspfSection

        section = HongKongHspfSection(tk_root, "Hong Kong")
        section.detail_toggle.invoke()
        tk_root.update_idletasks()
        assert section.detail_panel.is_visible()
        section.detail_toggle.invoke()
        tk_root.update_idletasks()
        assert not section.detail_panel.is_visible()
        assert section.detail_toggle.cget("text") == "상세 보기 ↓"

    def test_detail_panel_uses_heating_graph_labels(self, tk_root) -> None:
        from apps.calculator.ui.sections.hong_kong_hspf_section import HongKongHspfSection
        from apps.calculator.ui.sections.bin_detail_schema import HEATING_HSPF_BIN_DETAIL_SCHEMA

        section = HongKongHspfSection(tk_root, "Hong Kong")
        tk_root.update_idletasks()
        expected_labels = [
            label for label, _key in HEATING_HSPF_BIN_DETAIL_SCHEMA.graph_series
        ]
        assert list(section.detail_panel.graph_combo.cget("values")) == expected_labels

    def test_detail_table_headers_equal_heating_schema(self, tk_root) -> None:
        from apps.calculator.ui.sections.hong_kong_hspf_section import HongKongHspfSection
        from apps.calculator.ui.sections.bin_detail_schema import HEATING_HSPF_BIN_DETAIL_SCHEMA

        section = HongKongHspfSection(tk_root, "Hong Kong")
        tk_root.update_idletasks()
        section.detail_toggle.invoke()
        tk_root.update_idletasks()
        assert section.detail_panel.table.column_labels == HEATING_HSPF_BIN_DETAIL_SCHEMA.column_labels

    def test_detail_rows_populated_from_bin_details(self, tk_root) -> None:
        from apps.calculator.ui.sections.hong_kong_hspf_section import HongKongHspfSection

        section = HongKongHspfSection(tk_root, "Hong Kong")
        tk_root.update_idletasks()
        section.detail_toggle.invoke()
        tk_root.update_idletasks()
        headers, rows = section.detail_panel.table.table_export_data()
        assert len(rows) > 0
        # At least one row should contain the default calculation's case data
        # (e.g., formula45_half_full appears in some bins)
        all_text = "\n".join("\t".join(row) for row in rows)
        assert "formula45_half_full" in all_text or "cycling" in all_text

    def test_detail_copy_button_uses_header_included_tsv(self, tk_root) -> None:
        from apps.calculator.ui.sections.hong_kong_hspf_section import HongKongHspfSection

        section = HongKongHspfSection(tk_root, "Hong Kong")
        tk_root.update_idletasks()
        section.detail_toggle.invoke()
        tk_root.update_idletasks()
        section.detail_panel.copy_table()
        clipboard = tk_root.clipboard_get()
        # Clipboard should contain header row and at least one data row
        lines = clipboard.strip().splitlines()
        assert len(lines) >= 2
        assert "Bin No" in lines[0]

    def test_detail_csv_button_calls_helper(self, monkeypatch, tk_root) -> None:
        from apps.calculator.ui.sections.hong_kong_hspf_section import HongKongHspfSection

        calls = []

        def _fake_export(parent, filename, headers, rows):
            calls.append((filename, headers, rows))
            return True

        monkeypatch.setattr(
            "apps.calculator.ui.table_csv_export.export_table_to_csv", _fake_export
        )

        section = HongKongHspfSection(tk_root, "Hong Kong")
        tk_root.update_idletasks()
        section.detail_toggle.invoke()
        tk_root.update_idletasks()
        section.detail_panel.csv_button.invoke()
        tk_root.update_idletasks()

        assert len(calls) == 1
        filename, headers, rows = calls[0]
        assert filename == "hong_kong_hspf_bin_detail.csv"
        assert "Bin No" in headers
        assert len(rows) > 0


class TestHongKongHspfInvalidInput:
    def test_invalid_input_clears_stale_rows(self, tk_root) -> None:
        from apps.calculator.ui.sections.hong_kong_hspf_section import HongKongHspfSection

        section = HongKongHspfSection(tk_root, "Hong Kong")
        tk_root.update_idletasks()
        # First, ensure detail panel has data by opening it
        section.detail_toggle.invoke()
        tk_root.update_idletasks()
        headers, rows = section.detail_panel.table.table_export_data()
        assert len(rows) > 0
        # Now set invalid input and trigger recalculation
        section.input_table.set_values(
            {
                "full_capacity": "abc",
                "full_power": "1500",
                "half_capacity": "3200",
                "half_power": "800",
            }
        )
        section.recalculate_now()
        tk_root.update_idletasks()
        # Detail panel should show status row, not stale data
        headers, rows = section.detail_panel.table.table_export_data()
        assert headers == ("Status",)
        assert rows[0][0] == "입력 오류: 숫자 입력을 확인하세요."
