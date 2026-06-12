"""Unit tests for EN14825 SEER models, adapter, and table model without GUI dependence."""

import pytest
from apps.calculator.ui.en14825 import (
    SeerPointInput,
    SeerPointComputed,
    SeerResultSummary,
    SeerAdapter,
    SeerTableModel,
)
from core.calculator_en14825 import EN14825Calculator


class FakeCalculator:
    """Stub core calculator to capture raw inputs and verify W -> kW conversion."""

    def __init__(self):
        self.captured_test_points = None
        self.captured_p_to = None
        self.captured_p_sb = None
        self.captured_p_ck = None
        self.captured_p_off = None
        self.captured_p_design_c = None
        self.captured_t_design_c = None
        self.captured_cd = None

    def calculate_seer(self, test_points: dict, p_to: float, p_sb: float, p_ck: float, p_off: float,
                       p_design_c: float, t_design_c: float, cd: float) -> dict:
        self.captured_test_points = test_points
        self.captured_p_to = p_to
        self.captured_p_sb = p_sb
        self.captured_p_ck = p_ck
        self.captured_p_off = p_off
        self.captured_p_design_c = p_design_c
        self.captured_t_design_c = t_design_c
        self.captured_cd = cd
        return {
            "seer": 5.0,
            "seer_on": 5.2,
            "qc_kwh": p_design_c * 350.0,  # h_ce = 350
        }


def test_seer_point_input_init():
    """Verify initialization of SeerPointInput model."""
    inp = SeerPointInput(
        declared_capacity=3500.0,
        declared_eer=3.5,
        tested_capacity=3400.0,
        tested_power=950.0,
    )
    assert inp.declared_capacity == 3500.0
    assert inp.declared_eer == 3.5
    assert inp.tested_capacity == 3400.0
    assert inp.tested_power == 950.0


def test_seer_part_load_calculations():
    """Verify part load ratio (%) and part load (W) calculations."""
    # A (35°C) load ratio = 100%
    ratio_a, load_a = SeerAdapter.get_part_load_info(35.0, 3000.0, 35.0)
    assert pytest.approx(ratio_a) == 100.0
    assert pytest.approx(load_a) == 3000.0

    # B (30°C) load ratio = (30-16)/(35-16) * 100 = 14/19 * 100 approx 73.68%
    ratio_b, load_b = SeerAdapter.get_part_load_info(30.0, 3000.0, 35.0)
    assert pytest.approx(ratio_b) == (14.0 / 19.0) * 100.0
    assert pytest.approx(load_b) == 3000.0 * (14.0 / 19.0)

    # Edge cases: zero p_design_c or invalid t_design_c
    r, l = SeerAdapter.get_part_load_info(35.0, 0.0, 35.0)
    assert r == 0.0 and l == 0.0

    r, l = SeerAdapter.get_part_load_info(35.0, 3000.0, 16.0)
    assert r == 0.0 and l == 0.0


def test_seer_adapter_compute_points():
    """Verify intermediate computation logic on point level."""
    inputs = {
        "A": SeerPointInput(declared_capacity=3500.0, declared_eer=3.5, tested_capacity=3400.0, tested_power=950.0),
        "B": SeerPointInput(declared_capacity=2500.0, declared_eer=4.0, tested_capacity=2200.0, tested_power=500.0),
        "C": SeerPointInput(declared_capacity=1500.0, declared_eer=5.0), # tested missing
        "D": SeerPointInput(tested_capacity=1000.0, tested_power=150.0), # declared missing
    }

    adapter = SeerAdapter()
    computed = adapter.compute_points(inputs)

    # Check point A derived power (3500 / 3.5 = 1000 W)
    assert pytest.approx(computed["A"].declared_power_w_for_core) == 1000.0
    # Check point A tested EER (3400 / 950 approx 3.5789)
    assert pytest.approx(computed["A"].tested_eer) == 3400.0 / 950.0


