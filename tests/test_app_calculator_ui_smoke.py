import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PyQt5")

from PyQt5.QtWidgets import QApplication

from ui.calc_window import CalculatorWindow


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
        assert all(not label.endswith(".json") for label in labels)

        index = profile_ids.index("en14825_scop")
        window.combo_region_en.setCurrentIndex(index)
        window.on_region_changed_en(index)

        assert window.en_calc is not None
        assert hasattr(window.en_calc, "calculate_scop")
    finally:
        window.close()


def test_ahri_calculate_button_displays_result_text():
    app = _qapp()
    window = CalculatorWindow()

    try:
        assert app is QApplication.instance()
        window.tabs.setCurrentWidget(window.tab_ahri)
        window.radio_ac.setChecked(True)

        sample_points = {
            "A_Full": (36000, 3000),
            "B_Full": (30000, 2200),
            "B_Low": (18000, 1200),
            "E_Int": (24000, 1700),
            "F_Low": (12000, 900),
        }
        for point, (capacity, power) in sample_points.items():
            window.input_widgets_ahri[f"{point}_cap"].setText(str(capacity))
            window.input_widgets_ahri[f"{point}_pow"].setText(str(power))

        window.button_calculate.click()

        assert "AHRI SEER2 (AC) 결과:" in window.result_label.text()
    finally:
        window.close()
