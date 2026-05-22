import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PyQt5")

from PyQt5.QtWidgets import QApplication

from ui.calc_window import CalculatorWindow
from ui.spreadsheet_table import SpreadsheetTableView


def _qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_calculator_window_instantiates_offscreen():
    app = _qapp()
    window = CalculatorWindow()

    try:
        assert app is QApplication.instance()
        assert window.tabs.count() == 3
        assert window.tabs.tabText(0) == "ISO 16358"
        assert window.tabs.tabText(1) == "EN 14825"
        assert window.tabs.tabText(2) == "AHRI 210/240"
        assert window.combo_region_ahri.count() >= 1
        assert window.combo_region_ahri.currentData() == "ahri_usa_seer2"
    finally:
        window.close()


def test_ahri_combo_uses_profile_ids_for_dispatcher_selection():
    app = _qapp()
    window = CalculatorWindow()

    try:
        assert app is QApplication.instance()
        profile_ids = [
            window.combo_region_ahri.itemData(index)
            for index in range(window.combo_region_ahri.count())
        ]
        labels = [
            window.combo_region_ahri.itemText(index)
            for index in range(window.combo_region_ahri.count())
        ]

        assert "ahri_usa_seer2" in profile_ids
        assert all(not label.endswith(".json") for label in labels)

        index = profile_ids.index("ahri_usa_seer2")
        window.combo_region_ahri.setCurrentIndex(index)
        window.on_region_changed_ahri(index)

        assert window.ahri_calc is not None
        assert hasattr(window.ahri_calc, "calculate_seer2")
    finally:
        window.close()


def test_en_combo_uses_profile_ids_for_dispatcher_selection():
    app = _qapp()
    window = CalculatorWindow()

    try:
        assert app is QApplication.instance()
        profile_ids = [
            window.combo_region_en.itemData(index)
            for index in range(window.combo_region_en.count())
        ]
        labels = [
            window.combo_region_en.itemText(index)
            for index in range(window.combo_region_en.count())
        ]

        assert "en14825_scop" in profile_ids
        assert "en14825_seer" in profile_ids
        assert all(not label.endswith(".json") for label in labels)

        index = profile_ids.index("en14825_scop")
        window.combo_region_en.setCurrentIndex(index)
        window.on_region_changed_en(index)

        assert window.en_calc is not None
        assert hasattr(window.en_calc, "calculate_scop")
        assert hasattr(window.en_calc, "calculate_seer")
        assert window.en_profile is not None
        assert window.en_profile.metric == "SCOP"
    finally:
        window.close()


def test_en_combo_switching_to_seer_profile_tracks_metric():
    app = _qapp()
    window = CalculatorWindow()

    try:
        assert app is QApplication.instance()
        profile_ids = [
            window.combo_region_en.itemData(index)
            for index in range(window.combo_region_en.count())
        ]
        assert "en14825_seer" in profile_ids

        seer_index = profile_ids.index("en14825_seer")
        window.combo_region_en.setCurrentIndex(seer_index)
        window.on_region_changed_en(seer_index)

        assert window.en_profile is not None
        assert window.en_profile.metric == "SEER"
        assert window.en_profile.mode == "cooling"
    finally:
        window.close()


def _fill_ahri_seer2_table(window, points):
    """Helper: write ``{point: (capacity, power)}`` into the SEER2 table model.

    Used by AHRI smoke tests to populate the horizontal table input
    without touching the OS clipboard or a real QTableView paste path.
    """
    columns = window.ahri_seer2_model.column_labels
    for point, (capacity, power) in points.items():
        col = columns.index(point)
        window.ahri_seer2_model.set_cell(0, col, str(capacity))
        window.ahri_seer2_model.set_cell(1, col, str(power))


def _fill_ahri_hspf2_table(window, points):
    """Helper: write ``{point: (capacity, power)}`` into the HSPF2 table model.

    HSPF2 v3 heating test points (H01..H32) live in their own
    horizontal table; auxiliary fields (t_off / t_on / defrost
    minutes) stay in the compact form and are not handled here.
    """
    columns = window.ahri_hspf2_model.column_labels
    for point, (capacity, power) in points.items():
        col = columns.index(point)
        window.ahri_hspf2_model.set_cell(0, col, str(capacity))
        window.ahri_hspf2_model.set_cell(1, col, str(power))