def test_seer_adapter_w_to_kw_conversion_with_stub():
    """Verify W -> kW conversion for all parameters using FakeCalculator stub."""
    inputs = {
        "A": SeerPointInput(declared_capacity=3600.0, declared_eer=4.0, tested_capacity=3600.0, tested_power=900.0),
        "B": SeerPointInput(declared_capacity=2650.0, declared_eer=4.6, tested_capacity=2650.0, tested_power=576.0),
        "C": SeerPointInput(declared_capacity=1700.0, declared_eer=5.4, tested_capacity=1700.0, tested_power=315.0),
        "D": SeerPointInput(declared_capacity=1200.0, declared_eer=6.2, tested_capacity=1200.0, tested_power=194.0),
    }
    fake_core = FakeCalculator()
    adapter = SeerAdapter(calculator=fake_core)

    adapter.calculate(
        inputs=inputs,
        p_design_c_w=3000.0,
        p_to_w=50.0,
        p_sb_w=10.0,
        p_ck_w=20.0,
        p_off_w=10.0,
        t_design_c=35.0,
        cd=0.25,
    )

    # Verify W -> kW conversion on auxiliary bounds
    assert fake_core.captured_p_design_c == 3.0
    assert fake_core.captured_p_to == 0.05
    assert fake_core.captured_p_sb == 0.01
    assert fake_core.captured_p_ck == 0.02
    assert fake_core.captured_p_off == 0.01
    assert fake_core.captured_t_design_c == 35.0
    assert fake_core.captured_cd == 0.25

    # Verify W -> kW conversion on test points
    # Point A: declared capacity 3600W -> 3.6kW, derived power 900W -> 0.9kW
    assert fake_core.captured_test_points["A"] == (3.6, 0.9)


def test_seer_adapter_zero_negative_values_no_crash():
    """Verify that negative/zero inputs do not crash calculation and yield invalid or unavailable states consistently."""
    inputs = {
        "A": SeerPointInput(declared_capacity=3600.0, declared_eer=0.0, tested_capacity=3600.0, tested_power=0.0),
        "B": SeerPointInput(declared_capacity=0.0, declared_eer=4.6, tested_capacity=-100.0, tested_power=576.0),
        "C": SeerPointInput(declared_capacity=1700.0, declared_eer=-5.4, tested_capacity=1700.0, tested_power=-315.0),
        "D": SeerPointInput(),
    }
    adapter = SeerAdapter()
    computed = adapter.compute_points(inputs)

    # Negative/Zero input state is marked as 'invalid'
    assert computed["A"].declared_eer_state == "invalid"
    assert computed["A"].tested_power_state == "invalid"
    assert computed["B"].declared_capacity_state == "invalid"
    assert computed["B"].tested_capacity_state == "invalid"
    assert computed["C"].declared_eer_state == "invalid"
    assert computed["C"].tested_power_state == "invalid"

    # Unsupplied input state is marked as 'unavailable'
    assert computed["D"].declared_capacity_state == "unavailable"

    # Zero/negative division is prevented and returns None
    assert computed["A"].declared_power_w_for_core is None
    assert computed["A"].tested_eer is None
    assert computed["B"].declared_power_w_for_core is None

    # Check that calculate returns 'input_incomplete' status code without crashing
    summary = adapter.calculate(inputs=inputs, p_design_c_w=3000.0)
    assert summary.status_code == "input_incomplete"
    assert summary.declared_seer is None


def test_seer_adapter_calculate_declared_only():
    """Verify SEER calculation with declared inputs only (tested missing)."""
    inputs = {
        "A": SeerPointInput(declared_capacity=3600.0, declared_eer=4.0),
        "B": SeerPointInput(declared_capacity=2650.0, declared_eer=4.6),
        "C": SeerPointInput(declared_capacity=1700.0, declared_eer=5.4),
        "D": SeerPointInput(declared_capacity=1200.0, declared_eer=6.2),
    }
    adapter = SeerAdapter()
    summary = adapter.calculate(
        inputs=inputs,
        p_design_c_w=3000.0,
        p_to_w=50.0,
        p_sb_w=10.0,
        p_ck_w=20.0,
        p_off_w=0.0,
    )

    assert summary.status_code == "complete"
    assert summary.declared_seer is not None
    assert summary.tested_seer is None
    assert summary.seer_percent is None
    assert summary.seer_percent_state == "unavailable"


def test_seer_adapter_calculate_tested_only():
    """Verify SEER calculation with tested inputs only (declared missing)."""
    inputs = {
        "A": SeerPointInput(tested_capacity=3600.0, tested_power=900.0),
        "B": SeerPointInput(tested_capacity=2650.0, tested_power=576.0),
        "C": SeerPointInput(tested_capacity=1700.0, tested_power=315.0),
        "D": SeerPointInput(tested_capacity=1200.0, tested_power=194.0),
    }
    adapter = SeerAdapter()
    summary = adapter.calculate(
        inputs=inputs,
        p_design_c_w=3000.0,
        p_to_w=50.0,
        p_sb_w=10.0,
        p_ck_w=20.0,
        p_off_w=0.0,
    )

    assert summary.status_code == "complete"
    assert summary.tested_seer is not None
    assert summary.declared_seer is None
    assert summary.seer_percent is None


