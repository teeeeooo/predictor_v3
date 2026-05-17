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


def test_en_calculate_button_displays_seer_result_text_for_seer_profile():
    """EN tab의 SEER profile 선택 시 SEER 결과 텍스트가 표시된다.

    sample 값은 tests/test_en14825_golden.py::test_en14825_golden_seer
    에서 그대로 가져온다 (수치 비교는 골든 테스트가 보장).
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

        seer_points = {
            "A": (3.6233, 0.847),
            "B": (2.4691, 0.389),
            "C": (1.5150, 0.137),
            "D": (1.1277, 0.062),
        }
        for pt, (cap, pwr) in seer_points.items():
            window.input_widgets_en[f"{pt}_capacity"].setText(str(cap))
            window.input_widgets_en[f"{pt}_power"].setText(str(pwr))

        window.input_widgets_en["p_design_c"].setText("3.5")
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
    """EN tab의 SCOP 입력을 채운 뒤 계산 버튼을 누르면 SCOP 결과 텍스트가 표시된다.

    Sample 값은 tests/test_en14825_golden.py의 average 케이스를 기준으로 사용한다.
    Standby power는 W 단위로 입력된다는 UI 계약을 함께 점검한다.
    """
    app = _qapp()
    window = CalculatorWindow()

    try:
        assert app is QApplication.instance()
        window.tabs.setCurrentWidget(window.tab_en)

        sample_points = {
            "A": (2.1598, 0.6062),
            "B": (1.3293, 0.2542),
            "C": (0.9083, 0.1540),
            "D": (0.9299, 0.1231),
            "TOL": (2.3698, 0.8067),
            "Tbiv": (2.3669, 0.7820),
        }
        for pt, (cap, pwr) in sample_points.items():
            window.input_widgets_en[f"{pt}_capacity"].setText(str(cap))
            window.input_widgets_en[f"{pt}_power"].setText(str(pwr))

        window.input_widgets_en["p_design_h"].setText("2.4")
        # combo_climate_en defaults to first item ("average")
        window.input_widgets_en["TOL_temp_c"].setText("-11")
        window.input_widgets_en["Tbiv_temp_c"].setText("-10")
        window.input_widgets_en["p_to_w"].setText("6.6")
        window.input_widgets_en["p_sb_w"].setText("1.2")
        window.input_widgets_en["p_ck_w"].setText("0")
        window.input_widgets_en["p_off_w"].setText("1.2")

        window.button_calculate.click()

        assert "EN14825 SCOP" in window.result_label.text()
        assert "결과:" in window.result_label.text()
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