def test_ahri_seer2_input_uses_horizontal_table_layout():
    """AHRI SEER2 입력은 horizontal QTableView + model로 노출되고,
    기존 5-point per-cell QLineEdit key는 더 이상 ``input_widgets_ahri``에
    존재하지 않는다. Cd_low / Cd_full만 compact form으로 남는다.
    """
    app = _qapp()
    window = CalculatorWindow()

    try:
        assert app is QApplication.instance()
        assert window.ahri_seer2_model is not None
        assert window.ahri_seer2_view is not None
        assert isinstance(window.ahri_seer2_view, SpreadsheetTableView)
        assert window.ahri_seer2_model.column_labels == [
            "A_Full",
            "B_Full",
            "B_Low",
            "E_Int",
            "F_Low",
        ]
        assert window.ahri_seer2_model.row_labels == [
            "능력 [Btu/h]",
            "전력 [W]",
        ]
        # input_widgets_ahri에서 per-point QLineEdit key는 모두 제거된다.
        for point in ("A_Full", "B_Full", "B_Low", "E_Int", "F_Low"):
            assert f"{point}_cap" not in window.input_widgets_ahri
            assert f"{point}_pow" not in window.input_widgets_ahri
        # Cd_low / Cd_full은 compact form으로 유지된다.
        assert "Cd_low" in window.input_widgets_ahri
        assert "Cd_full" in window.input_widgets_ahri
    finally:
        window.close()


def test_ahri_seer2_table_as_point_dict_matches_calculator_input_shape():
    """Table model의 ``as_point_dict`` 결과가 calculate_seer2 입력 형태와 같다."""
    app = _qapp()
    window = CalculatorWindow()

    try:
        assert app is QApplication.instance()
        sample = {
            "A_Full": (36000, 3000),
            "B_Full": (30000, 2200),
            "B_Low": (18000, 1200),
            "E_Int": (24000, 1700),
            "F_Low": (12000, 900),
        }
        _fill_ahri_seer2_table(window, sample)
        points = window.ahri_seer2_model.as_point_dict(
            capacity_row=0, power_row=1
        )
        assert points == {
            "A_Full": (36000.0, 3000.0),
            "B_Full": (30000.0, 2200.0),
            "B_Low": (18000.0, 1200.0),
            "E_Int": (24000.0, 1700.0),
            "F_Low": (12000.0, 900.0),
        }
    finally:
        window.close()


def test_ahri_hp_calculate_button_displays_seer2_and_hspf2_results():
    """AHRI HP 모드에서 SEER2 + HSPF2 v3 결과가 result label에 모두 표시된다.

    AHRI SEER2 필수 5 포인트(A_Full ~ F_Low)와 HSPF2 v3 필수 입력 (H01..H32,
    t_off/t_on, defrost minutes)을 채워서 계산 버튼 클릭 후 result label에
    "AHRI SEER2 (HP) 결과:"와 "HSPF2 v3 결과:"가 모두 포함되는지만 확인하는
    happy-path smoke. 수치 비교는 calculator 단위 테스트가 보장한다.
    """
    app = _qapp()
    window = CalculatorWindow()

    try:
        assert app is QApplication.instance()
        window.tabs.setCurrentWidget(window.tab_ahri)
        window.radio_hp.setChecked(True)

        _fill_ahri_seer2_table(
            window,
            {
                "A_Full": (24000, 2500),
                "B_Full": (22000, 2000),
                "B_Low": (12000, 1200),
                "E_Int": (15000, 1500),
                "F_Low": (10000, 1000),
            },
        )

        _fill_ahri_hspf2_table(
            window,
            {
                "H01": (12500, 980),
                "H11": (12000, 1000),
                "H12": (24000, 2200),
                "H1N": (22000, 2000),
                "H22": (23200, 2160),
                "H2Int": (13000, 1200),
                "H32": (22000, 2100),
            },
        )

        window.input_widgets_hspf2["t_off"].setText("-10")
        window.input_widgets_hspf2["t_on"].setText("-5")
        window.input_widgets_hspf2["defrost_t_test_minutes"].setText("90")
        window.input_widgets_hspf2["defrost_t_max_minutes"].setText("720")

        window.button_calculate.click()

        text = window.result_label.text()
        assert "AHRI SEER2 (HP) 결과:" in text
        assert "HSPF2 v3 결과:" in text
    finally:
        window.close()


def test_ahri_calculate_button_displays_result_text():
    app = _qapp()
    window = CalculatorWindow()

    try:
        assert app is QApplication.instance()
        window.tabs.setCurrentWidget(window.tab_ahri)
        window.radio_ac.setChecked(True)

        _fill_ahri_seer2_table(
            window,
            {
                "A_Full": (36000, 3000),
                "B_Full": (30000, 2200),
                "B_Low": (18000, 1200),
                "E_Int": (24000, 1700),
                "F_Low": (12000, 900),
            },
        )

        window.button_calculate.click()

        assert "AHRI SEER2 (AC) 결과:" in window.result_label.text()
    finally:
        window.close()