def test_point_level_threshold_pass_fail():
    """Verify point-level comparison thresholds: capacity <90 or >=110, EER <90."""
    inputs = {
        "A": SeerPointInput(declared_capacity=100.0, declared_eer=4.0, tested_capacity=89.0, tested_power=25.0),  # cap_pct = 89% (<90, invalid)
        "B": SeerPointInput(declared_capacity=100.0, declared_eer=4.0, tested_capacity=110.0, tested_power=25.0), # cap_pct = 110% (>=110, invalid)
        "C": SeerPointInput(declared_capacity=100.0, declared_eer=4.0, tested_capacity=100.0, tested_power=28.0), # eer_pct = 3.57/4.0 = 89.2% (<90, invalid)
        "D": SeerPointInput(declared_capacity=100.0, declared_eer=4.0, tested_capacity=100.0, tested_power=25.0), # cap = 100%, eer = 100% (pass)
    }
    adapter = SeerAdapter()
    comp = adapter.compute_points(inputs)

    assert comp["A"].capacity_percent_state == "invalid"
    assert comp["B"].capacity_percent_state == "invalid"
    assert comp["C"].eer_percent_state == "invalid"
    assert comp["D"].capacity_percent_state == "pass"
    assert comp["D"].eer_percent_state == "pass"


def test_final_seer_threshold_pass_fail():
    """Verify final SEER % pass/fail logic: invalid if < 92%, pass if >= 92% (no upper bound)."""
    # Case 1: tested SEER / declared SEER >= 92%
    inputs_pass = {
        "A": SeerPointInput(declared_capacity=3600.0, declared_eer=4.0, tested_capacity=3600.0, tested_power=950.0), # slight drop
        "B": SeerPointInput(declared_capacity=2650.0, declared_eer=4.6, tested_capacity=2650.0, tested_power=600.0),
        "C": SeerPointInput(declared_capacity=1700.0, declared_eer=5.4, tested_capacity=1700.0, tested_power=330.0),
        "D": SeerPointInput(declared_capacity=1200.0, declared_eer=6.2, tested_capacity=1200.0, tested_power=200.0),
    }
    adapter = SeerAdapter()
    res_pass = adapter.calculate(inputs=inputs_pass, p_design_c_w=3000.0)
    assert res_pass.status_code == "complete"
    assert res_pass.seer_percent_state == "pass"

    # Case 2: tested SEER / declared SEER < 92%
    inputs_fail = {
        "A": SeerPointInput(declared_capacity=3600.0, declared_eer=4.0, tested_capacity=3600.0, tested_power=1400.0), # large drop
        "B": SeerPointInput(declared_capacity=2650.0, declared_eer=4.6, tested_capacity=2650.0, tested_power=1000.0),
        "C": SeerPointInput(declared_capacity=1700.0, declared_eer=5.4, tested_capacity=1700.0, tested_power=600.0),
        "D": SeerPointInput(declared_capacity=1200.0, declared_eer=6.2, tested_capacity=1200.0, tested_power=400.0),
    }
    res_fail = adapter.calculate(inputs=inputs_fail, p_design_c_w=3000.0)
    assert res_fail.status_code == "complete"
    assert res_fail.seer_percent_state == "invalid"


def test_seer_table_model_and_row_protection():
    """Verify SeerTableModel row definitions and verify declared power is NOT exposed."""
    inputs = {
        "A": SeerPointInput(declared_capacity=3600.0, declared_eer=4.0),
        "B": SeerPointInput(), "C": SeerPointInput(), "D": SeerPointInput(),
    }
    adapter = SeerAdapter()
    computed = adapter.compute_points(inputs)
    model = SeerTableModel(inputs, computed, 3000.0)

    # Assert row keys exists but declared power is excluded
    row_keys = model.get_row_keys()
    assert "declared_capacity" in row_keys
    assert "declared_eer" in row_keys

    # Search for any string containing "power" representing declared power row
    assert "declared_power" not in row_keys
    assert "declared_power_w_for_core" not in row_keys
    assert "derived_power" not in row_keys


