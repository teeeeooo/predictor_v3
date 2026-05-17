# ui/calc_window.py

import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QComboBox,
                             QLabel, QGroupBox, QFormLayout, QLineEdit,
                             QMessageBox, QScrollArea, QFrame, QTabWidget,
                             QRadioButton, QButtonGroup, QPushButton,
                             QTableView, QHeaderView, QAbstractItemView)
from PyQt5.QtCore import Qt, QSettings

# 코어 계산기 임포트
from core.calculator_dispatcher import create_calculator_for_profile
from core.calculator_profiles import (
    list_calculator_profiles,
    resolve_calculator_profile,
)

from ui.spreadsheet_table import (
    coerce_numeric,
    make_ahri_seer2_table_model,
)


# [6] 숫자 파싱 공통 함수
def parse_number(text: str) -> float:
    """텍스트에서 콤마를 제거하고 float으로 변환합니다."""
    clean_text = text.replace(',', '').strip()
    if not clean_text:
        raise ValueError("빈 값입니다.")
    return float(clean_text)


class InputValidationError(Exception):
    """입력 검증 실패 시 에러 위젯 정보를 함께 전달하는 예외"""
    def __init__(self, message: str, widget=None):
        super().__init__(message)
        self.widget = widget


class CalculatorWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("효율 계산기 (ISO / EN / AHRI)")
        self.resize(980, 850)

        # 경로 설정
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.dirname(current_dir)
        self.config_dir = os.path.join(self.project_root, "data", "region_configs")

        # [7] Calculator 인스턴스 (1회 생성 후 재사용)
        self.iso_calc = None
        self.en_calc = None
        self.en_profile = None
        self.ahri_calc = None
        self.hspf2_calc = None

        self.input_widgets_iso = {}
        self.input_widgets_en = {}
        self.input_widgets_ahri = {}
        self.input_widgets_hspf2 = {}

        # AHRI SEER2 입력은 horizontal QTableView + QAbstractTableModel로
        # 받는다. 각 cooling test point (A_Full/B_Full/B_Low/E_Int/F_Low)는
        # column이고, row 0 = 능력 [Btu/h], row 1 = 전력 [W]이다.
        # SPREADSHEET_TABLE_CONTRACT.md를 따른다.
        self.ahri_seer2_model = None
        self.ahri_seer2_view = None

        self.init_ui()
        self.settings = QSettings("HVAC_Calculator", "RegionSettings")
        self.scan_configs()
        self._load_hspf2_calc()

    def init_ui(self):
        """메인 레이아웃 및 탭 구성"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)

        self.tabs = QTabWidget()
        
        self.tab_iso = QWidget()
        self.tab_en = QWidget()
        self.tab_ahri = QWidget()

        self.init_iso_tab()
        self.init_en_tab()
        self.init_ahri_tab()

        self.tabs.addTab(self.tab_iso, "ISO 16358")
        self.tabs.addTab(self.tab_en, "EN 14825")
        self.tabs.addTab(self.tab_ahri, "AHRI 210/240")

        main_layout.addWidget(self.tabs)

        action_layout = QHBoxLayout()
        self.button_calculate = QPushButton("계산 실행")
        self.button_calculate.clicked.connect(self.on_calculate)
        self.result_label = QLabel("결과 대기")
        self.result_label.setWordWrap(True)
        self.result_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        action_layout.addWidget(self.button_calculate)
        action_layout.addWidget(self.result_label, 1)
        main_layout.addLayout(action_layout)

    # [1] 에러 스타일링 리셋 로직 (공통 헬퍼)
    def bind_error_reset(self, widget: QLineEdit):
        """사용자가 수정을 시작하면 붉은 테두리를 해제합니다."""
        widget.textChanged.connect(lambda: widget.setStyleSheet(""))

    def init_iso_tab(self):
        """ISO/CSPF 탭: 단건 입력 우선 UI"""
        from ui.calculators_2point import IsoCspfSingleWidget

        layout = QVBoxLayout(self.tab_iso)
        self.iso_cspf_widget = IsoCspfSingleWidget(self.config_dir)
        layout.addWidget(self.iso_cspf_widget)

    def init_en_tab(self):
        """EN 탭: 단위 kW 적용 (EN 14825 SEER + SCOP)"""
        layout = QVBoxLayout(self.tab_en)

        self.combo_region_en = QComboBox()
        self.combo_region_en.currentIndexChanged.connect(self.on_region_changed_en)
        layout.addWidget(QLabel("규격 프로파일:"))
        layout.addWidget(self.combo_region_en)

        group = QGroupBox("A/B/C/D/TOL/Tbiv 테스트 포인트 (kW)")
        form = QFormLayout()
        points = ["A", "B", "C", "D", "TOL", "Tbiv"]
        for pt in points:
            cap_w = QLineEdit()
            pow_w = QLineEdit()
            self.input_widgets_en[f"{pt}_capacity"] = cap_w
            self.input_widgets_en[f"{pt}_power"] = pow_w

            # [2] 단위 명시
            form.addRow(f"{pt} 조건 능력 (kW):", cap_w)
            form.addRow(f"{pt} 조건 소비전력 (kW):", pow_w)

            self.bind_error_reset(cap_w)
            self.bind_error_reset(pow_w)

        group.setLayout(form)
        layout.addWidget(group)

        # SEER/SCOP 계산 파라미터 (metric에 따라 일부만 사용)
        param_group = QGroupBox("SEER/SCOP 계산 파라미터")
        param_form = QFormLayout()

        self.input_widgets_en["p_design_c"] = QLineEdit()
        self.input_widgets_en["p_design_h"] = QLineEdit()
        self.combo_climate_en = QComboBox()
        self.combo_climate_en.addItem("Average", "average")
        self.combo_climate_en.addItem("Warmer", "warmer")
        self.combo_climate_en.addItem("Colder", "colder")
        self.input_widgets_en["TOL_temp_c"] = QLineEdit()
        self.input_widgets_en["Tbiv_temp_c"] = QLineEdit()
        self.input_widgets_en["p_to_w"] = QLineEdit()
        self.input_widgets_en["p_sb_w"] = QLineEdit()
        self.input_widgets_en["p_ck_w"] = QLineEdit()
        self.input_widgets_en["p_off_w"] = QLineEdit()

        param_form.addRow("p_design_c (kW, SEER):", self.input_widgets_en["p_design_c"])
        param_form.addRow("p_design_h (kW, SCOP):", self.input_widgets_en["p_design_h"])
        param_form.addRow("기후 (climate, SCOP):", self.combo_climate_en)
        param_form.addRow("TOL 온도 (°C, SCOP):", self.input_widgets_en["TOL_temp_c"])
        param_form.addRow("Tbiv 온도 (°C, SCOP):", self.input_widgets_en["Tbiv_temp_c"])
        param_form.addRow("p_to (W):", self.input_widgets_en["p_to_w"])
        param_form.addRow("p_sb (W):", self.input_widgets_en["p_sb_w"])
        param_form.addRow("p_ck (W):", self.input_widgets_en["p_ck_w"])
        param_form.addRow("p_off (W):", self.input_widgets_en["p_off_w"])

        for key in (
            "p_design_c",
            "p_design_h",
            "TOL_temp_c",
            "Tbiv_temp_c",
            "p_to_w",
            "p_sb_w",
            "p_ck_w",
            "p_off_w",
        ):
            self.bind_error_reset(self.input_widgets_en[key])

        param_group.setLayout(param_form)
        layout.addWidget(param_group)
        layout.addStretch()

    def init_ahri_tab(self):
        """AHRI 탭: 그룹화 및 시스템 타입 분리"""
        layout = QVBoxLayout(self.tab_ahri)

        # [4] System Type UX 개선 (최상단 배치)
        sys_type_group = QGroupBox("시스템 타입 (System Type)")
        sys_type_layout = QHBoxLayout()
        self.radio_hp = QRadioButton("HP (냉난방 겸용)")
        self.radio_ac = QRadioButton("AC (냉방 전용)")
        self.radio_hp.setChecked(True)
        
        self.sys_type_bg = QButtonGroup()
        self.sys_type_bg.addButton(self.radio_hp)
        self.sys_type_bg.addButton(self.radio_ac)
        
        sys_type_layout.addWidget(self.radio_hp)
        sys_type_layout.addWidget(self.radio_ac)
        sys_type_group.setLayout(sys_type_layout)
        layout.addWidget(sys_type_group)

        self.combo_region_ahri = QComboBox()
        self.combo_region_ahri.currentIndexChanged.connect(self.on_region_changed_ahri)
        layout.addWidget(QLabel("규격 프로파일:"))
        layout.addWidget(self.combo_region_ahri)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # [3] AHRI SEER2 입력 UI: horizontal spreadsheet-like table.
        # 조건이 column, 능력/전력이 row인 형태로 통합한다.
        group_seer2 = QGroupBox(
            "1. SEER2 냉방 시험 포인트 (A_Full ~ F_Low)"
        )
        seer2_layout = QVBoxLayout()
        self.ahri_seer2_model = make_ahri_seer2_table_model(self)
        self.ahri_seer2_view = QTableView()
        self.ahri_seer2_view.setModel(self.ahri_seer2_model)
        self.ahri_seer2_view.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.ahri_seer2_view.setEditTriggers(
            QAbstractItemView.DoubleClicked
            | QAbstractItemView.SelectedClicked
            | QAbstractItemView.EditKeyPressed
            | QAbstractItemView.AnyKeyPressed
        )
        self.ahri_seer2_view.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        self.ahri_seer2_view.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )
        # Row height fits two rows comfortably without scrolling.
        self.ahri_seer2_view.setMinimumHeight(110)
        seer2_layout.addWidget(self.ahri_seer2_view)
        group_seer2.setLayout(seer2_layout)
        scroll_layout.addWidget(group_seer2)

        # Group 2: SEER2 추가 파라미터 (Optional)
        group_extra = QGroupBox("2. 추가 파라미터 (Optional)")
        form_extra = QFormLayout()
        self.input_widgets_ahri["Cd_low"] = QLineEdit()
        self.input_widgets_ahri["Cd_full"] = QLineEdit()
        
        self.input_widgets_ahri["Cd_low"].setPlaceholderText("기본값: 0.25")
        
        form_extra.addRow("Cd_low:", self.input_widgets_ahri["Cd_low"])
        form_extra.addRow("Cd_full (Optional):", self.input_widgets_ahri["Cd_full"])
        group_extra.setLayout(form_extra)
        scroll_layout.addWidget(group_extra)

        # Group 3: HSPF2 v3 Heating (vertical form, table 전환은 다음 slice)
        group_hspf2 = QGroupBox("3. HSPF2 v3 난방 테스트 포인트")
        form_hspf2 = QFormLayout()
        for point in ("H01", "H11", "H12", "H1N", "H22", "H2Int", "H32"):
            cap_w = QLineEdit()
            pow_w = QLineEdit()
            self.input_widgets_hspf2[f"{point}_cap"] = cap_w
            self.input_widgets_hspf2[f"{point}_pow"] = pow_w
            form_hspf2.addRow(f"{point} 능력 (Btu/h):", cap_w)
            form_hspf2.addRow(f"{point} 전력 (W):", pow_w)

        self.input_widgets_hspf2["t_off"] = QLineEdit()
        self.input_widgets_hspf2["t_on"] = QLineEdit()
        self.input_widgets_hspf2["defrost_t_test_minutes"] = QLineEdit()
        self.input_widgets_hspf2["defrost_t_max_minutes"] = QLineEdit()

        form_hspf2.addRow("t_off (°F):", self.input_widgets_hspf2["t_off"])
        form_hspf2.addRow("t_on (°F):", self.input_widgets_hspf2["t_on"])
        form_hspf2.addRow("defrost_t_test_minutes:", self.input_widgets_hspf2["defrost_t_test_minutes"])
        form_hspf2.addRow("defrost_t_max_minutes:", self.input_widgets_hspf2["defrost_t_max_minutes"])
        group_hspf2.setLayout(form_hspf2)
        scroll_layout.addWidget(group_hspf2)

        # 에러 리셋 바인딩
        for w in list(self.input_widgets_ahri.values()) + list(self.input_widgets_hspf2.values()):
            self.bind_error_reset(w)

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

    def scan_configs(self):
        """설정 파일과 profile registry를 규격(Standard)에 맞는 콤보박스에 추가"""
        self._populate_ahri_profiles()
        self._populate_en_profiles()

    def _populate_ahri_profiles(self):
        """AHRI UI는 enabled calculator profile만 선택지로 노출합니다."""
        if not hasattr(self, 'combo_region_ahri'):
            return

        was_blocked = self.combo_region_ahri.blockSignals(True)
        try:
            self.combo_region_ahri.clear()
            for profile in list_calculator_profiles():
                if profile.standard == "AHRI_210_240" and profile.metric == "SEER2":
                    label = f"{profile.standard} / {profile.region.upper()} / {profile.metric}"
                    self.combo_region_ahri.addItem(label, profile.profile_id)
        finally:
            self.combo_region_ahri.blockSignals(was_blocked)

        if self.combo_region_ahri.count() > 0:
            self.on_region_changed_ahri(self.combo_region_ahri.currentIndex())

    def _populate_en_profiles(self):
        """EN UI는 enabled calculator profile만 선택지로 노출합니다.

        SCOP / SEER profile을 모두 노출하며, SCOP을 첫 항목으로 둔다.
        """
        if not hasattr(self, 'combo_region_en'):
            return

        was_blocked = self.combo_region_en.blockSignals(True)
        try:
            self.combo_region_en.clear()
            en_profiles = [
                profile
                for profile in list_calculator_profiles()
                if profile.standard == "EN_14825"
            ]
            # SCOP을 먼저 노출해 기존 사용자 경험을 유지한다.
            en_profiles.sort(key=lambda profile: 0 if profile.metric == "SCOP" else 1)
            for profile in en_profiles:
                label = f"{profile.standard} / {profile.region.upper()} / {profile.metric}"
                self.combo_region_en.addItem(label, profile.profile_id)
        finally:
            self.combo_region_en.blockSignals(was_blocked)

        if self.combo_region_en.count() > 0:
            self.on_region_changed_en(self.combo_region_en.currentIndex())

    def on_region_changed_iso(self, index):
        pass

    def on_region_changed_en(self, index):
        profile_id = None
        if hasattr(self, 'combo_region_en') and index >= 0:
            profile_id = self.combo_region_en.itemData(index)
        if not profile_id:
            profile_id = "en14825_scop"

        try:
            self.en_calc = create_calculator_for_profile(profile_id=profile_id)
            self.en_profile = resolve_calculator_profile(profile_id=profile_id)
        except:
            self.en_calc = None
            self.en_profile = None

    def on_region_changed_ahri(self, index):
        profile_id = None
        if hasattr(self, 'combo_region_ahri') and index >= 0:
            profile_id = self.combo_region_ahri.itemData(index)
        if not profile_id:
            profile_id = "ahri_usa_seer2"

        try:
            self.ahri_calc = create_calculator_for_profile(profile_id=profile_id)
        except:
            self.ahri_calc = None

        self._load_hspf2_calc()

    def _load_hspf2_calc(self):
        try:
            self.hspf2_calc = create_calculator_for_profile(profile_id="ahri_usa_hspf2")
        except:
            self.hspf2_calc = None

    def _get_float_val(self, widget: QLineEdit, field_name: str, allow_empty=False, allow_zero=False) -> float:
        """[9] 입력 유효성 검사 강화"""
        text = widget.text().strip()
        if not text:
            if allow_empty: return None
            raise InputValidationError(f"'{field_name}' 항목을 입력해주세요.", widget)
        
        try:
            val = parse_number(text)
        except ValueError:
            raise InputValidationError(f"'{field_name}' 필드에 올바른 숫자를 입력해주세요.", widget)

        if not allow_zero and val <= 0:
             raise InputValidationError(f"'{field_name}' 필드는 0보다 큰 값이어야 합니다.", widget)

        return val

    def _read_ahri_seer2_table_points(self):
        """AHRI SEER2 table에서 5-point ``test_points`` dict를 읽는다.

        Returns ``{column_label: (capacity, power)}`` for every column.
        Empty / non-numeric / non-positive cells raise
        :class:`InputValidationError` with a Korean message describing
        the offending cell.
        """
        if self.ahri_seer2_model is None:
            raise InputValidationError("AHRI SEER2 입력 테이블이 초기화되지 않았습니다.")
        columns = self.ahri_seer2_model.column_labels
        out = {}
        for col_idx, point_id in enumerate(columns):
            out[point_id] = self._read_ahri_seer2_point(point_id, col_index=col_idx)
        return out

    def _read_ahri_seer2_point(self, point_id, col_index=None):
        """AHRI SEER2 table의 단일 column 값을 ``(capacity, power)``로 읽는다.

        ``InputValidationError``를 던지며, 값이 없거나 숫자가 아니거나
        0 이하이면 어떤 셀이 문제인지 명확한 한글 메시지로 알린다.
        """
        if self.ahri_seer2_model is None:
            raise InputValidationError("AHRI SEER2 입력 테이블이 초기화되지 않았습니다.")
        columns = self.ahri_seer2_model.column_labels
        if col_index is None:
            if point_id not in columns:
                raise InputValidationError(
                    f"AHRI SEER2 테이블에 알 수 없는 포인트: {point_id!r}"
                )
            col_index = columns.index(point_id)
        cap_raw = self.ahri_seer2_model.get_cell(0, col_index)
        pow_raw = self.ahri_seer2_model.get_cell(1, col_index)
        capacity = coerce_numeric(cap_raw)
        power = coerce_numeric(pow_raw)
        if capacity is None:
            raise InputValidationError(
                f"AHRI SEER2 {point_id} 능력 (Btu/h) 값을 입력해주세요."
            )
        if capacity <= 0:
            raise InputValidationError(
                f"AHRI SEER2 {point_id} 능력 (Btu/h)은 0보다 큰 값이어야 합니다."
            )
        if power is None:
            raise InputValidationError(
                f"AHRI SEER2 {point_id} 전력 (W) 값을 입력해주세요."
            )
        if power <= 0:
            raise InputValidationError(
                f"AHRI SEER2 {point_id} 전력 (W)은 0보다 큰 값이어야 합니다."
            )
        return (capacity, power)

    # [8] 탭 전환 상태 꼬임 방지
    def on_calculate(self):
        """계산 실행"""
        current_tab = self.tabs.currentWidget()
        self._clear_all_errors() # 초기화
        result_text = None

        try:
            if current_tab == self.tab_iso:
                result_text = self.calculate_iso()
            elif current_tab == self.tab_en:
                result_text = self.calculate_en()
            elif current_tab == self.tab_ahri:
                result_text = self.calculate_ahri()

            if result_text is not None:
                self.result_label.setText(str(result_text))
            return result_text
                
        # [5] 입력 검증 로직 통일
        except InputValidationError as e:
            QMessageBox.warning(self, "입력 오류", str(e))
            if e.widget:
                e.widget.setStyleSheet("border: 2px solid #E74C3C; background-color: #FDEDEC;")
                e.widget.setFocus()
                e.widget.selectAll()
        except Exception as e:
            QMessageBox.critical(self, "계산 오류", str(e))

    def _clear_all_errors(self):
        """모든 위젯 스타일 리셋"""
        for widgets in [self.input_widgets_iso, self.input_widgets_en, self.input_widgets_ahri, self.input_widgets_hspf2]:
            for w in widgets.values():
                w.setStyleSheet("")

    def calculate_ahri(self):
        """AHRI SEER2 계산 로직"""
        if not self.ahri_calc:
            raise Exception("AHRI 계산기 설정 파일이 로드되지 않았습니다.")

        system_type = "HP" if self.radio_hp.isChecked() else "AC"

        test_points = self._read_ahri_seer2_table_points()

        cd_low = self._get_float_val(self.input_widgets_ahri["Cd_low"], "Cd_low", True, True)

        result = self.ahri_calc.calculate_seer2(
            test_points=test_points,
            system_type=system_type,
            cd_low=cd_low
        )

        seer2 = result.get("SEER2", 0.0)
        result_text = f"AHRI SEER2 ({system_type}) 결과: {seer2}"

        if system_type == "HP":
            hspf2_result = self.calculate_hspf2_v3()
            rounded_hspf2 = hspf2_result.get("rounded_hspf2")
            result_text += f" / HSPF2 v3 결과: {rounded_hspf2}"

        return result_text

    def _build_hspf2_v3_input(self):
        """HSPF2 v3 UI 값을 canonical input으로 변환합니다.

        A2는 AHRI SEER2 horizontal table의 ``A_Full`` 열에서 읽는다.
        나머지 HSPF2 point는 기존 vertical form (``input_widgets_hspf2``)을
        그대로 사용한다.
        """
        test_points = {
            "A2": self._read_ahri_seer2_point("A_Full"),
        }

        for point in ("H01", "H11", "H12", "H1N", "H22", "H2Int", "H32"):
            test_points[point] = (
                self._get_float_val(self.input_widgets_hspf2[f"{point}_cap"], f"{point} 능력"),
                self._get_float_val(self.input_widgets_hspf2[f"{point}_pow"], f"{point} 전력"),
            )

        kwargs = {
            "t_off": self._get_float_val(self.input_widgets_hspf2["t_off"], "t_off", allow_zero=True),
            "t_on": self._get_float_val(self.input_widgets_hspf2["t_on"], "t_on", allow_zero=True),
            "defrost_t_test_minutes": self._get_float_val(
                self.input_widgets_hspf2["defrost_t_test_minutes"],
                "defrost_t_test_minutes",
                allow_zero=True,
            ),
            "defrost_t_max_minutes": self._get_float_val(
                self.input_widgets_hspf2["defrost_t_max_minutes"],
                "defrost_t_max_minutes",
                allow_zero=True,
            ),
        }
        return test_points, kwargs

    def calculate_hspf2_v3(self):
        """AHRI HSPF2 v3 strict 계산 로직 연결"""
        if not self.hspf2_calc:
            raise Exception("HSPF2 v3 계산기 설정 파일이 로드되지 않았습니다.")

        test_points, kwargs = self._build_hspf2_v3_input()
        return self.hspf2_calc.calculate_hspf2_v3(test_points, **kwargs)

    def calculate_iso(self):
        # 2점식 ISO/ISEER 탭은 실시간 계산이므로 수동 계산 버튼 동작 안 함.
        pass

    def calculate_en(self):
        """EN 14825 계산 (선택된 profile metric에 따라 SEER 또는 SCOP 분기)."""
        if not self.en_calc:
            raise Exception("EN 계산기 설정 파일이 로드되지 않았습니다.")

        metric = self.en_profile.metric if self.en_profile else "SCOP"

        # Standby powers는 UI에서 W로 입력받아 calculator API의 kW로 변환합니다.
        p_to_w = self._get_float_val(self.input_widgets_en["p_to_w"], "p_to", allow_zero=True)
        p_sb_w = self._get_float_val(self.input_widgets_en["p_sb_w"], "p_sb", allow_zero=True)
        p_ck_w = self._get_float_val(self.input_widgets_en["p_ck_w"], "p_ck", allow_zero=True)
        p_off_w = self._get_float_val(self.input_widgets_en["p_off_w"], "p_off", allow_zero=True)

        if metric == "SEER":
            test_points = {}
            for pt in ("A", "B", "C", "D"):
                cap = self._get_float_val(
                    self.input_widgets_en[f"{pt}_capacity"], f"{pt} 능력"
                )
                pwr = self._get_float_val(
                    self.input_widgets_en[f"{pt}_power"], f"{pt} 소비전력"
                )
                test_points[pt] = (cap, pwr)

            p_design_c = self._get_float_val(
                self.input_widgets_en["p_design_c"], "p_design_c"
            )

            result = self.en_calc.calculate_seer(
                test_points=test_points,
                p_to=p_to_w / 1000.0,
                p_sb=p_sb_w / 1000.0,
                p_ck=p_ck_w / 1000.0,
                p_off=p_off_w / 1000.0,
                p_design_c=p_design_c,
            )
            seer = result.get("seer", 0.0)
            return f"EN14825 SEER 결과: {seer}"

        # SCOP path (default for backward compatibility)
        test_points = {}
        for pt in ("A", "B", "C", "D", "TOL", "Tbiv"):
            cap = self._get_float_val(self.input_widgets_en[f"{pt}_capacity"], f"{pt} 능력")
            pwr = self._get_float_val(self.input_widgets_en[f"{pt}_power"], f"{pt} 소비전력")
            test_points[pt] = (cap, pwr)

        p_design_h = self._get_float_val(self.input_widgets_en["p_design_h"], "p_design_h")
        climate = self.combo_climate_en.currentData() or "average"
        tol_temp_c = self._get_float_val(
            self.input_widgets_en["TOL_temp_c"], "TOL 온도", allow_zero=True
        )
        tbiv_temp_c = self._get_float_val(
            self.input_widgets_en["Tbiv_temp_c"], "Tbiv 온도", allow_zero=True
        )

        result = self.en_calc.calculate_scop(
            test_points=test_points,
            p_to=p_to_w / 1000.0,
            p_sb=p_sb_w / 1000.0,
            p_ck=p_ck_w / 1000.0,
            p_off=p_off_w / 1000.0,
            p_design_h=p_design_h,
            climate=climate,
            tbiv_temp_c=tbiv_temp_c,
            tol_temp_c=tol_temp_c,
        )

        scop = result.get("scop", result.get("SCOP", 0.0))
        return f"EN14825 SCOP ({climate}) 결과: {scop}"