def test_ahri_hspf2_input_uses_horizontal_table_layout():
    """AHRI HSPF2 v3 입력은 horizontal QTableView + model로 노출된다.

    H01..H32 per-point QLineEdit (``*_cap`` / ``*_pow``) key는
    ``input_widgets_hspf2``에서 모두 제거되고, auxiliary 4개 key
    (``t_off``, ``t_on``, ``defrost_t_test_minutes``,
    ``defrost_t_max_minutes``)만 compact form으로 유지된다.
    """
    app = _qapp()
    window = CalculatorWindow()

    try:
        assert app is QApplication.instance()
        assert window.ahri_hspf2_model is not None
        assert window.ahri_hspf2_view is not None
        assert isinstance(window.ahri_hspf2_view, SpreadsheetTableView)
        assert window.ahri_hspf2_model.column_labels == [
            "H01",
            "H11",
            "H12",
            "H1N",
            "H22",
            "H2Int",
            "H32",
        ]
        assert window.ahri_hspf2_model.row_labels == [
            "능력 [Btu/h]",
            "전력 [W]",
        ]

        for point in ("H01", "H11", "H12", "H1N", "H22", "H2Int", "H32"):
            assert f"{point}_cap" not in window.input_widgets_hspf2
            assert f"{point}_pow" not in window.input_widgets_hspf2

        for extra_key in (
            "t_off",
            "t_on",
            "defrost_t_test_minutes",
            "defrost_t_max_minutes",
        ):
            assert extra_key in window.input_widgets_hspf2

        assert set(window.input_widgets_hspf2.keys()) == {
            "t_off",
            "t_on",
            "defrost_t_test_minutes",
            "defrost_t_max_minutes",
        }
    finally:
        window.close()


def test_ahri_hspf2_table_as_point_dict_matches_calculator_input_shape():
    """HSPF2 table의 ``as_point_dict`` 결과가 HSPF2 v3 calculator의
    per-point input 형태와 같다 (A2는 별도, SEER2 table에서 읽음).
    """
    app = _qapp()
    window = CalculatorWindow()

    try:
        assert app is QApplication.instance()
        sample = {
            "H01": (12500, 980),
            "H11": (12000, 1000),
            "H12": (24000, 2200),
            "H1N": (22000, 2000),
            "H22": (23200, 2160),
            "H2Int": (13000, 1200),
            "H32": (22000, 2100),
        }
        _fill_ahri_hspf2_table(window, sample)
        points = window.ahri_hspf2_model.as_point_dict(
            capacity_row=0, power_row=1
        )
        assert points == {
            point_id: (float(c), float(p))
            for point_id, (c, p) in sample.items()
        }
    finally:
        window.close()


def _fill_en_seer_table(window, points_w):
    """Helper: write ``{point: (capacity_w, power_w)}`` into the EN SEER table."""
    columns = window.en_seer_model.column_labels
    for point, (capacity_w, power_w) in points_w.items():
        col = columns.index(point)
        window.en_seer_model.set_cell(0, col, str(capacity_w))
        window.en_seer_model.set_cell(1, col, str(power_w))


def _fill_en_scop_table(window, climate_key, points_w):
    """Helper: write per-climate SCOP table values (in watts)."""
    climate = window.en_scop_climates[climate_key]
    columns = climate["model"].column_labels
    for point, (capacity_w, power_w) in points_w.items():
        col = columns.index(point)
        climate["model"].set_cell(0, col, str(capacity_w))
        climate["model"].set_cell(1, col, str(power_w))


def test_en_seer_input_uses_horizontal_table_layout():
    """EN SEER 입력은 horizontal QTableView + model로 노출되고, 단위는 W이다."""
    app = _qapp()
    window = CalculatorWindow()

    try:
        assert app is QApplication.instance()
        assert window.en_seer_model is not None
        assert window.en_seer_view is not None
        assert isinstance(window.en_seer_view, SpreadsheetTableView)
        assert window.en_seer_model.column_labels == ["A", "B", "C", "D"]
        assert window.en_seer_model.row_labels == ["능력 [W]", "전력 [W]"]
    finally:
        window.close()