def test_seer_adapter_validation_failure():
    """Verify that calculator validations do not crash but return structured errors."""
    inputs = {
        "A": SeerPointInput(declared_capacity=3600.0, declared_eer=4.0),
        "B": SeerPointInput(declared_capacity=2650.0, declared_eer=4.6),
        "C": SeerPointInput(declared_capacity=1700.0, declared_eer=5.4),
        "D": SeerPointInput(declared_capacity=1200.0, declared_eer=6.2),
    }
    adapter = SeerAdapter()

    # p_design_c_w <= 0 triggers validation error
    summary = adapter.calculate(inputs=inputs, p_design_c_w=0.0)
    assert summary.status_code == "invalid_design_load"
    assert summary.declared_seer is None


def test_seer_table_model_behavior():
    """Verify that SeerTableModel exposes rows, columns, values, and states correctly."""
    inputs = {
        "A": SeerPointInput(declared_capacity=3600.0, declared_eer=4.0, tested_capacity=3600.0, tested_power=900.0),
        "B": SeerPointInput(declared_capacity=2650.0, declared_eer=4.6, tested_capacity=2385.0, tested_power=576.0), # tested capacity = 2385 -> 90% (pass)
        "C": SeerPointInput(declared_capacity=1700.0, declared_eer=5.4), # tested missing
        "D": SeerPointInput(),
    }
    adapter = SeerAdapter()
    computed = adapter.compute_points(inputs)

    model = SeerTableModel(
        inputs=inputs,
        computed=computed,
        p_design_c_w=3000.0,
        t_design_c=35.0,
    )

    # Check metadata structure
    assert model.get_row_keys() == SeerTableModel.ROW_KEYS
    assert model.get_col_keys() == SeerTableModel.COL_KEYS
    assert model.get_row_label("condition_temp") == "Condition / Temp"
    assert model.get_col_label("A") == "A (35°C)"

    # Check editability
    assert model.is_editable("declared_capacity", "A") is True
    assert model.is_editable("tested_eer", "A") is False

    # Check cell values
    assert model.get_value("condition_temp", "A") == "35°C"
    assert model.get_value("part_load_ratio", "A") == "100%"
    assert model.get_value("part_load_w", "A") == "3000"

    assert model.get_value("declared_capacity", "A") == "3600"
    assert model.get_value("declared_eer", "A") == "4.00"
    assert model.get_value("tested_capacity", "A") == "3600"
    assert model.get_value("tested_power", "A") == "900"
    assert model.get_value("tested_eer", "A") == "4.00"
    assert model.get_value("capacity_percent", "A") == "100.0%"
    assert model.get_value("eer_percent", "A") == "100.0%"

    # Check missing cell representations
    assert model.get_value("tested_capacity", "C") == ""
    assert model.get_value("tested_eer", "C") == ""
    assert model.get_value("capacity_percent", "C") == ""

    # Check cell states
    assert model.get_state("condition_temp", "A") == "neutral"
    assert model.get_state("declared_capacity", "A") == "neutral"
    assert model.get_state("capacity_percent", "A") == "pass"
    assert model.get_state("capacity_percent", "C") == "unavailable"
    assert model.get_state("tested_capacity", "C") == "unavailable"


