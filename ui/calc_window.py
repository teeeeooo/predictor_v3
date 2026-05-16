# ui/calc_window.py

import os
import json
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QComboBox,
                             QLabel, QGroupBox, QFormLayout, QLineEdit,
                             QMessageBox, QScrollArea, QFrame, QTabWidget,
                             QRadioButton, QButtonGroup)
from PyQt5.QtCore import Qt, QSettings

# 코어 계산기 임포트
from core.calculator_en14825 import EN14825Calculator
from core.calculator_ahri_seer2 import AHRICalculator
from core.calculator_ahri_hspf2 import AHRIHSPF2Calculator
from core.calculator_dispatcher import create_calculator_for_profile


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
        self.ahri_calc = None
        self.hspf2_calc = None

        self.input_widgets_iso = {}
        self.input_widgets_en = {}
        self.input_widgets_ahri = {}
        self.input_widgets_hspf2 = {}

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
        """EN 탭: 단위 kW 적용"""
        layout = QVBoxLayout(self.tab_en)
        
        self.combo_region_en = QComboBox()
        self.combo_region_en.currentIndexChanged.connect(self.on_region_changed_en)
        layout.addWidget(QLabel("지역 설정:"))
        layout.addWidget(self.combo_region_en)

        group = QGroupBox("A/B/C/D 테스트 포인트")
        form = QFormLayout()
        points = ["A", "B", "C", "D"]
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
        layout.addWidget(QLabel("규격 설정 (JSON):"))
        layout.addWidget(self.combo_region_ahri)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # [3] AHRI 입력 UI 시각적 그룹화
        
        # Group 1: Full Load
        group_full = QGroupBox("1. Full Load 조건 (95°F / 82°F)")
        form_full = QFormLayout()
        self.input_widgets_ahri["A_Full_cap"] = QLineEdit()
        self.input_widgets_ahri["A_Full_pow"] = QLineEdit()
        self.input_widgets_ahri["B_Full_cap"] = QLineEdit()
        self.input_widgets_ahri["B_Full_pow"] = QLineEdit()
        
        form_full.addRow("A_Full 능력 (Btu/h):", self.input_widgets_ahri["A_Full_cap"])
        form_full.addRow("A_Full 전력 (W):", self.input_widgets_ahri["A_Full_pow"])
        form_full.addRow("B_Full 능력 (Btu/h):", self.input_widgets_ahri["B_Full_cap"])
        form_full.addRow("B_Full 전력 (W):", self.input_widgets_ahri["B_Full_pow"])
        group_full.setLayout(form_full)
        scroll_layout.addWidget(group_full)

        # Group 2: Part Load / Low Speed
        group_part = QGroupBox("2. Part Load / Low Speed 조건")
        form_part = QFormLayout()
        self.input_widgets_ahri["B_Low_cap"] = QLineEdit()
        self.input_widgets_ahri["B_Low_pow"] = QLineEdit()
        self.input_widgets_ahri["E_Int_cap"] = QLineEdit()
        self.input_widgets_ahri["E_Int_pow"] = QLineEdit()
        self.input_widgets_ahri["F_Low_cap"] = QLineEdit()
        self.input_widgets_ahri["F_Low_pow"] = QLineEdit()
        
        form_part.addRow("B_Low 능력 (Btu/h):", self.input_widgets_ahri["B_Low_cap"])
        form_part.addRow("B_Low 전력 (W):", self.input_widgets_ahri["B_Low_pow"])
        form_part.addRow("E_Int 능력 (Btu/h):", self.input_widgets_ahri["E_Int_cap"])
        form_part.addRow("E_Int 전력 (W):", self.input_widgets_ahri["E_Int_pow"])
        form_part.addRow("F_Low 능력 (Btu/h):", self.input_widgets_ahri["F_Low_cap"])
        form_part.addRow("F_Low 전력 (W):", self.input_widgets_ahri["F_Low_pow"])
        group_part.setLayout(form_part)
        scroll_layout.addWidget(group_part)

        # Group 3: 추가 파라미터
        group_extra = QGroupBox("3. 추가 파라미터 (Optional)")
        form_extra = QFormLayout()
        self.input_widgets_ahri["Cd_low"] = QLineEdit()
        self.input_widgets_ahri["Cd_full"] = QLineEdit()
        
        self.input_widgets_ahri["Cd_low"].setPlaceholderText("기본값: 0.25")
        
        form_extra.addRow("Cd_low:", self.input_widgets_ahri["Cd_low"])
        form_extra.addRow("Cd_full (Optional):", self.input_widgets_ahri["Cd_full"])
        group_extra.setLayout(form_extra)
        scroll_layout.addWidget(group_extra)

        # Group 4: HSPF2 v3 Heating
        group_hspf2 = QGroupBox("4. HSPF2 v3 난방 테스트 포인트")
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
        """설정 파일 스캔 및 규격(Standard)에 맞는 콤보박스에 필터링하여 추가"""
        if not os.path.exists(self.config_dir): 
            return
            
        files = [f for f in os.listdir(self.config_dir) if f.endswith('.json')]
        
        for f in files:
            path = os.path.join(self.config_dir, f)
            try:
                with open(path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    standard = data.get("standard", "").lower()
                    
                    # standard 문자열에 포함된 키워드로 탭 분류
                    if "ahri" in standard:
                        if hasattr(self, 'combo_region_ahri'):
                            self.combo_region_ahri.addItem(f)
                    elif "en" in standard or "14825" in standard:
                        if hasattr(self, 'combo_region_en'):
                            self.combo_region_en.addItem(f)
            except Exception as e:
                print(f"⚠️ 설정 파일 로드 실패 ({f}): {e}")


    def on_region_changed_iso(self, index):
        pass

    def on_region_changed_en(self, index):
        # self.en_calc = EN14825Calculator(path)
        pass

    def on_region_changed_ahri(self, index):
        filename = self.combo_region_ahri.currentText()
        path = os.path.join(self.config_dir, filename)
        # [7] 인스턴스 1회 생성
        try:
            self.ahri_calc = AHRICalculator(path)
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

    # [8] 탭 전환 상태 꼬임 방지
    def on_calculate(self):
        """계산 실행"""
        current_tab = self.tabs.currentWidget()
        self._clear_all_errors() # 초기화

        try:
            if current_tab == self.tab_iso:
                self.calculate_iso()
            elif current_tab == self.tab_en:
                self.calculate_en()
            elif current_tab == self.tab_ahri:
                self.calculate_ahri()
                
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

        # 데이터 추출
        test_points = {
            "A_Full": (self._get_float_val(self.input_widgets_ahri["A_Full_cap"], "A_Full 능력"),
                       self._get_float_val(self.input_widgets_ahri["A_Full_pow"], "A_Full 전력")),
            "B_Full": (self._get_float_val(self.input_widgets_ahri["B_Full_cap"], "B_Full 능력"),
                       self._get_float_val(self.input_widgets_ahri["B_Full_pow"], "B_Full 전력")),
            "B_Low":  (self._get_float_val(self.input_widgets_ahri["B_Low_cap"], "B_Low 능력"),
                       self._get_float_val(self.input_widgets_ahri["B_Low_pow"], "B_Low 전력")),
            "E_Int":  (self._get_float_val(self.input_widgets_ahri["E_Int_cap"], "E_Int 능력"),
                       self._get_float_val(self.input_widgets_ahri["E_Int_pow"], "E_Int 전력")),
            "F_Low":  (self._get_float_val(self.input_widgets_ahri["F_Low_cap"], "F_Low 능력"),
                       self._get_float_val(self.input_widgets_ahri["F_Low_pow"], "F_Low 전력")),
        }

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
        """HSPF2 v3 UI 값을 canonical input으로 변환합니다."""
        test_points = {
            "A2": (self._get_float_val(self.input_widgets_ahri["A_Full_cap"], "A_Full 능력"),
                   self._get_float_val(self.input_widgets_ahri["A_Full_pow"], "A_Full 전력")),
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
        # EN 로직 (단위 kW)
        return "EN 계산 결과 (kW 기준)"