def test_en_scop_input_uses_multi_climate_table_layout_with_average_default():
    """EN SCOP 입력은 climate별 checkbox + table이고, Average가 기본 checked."""
    app = _qapp()
    window = CalculatorWindow()

    try:
        assert app is QApplication.instance()
        assert set(window.en_scop_climates.keys()) == {
            "average",
            "warmer",
            "colder",
        }
        for climate_key, climate in window.en_scop_climates.items():
            assert climate["model"].column_labels == [
                "A",
                "B",
                "C",
                "D",
                "TOL",
                "Tbiv",
            ]
            assert climate["model"].row_labels == ["능력 [W]", "전력 [W]"]
        assert window.en_scop_climates["average"]["checkbox"].isChecked() is True
        assert window.en_scop_climates["warmer"]["checkbox"].isChecked() is False
        assert window.en_scop_climates["colder"]["checkbox"].isChecked() is False
    finally:
        window.close()


def test_en_scop_climate_default_temperatures_are_prefilled():
    """각 climate card의 Tbiv / TOL 기본값이 task 명시 값으로 prefill된다."""
    app = _qapp()
    window = CalculatorWindow()

    try:
        assert app is QApplication.instance()
        expected = {
            "average": (-10.0, -11.0),
            "warmer": (2.0, -11.0),
            "colder": (-15.0, -22.0),
        }
        for climate_key, (tbiv, tol) in expected.items():
            climate = window.en_scop_climates[climate_key]
            assert float(climate["tbiv_w"].text()) == tbiv
            assert float(climate["tol_w"].text()) == tol
    finally:
        window.close()


def test_en_standby_group_is_positioned_above_seer_and_scop_sections():
    """Standby 입력은 SEER/SCOP main input보다 먼저 보이고, 기존 key/default(0.0)/W 단위를 유지한다."""
    app = _qapp()
    window = CalculatorWindow()

    try:
        assert app is QApplication.instance()
        parent_layout = window.tab_en.layout()
        positions = {}
        for i in range(parent_layout.count()):
            item = parent_layout.itemAt(i)
            widget = item.widget()
            if widget is None:
                continue
            if widget is window.en_standby_group:
                positions["standby"] = i
            elif widget is window.en_seer_group:
                positions["seer"] = i
            elif widget is window.en_scop_group:
                positions["scop"] = i
        assert "standby" in positions and "seer" in positions and "scop" in positions
        assert positions["standby"] < positions["seer"]
        assert positions["standby"] < positions["scop"]

        for key in ("p_to_w", "p_sb_w", "p_ck_w", "p_off_w"):
            widget = window.input_widgets_en[key]
            assert widget is not None
            assert widget.text() == "0.0"
    finally:
        window.close()


def test_en_seer_profile_shows_seer_table_and_hides_scop_section():
    """SEER profile 선택 시 SEER table은 visible, SCOP card section은 hidden."""
    app = _qapp()
    window = CalculatorWindow()

    try:
        assert app is QApplication.instance()
        profile_ids = [
            window.combo_region_en.itemData(index)
            for index in range(window.combo_region_en.count())
        ]
        seer_index = profile_ids.index("en14825_seer")
        window.combo_region_en.setCurrentIndex(seer_index)
        window.on_region_changed_en(seer_index)
        assert window.en_seer_group.isHidden() is False
        assert window.en_scop_group.isHidden() is True
    finally:
        window.close()


def test_en_calculate_button_displays_seer_result_text_for_seer_profile():
    """EN tab의 SEER profile 선택 시 SEER 결과 텍스트가 표시된다.

    UI 입력은 W 단위. EN core 호출 직전 W → kW 변환되어 calculate_seer를
    1회 호출한다. 수치 비교는 골든 테스트가 보장하므로 여기는 표시
    문자열만 확인한다.
    """
    app = _qapp()
    window = CalculatorWindow()

    try:
        assert app is QApplication.instance()
        window.tabs.setCurrentWidget(window.tab_en)

        profile_ids = [
            window.combo_region_en.itemData(index)
            for index in range(window.combo_region_en.count())
        ]
        seer_index = profile_ids.index("en14825_seer")
        window.combo_region_en.setCurrentIndex(seer_index)
        window.on_region_changed_en(seer_index)

        # Golden sample (kW) × 1000 = W.
        _fill_en_seer_table(
            window,
            {
                "A": (3623.3, 847.0),
                "B": (2469.1, 389.0),
                "C": (1515.0, 137.0),
                "D": (1127.7, 62.0),
            },
        )

        window.input_widgets_en["p_design_c_w"].setText("3500")
        window.input_widgets_en["p_to_w"].setText("6.6")
        window.input_widgets_en["p_sb_w"].setText("1.2")
        window.input_widgets_en["p_ck_w"].setText("0")
        window.input_widgets_en["p_off_w"].setText("1.2")

        window.button_calculate.click()

        assert "EN14825 SEER" in window.result_label.text()
        assert "결과:" in window.result_label.text()
    finally:
        window.close()