def test_en14825_gui_integration():
    """Verify EN14825 SEER section and app integration."""
    import tkinter as tk
    from tkinter import ttk
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tkinter is not available in this environment")

    try:
        root.withdraw()

        # Import components
        from apps.calculator.ui.sections.en14825_seer_section import En14825SeerSection
        from apps.calculator.ui.calculator_app import CalculatorTkApp

        # 1. EN14825 SEER section 생성 시 table에 declared_power row가 없는지 확인한다.
        section = En14825SeerSection(root)
        row_keys = section.input_table.rows
        row_names = [r[0] for r in row_keys]
        assert "declared_power" not in row_names
        assert "declared_power_w_for_core" not in row_names
        assert "derived_power" not in row_names

        # 2. default/prefill 값으로 initial recalculate가 crash 없이 수행되는지 확인한다.
        summary_widget = section.result_panel
        summary_text = summary_widget._text.get("1.0", tk.END)
        assert "Declared SEER" in summary_text
        assert "Tested SEER" in summary_text
        assert "자동 계산 완료" in summary_text

        # 3. editable input 변경 후 recalculate_now 또는 debounced flush 후 computed row/tested EER/percent/result summary가 갱신되는지 확인한다.
        section.input_table.set_value("tested_power_A", "1000")  # A tested power: 900 -> 1000
        section._auto_calc.flush_now()

        # Verify tested EER A (3600 / 1000 = 3.60)
        assert section._current_table_model.get_value("tested_eer", "A") == "3.60"

        # 4. declared-only 입력 상태에서 declared result만 나오고 tested/percent가 unavailable 또는 공란 상태인지 확인한다.
        for col in ("A", "B", "C", "D"):
            section.input_table.set_value(f"tested_capacity_{col}", "")
            section.input_table.set_value(f"tested_power_{col}", "")
        section._auto_calc.flush_now()

        summary_text_dec_only = summary_widget._text.get("1.0", tk.END)
        assert "Declared SEER" in summary_text_dec_only
        assert "Tested SEER" in summary_text_dec_only

        assert section._current_table_model.get_value("tested_eer", "A") == ""
        assert section._current_table_model.get_value("capacity_percent", "A") == ""

        # 5. tested-only 입력 상태에서 tested result만 나오고 declared/percent가 unavailable 또는 공란 상태인지 확인한다.
        for col in ("A", "B", "C", "D"):
            section.input_table.set_value(f"declared_capacity_{col}", "")
            section.input_table.set_value(f"declared_eer_{col}", "")
            section.input_table.set_value(f"tested_capacity_{col}", "3600")
            section.input_table.set_value(f"tested_power_{col}", "900")
        section._auto_calc.flush_now()

        assert section._current_table_model.get_value("tested_eer", "A") == "4.00"
        assert section._current_table_model.get_value("declared_eer", "A") == ""
        assert section._current_table_model.get_value("capacity_percent", "A") == ""

        # 6. CalculatorTkApp notebook에 EN14825 tab이 등록되는지 확인한다.
        app = CalculatorTkApp(root=root)
        notebook = None
        for child in root.winfo_children():
            if isinstance(child, ttk.Notebook):
                notebook = child
                break
        assert notebook is not None
        tab_names = [notebook.tab(i, "text") for i in range(len(notebook.tabs()))]
        assert "EN14825" in tab_names

    finally:
        root.destroy()


def test_en14825_static_cell_tint():
    """Verify that static computed cells expose their Label as widget and get correctly tinted."""
    import tkinter as tk
    from tkinter import ttk
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tkinter is not available in this environment")

    try:
        root.withdraw()
        from apps.calculator.ui.sections.en14825_seer_section import En14825SeerSection
        from apps.calculator.ui.layout_constants import TABLE_PASS_BG, TABLE_INVALID_BG
        from apps.calculator.ui.table.roles import CellRole
        from apps.calculator.ui.en14825 import SeerTableModel

        section = En14825SeerSection(root)

        row_idx = SeerTableModel.ROW_KEYS.index("eer_percent")
        col_idx = SeerTableModel.COL_KEYS.index("A")
        position = (row_idx, col_idx)

        # Verify role is READONLY
        assert section.input_table.cell_role(position) == CellRole.READONLY

        # Get widget
        widget = section.input_table.cell_widget(position)
        assert isinstance(widget, tk.Label)

        # Repaint and verify background colors
        section._auto_calc.flush_now()

        frame = section.input_table.cell_frame(position)
        assert frame.cget("background") == TABLE_PASS_BG
        assert widget.cget("background") == TABLE_PASS_BG

        # Now set invalid input to tested_power to trigger invalid state/recalculate
        section.input_table.set_value("tested_power_A", "0")
        section._auto_calc.flush_now()

        # Power state is invalid
        power_row_idx = SeerTableModel.ROW_KEYS.index("tested_power")
        power_pos = (power_row_idx, col_idx)
        power_widget = section.input_table.cell_widget(power_pos)
        assert power_widget.cget("background") == TABLE_INVALID_BG

    finally:
        root.destroy()


def test_en14825_section_breaks():
    """Verify that section breaks are correctly applied to the SEER input table."""
    import tkinter as tk
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tkinter is not available in this environment")

    try:
        root.withdraw()
        from apps.calculator.ui.sections.en14825_seer_section import En14825SeerSection
        from apps.calculator.ui.en14825 import SeerTableModel

        section = En14825SeerSection(root)

        for row_key in ("declared_capacity", "tested_capacity", "capacity_percent"):
            row_idx = SeerTableModel.ROW_KEYS.index(row_key)
            frame = section.input_table.cell_frame((row_idx, 0))
            pady = frame.grid_info()["pady"]
            assert pady == (6, 1) or str(pady) == "6 1"

        part_load_row_idx = SeerTableModel.ROW_KEYS.index("part_load_ratio")
        frame = section.input_table.cell_frame((part_load_row_idx, 0))
        pady = frame.grid_info()["pady"]
        assert pady == 1 or pady == (0, 1) or str(pady) == "1"

    finally:
        root.destroy()


def test_en14825_tab_composes_seer_scop_and_refits_on_scop_toggle():
    """Verify EN14825 tab composition exposes SEER/SCOP and SCOP refit callback."""
    import tkinter as tk
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tkinter is not available in this environment")

    try:
        root.withdraw()
        from apps.calculator.ui.tabs.en14825_tab import En14825Tab
        from apps.calculator.ui.sections.en14825_scop_section import En14825ScopSection
        from apps.calculator.ui.sections.en14825_seer_section import En14825SeerSection

        tab = En14825Tab(root)
        tab.pack(fill=tk.BOTH, expand=True)
        root.update_idletasks()

        tab_names = [
            tab._standard_notebook.tab(tab_id, "text")
            for tab_id in tab._standard_notebook.tabs()
        ]
        assert tab_names == ["SEER", "SCOP"]
        assert isinstance(tab.seer_section, En14825SeerSection)
        assert isinstance(tab.scop_section, En14825ScopSection)
        assert tab.seer_section._frame.cget("text") == "SEER"
        assert tab.scop_section._frame.cget("text") == "SCOP"
        assert "Comparison (EN 14825)" not in tab.seer_section._frame.cget("text")
        assert "Comparison (EN 14825)" not in tab.scop_section._frame.cget("text")
        assert tab._seer_frame.winfo_children()[0].cget("text") == "공통 입력"
        assert tab._scop_frame.winfo_children()[0].cget("text") == "공통 입력"
        assert hasattr(tab, "_p_to_var")
        assert hasattr(tab, "_p_sb_var")
        assert hasattr(tab, "_p_ck_var")
        assert hasattr(tab, "_p_off_var")
        assert hasattr(tab, "_appliance_type_var")
        assert not hasattr(tab.seer_section, "_p_to_var")
        assert not hasattr(tab.scop_section, "_p_to_var")
        assert not hasattr(tab.scop_section, "_appliance_type_var")

        tab._p_to_var.set("25")
        tab._p_sb_var.set("5")
        tab._p_ck_var.set("2")
        tab._p_off_var.set("1")
        tab._appliance_type_var.set("heating_only")

        tab.scop_section._auto_calc.flush_now()
        summary_text = tab.scop_section.result_panel._text.get("1.0", tk.END)
        assert "EN14825 SCOP - Average" in summary_text
        assert "자동 계산 완료" in summary_text

        refit_requests = []

        def record_refit(*, settle_cycles: int = 1) -> None:
            refit_requests.append(settle_cycles)

        tab._refit_scheduler.request_refit = record_refit

        tab._standard_notebook.select(tab._scop_frame)
        tab._on_standard_tab_changed()
        assert tab._p_to_var.get() == "25"
        assert tab._appliance_type_var.get() == "heating_only"
        tab.scop_section.climate_active_vars["warmer"].set(True)
        tab.scop_section._on_climate_toggle()
        tab.scop_section.climate_active_vars["colder"].set(True)
        tab.scop_section._on_climate_toggle()

        assert refit_requests == [1, 1, 1]

    finally:
        root.destroy()


def test_seer_section_uses_en14825_common_auxiliary_inputs():
    """SEER section reads auxiliary power from the EN14825 tab owner provider."""
    import tkinter as tk
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tkinter is not available in this environment")

    common_values = {"p_to": "50", "p_sb": "10", "p_ck": "20", "p_off": "5"}

    try:
        root.withdraw()
        from apps.calculator.ui.sections.en14825_seer_section import En14825SeerSection

        section = En14825SeerSection(root, common_input_values=lambda: common_values)
        fake_core = FakeCalculator()
        section.adapter = SeerAdapter(calculator=fake_core)

        section.recalculate_now()

        assert fake_core.captured_p_to == 0.05
        assert fake_core.captured_p_sb == 0.01
        assert fake_core.captured_p_ck == 0.02
        assert fake_core.captured_p_off == 0.005

    finally:
        root.destroy()