def test_en_calculate_button_displays_scop_result_text():
    """SCOP 입력을 채워 average climate만 계산하면 Average SCOP 결과가 나온다."""
    app = _qapp()
    window = CalculatorWindow()

    try:
        assert app is QApplication.instance()
        window.tabs.setCurrentWidget(window.tab_en)

        sample_points_w = {
            "A": (2159.8, 606.2),
            "B": (1329.3, 254.2),
            "C": (908.3, 154.0),
            "D": (929.9, 123.1),
            "TOL": (2369.8, 806.7),
            "Tbiv": (2366.9, 782.0),
        }
        _fill_en_scop_table(window, "average", sample_points_w)
        window.en_scop_climates["average"]["p_design_h_w"].setText("2400")
        # Tbiv / TOL는 prefill 값을 그대로 사용.

        window.input_widgets_en["p_to_w"].setText("6.6")
        window.input_widgets_en["p_sb_w"].setText("1.2")
        window.input_widgets_en["p_ck_w"].setText("0")
        window.input_widgets_en["p_off_w"].setText("1.2")

        window.button_calculate.click()

        text = window.result_label.text()
        assert "EN14825 SCOP" in text
        assert "Average SCOP" in text
    finally:
        window.close()


def test_en_calculate_button_displays_multi_climate_scop_result_text():
    """Average + Warmer를 모두 선택하면 두 climate 결과가 한 줄에 표시된다."""
    app = _qapp()
    window = CalculatorWindow()

    try:
        assert app is QApplication.instance()
        window.tabs.setCurrentWidget(window.tab_en)

        sample_points_w = {
            "A": (2159.8, 606.2),
            "B": (1329.3, 254.2),
            "C": (908.3, 154.0),
            "D": (929.9, 123.1),
            "TOL": (2369.8, 806.7),
            "Tbiv": (2366.9, 782.0),
        }
        for climate_key in ("average", "warmer"):
            window.en_scop_climates[climate_key]["checkbox"].setChecked(True)
            _fill_en_scop_table(window, climate_key, sample_points_w)
            window.en_scop_climates[climate_key]["p_design_h_w"].setText("2400")

        # Disable colder explicitly.
        window.en_scop_climates["colder"]["checkbox"].setChecked(False)

        window.input_widgets_en["p_to_w"].setText("6.6")
        window.input_widgets_en["p_sb_w"].setText("1.2")
        window.input_widgets_en["p_ck_w"].setText("0")
        window.input_widgets_en["p_off_w"].setText("1.2")

        window.button_calculate.click()

        text = window.result_label.text()
        assert "Average SCOP" in text
        assert "Warmer SCOP" in text
    finally:
        window.close()


def test_en_seer_w_input_is_converted_to_kw_before_core_call():
    """W 입력은 EN core 호출 직전에 1/1000 배되어 kW로 전달된다.

    _read_en_table_points_kw helper가 capacity/power를 kW로 변환하는지
    직접 확인한다. EN core나 region config는 수정하지 않으므로 helper
    수준 smoke만 본다.
    """
    app = _qapp()
    window = CalculatorWindow()

    try:
        assert app is QApplication.instance()
        _fill_en_seer_table(
            window,
            {
                "A": (3623.3, 847.0),
                "B": (2469.1, 389.0),
                "C": (1515.0, 137.0),
                "D": (1127.7, 62.0),
            },
        )
        points_kw = window._read_en_table_points_kw(
            window.en_seer_model, "ABCD"
        )
        assert points_kw["A"] == pytest.approx((3.6233, 0.847))
        assert points_kw["D"] == pytest.approx((1.1277, 0.062))
    finally:
        window.close()


def test_hspf2_required_input_raises_validation_error_when_missing():
    """HP 모드에서 HSPF2 필수 입력이 비어 있으면 InputValidationError가 발생한다.

    HSPF2 A2 값은 AHRI SEER2 table의 ``A_Full`` 열에서 읽으므로 그 셀만
    채우고 ``calculate_hspf2_v3``를 직접 호출한다. on_calculate는
    QMessageBox 호출을 포함하므로 validation 경로만 직접 점검한다.
    """
    from ui.calc_window import InputValidationError

    app = _qapp()
    window = CalculatorWindow()

    try:
        assert app is QApplication.instance()
        a_full_col = window.ahri_seer2_model.column_labels.index("A_Full")
        window.ahri_seer2_model.set_cell(0, a_full_col, "36000")
        window.ahri_seer2_model.set_cell(1, a_full_col, "3000")

        with pytest.raises(InputValidationError):
            window.calculate_hspf2_v3()
    finally:
        window.close()
