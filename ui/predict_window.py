# ui/predict_window.py — 메인 예측 윈도우 (Controller)
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QMessageBox, QLabel
)
from PyQt5.QtCore import Qt

from core.constants import *
from core.utils import load_mapping_data
from core.predictor import load_model, predict_row
from ui.base_model import HVACTableModel
from ui.base_view import HVACTableView

class PredictWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HVAC V3 - 효율 및 성능 예측 시스템")
        self.resize(1300, 600)

        # 1. 의존성 데이터 및 ML 모델 로드
        self.mapping_data = load_mapping_data(MAPPING_JSON_FILE)
        try:
            self.ml_model_data = load_model(MODEL_FILE)
        except Exception as e:
            self.ml_model_data = None
            print(f"⚠️ 모델 로드 실패: {e}")

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """메인 화면 레이아웃 및 컴포넌트 배치"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        top_layout = QHBoxLayout()
        self.btn_predict = QPushButton("🚀 예측 실행 (Predict)")
        self.btn_predict.setMinimumHeight(40)
        self.btn_predict.setStyleSheet("font-weight: bold; background-color: #E6F3E6;")
        
        self.btn_clear = QPushButton("🗑️ 표 초기화 (Clear)")
        self.btn_clear.setMinimumHeight(40)
        
        model_status = "✅ 모델 연결됨" if self.ml_model_data else "❌ 모델 없음 (학습 필요)"
        self.lbl_status = QLabel(model_status)

        top_layout.addWidget(self.btn_predict)
        top_layout.addWidget(self.btn_clear)
        top_layout.addStretch()
        top_layout.addWidget(self.lbl_status)
        layout.addLayout(top_layout)

        # MVC 패턴: 테이블 세팅
        self.table_model = HVACTableModel(self.mapping_data, NUM_ROWS)
        self.table_view = HVACTableView()
        self.table_view.setModel(self.table_model)
        self.table_view.setup_delegates(self.mapping_data)

        layout.addWidget(self.table_view)

    def _connect_signals(self):
        self.btn_predict.clicked.connect(self.on_predict_clicked)
        self.btn_clear.clicked.connect(self.on_clear_clicked)
        self.table_model.dataChanged.connect(self.on_data_changed)

    def on_data_changed(self, top_left, bottom_right, roles):
        """표의 데이터가 수정되었을 때 발생하는 이벤트 핸들러"""
        if not roles or Qt.EditRole not in roles:
            return

        col = top_left.column()
        row = top_left.row()

        # 1. ODU가 변경되었을 때: 종속된 Fin, Pi, Row 드롭다운 목록 갱신
        if col == COL_ODU:
            selected_odu = str(self.table_model.data(top_left, Qt.DisplayRole)).strip()
            self._update_odu_cascading(selected_odu)
            
            # 실외기가 바뀌었으므로 기존 하위 사양들을 빈칸으로 초기화
            self._clear_cells(row, [COL_FIN_TYPE, COL_PI, COL_ROW, COL_COND_AREA, COL_COND_VOLUME])

        # 2. ODU, FIN, PI, ROW 중 하나라도 변경되었을 때: Cond Index 조합 검사 (수정완료)
        if col in [COL_ODU, COL_FIN_TYPE, COL_PI, COL_ROW]:
            self._check_and_fill_cond_specs(row)

    def _update_odu_cascading(self, odu_name):
        """선택된 ODU에 따라 Fin, Pi, Row 드롭다운 목록을 동적으로 갱신합니다."""
        if not odu_name or "odu_cascade" not in self.mapping_data:
            self.table_view.update_dropdown_items(COL_FIN_TYPE, [])
            self.table_view.update_dropdown_items(COL_PI, [])
            self.table_view.update_dropdown_items(COL_ROW, [])
            return

        odu_spec = self.mapping_data["odu_cascade"].get(odu_name, {})
        self.table_view.update_dropdown_items(COL_FIN_TYPE, odu_spec.get("Available_Fins", []))
        self.table_view.update_dropdown_items(COL_PI, odu_spec.get("Available_Pis", []))
        self.table_view.update_dropdown_items(COL_ROW, odu_spec.get("Available_Rows", []))

    def _check_and_fill_cond_specs(self, row):
        """ODU, Fin, Pi, Row가 모두 선택되면 Cond Area/Volume을 자동 입력합니다. (수정완료)"""
        odu_val = str(self.table_model.data(self.table_model.index(row, COL_ODU), Qt.DisplayRole)).strip()
        fin_val = str(self.table_model.data(self.table_model.index(row, COL_FIN_TYPE), Qt.DisplayRole)).strip()
        pi_val = str(self.table_model.data(self.table_model.index(row, COL_PI), Qt.DisplayRole)).strip()
        row_val = str(self.table_model.data(self.table_model.index(row, COL_ROW), Qt.DisplayRole)).strip()

        # 4가지가 모두 입력된 경우에만 매핑 시도
        if odu_val and fin_val and pi_val and row_val:
            # Fin Type을 포함하여 정확한 고유 식별키 생성 (예: N-V2MD F&T 7 1)
            cond_index_key = f"{odu_val} {fin_val} {pi_val} {row_val}"
            
            cond_spec = self.mapping_data.get("cond_specs", {}).get(cond_index_key)
            
            if cond_spec:
                self.table_model.setData(self.table_model.index(row, COL_COND_AREA), cond_spec.get("Cond Area", ""), Qt.EditRole)
                self.table_model.setData(self.table_model.index(row, COL_COND_VOLUME), cond_spec.get("Cond Volume", ""), Qt.EditRole)
            else:
                self._clear_cells(row, [COL_COND_AREA, COL_COND_VOLUME])

    def _clear_cells(self, row, cols):
        """특정 셀들의 값을 비웁니다. 무한 루프 방지를 위해 값이 있을 때만 지웁니다."""
        for c in cols:
            idx = self.table_model.index(row, c)
            if self.table_model.data(idx, Qt.DisplayRole):
                self.table_model.setData(idx, "", Qt.EditRole)

    def on_clear_clicked(self):
        """테이블 전체를 초기화합니다. (무한 루프 방지 로직 적용 완료)"""
        for row in range(self.table_model.rowCount()):
            for col in range(self.table_model.columnCount()):
                idx = self.table_model.index(row, col)
                # 셀에 값이 존재할 때만 setData 호출하여 불필요한 시그널 및 무한 루프 차단
                if self.table_model.data(idx, Qt.DisplayRole):
                    self.table_model.setData(idx, "", Qt.EditRole)

    def on_predict_clicked(self):
        """예측 실행 버튼 로직"""
        if not self.ml_model_data:
            QMessageBox.critical(self, "오류", "학습된 모델(model.pkl)이 없습니다.")
            return

        success_count = 0
        for row in range(self.table_model.rowCount()):
            capa_val = self.table_model.data(self.table_model.index(row, COL_COOLING_CAPA), Qt.DisplayRole)
            if not capa_val or str(capa_val).strip() == "":
                continue

            row_dict = self.table_model.get_row_as_ml_dict(row)
            try:
                results = predict_row(self.ml_model_data, row_dict)
                
                self.table_model.setData(self.table_model.index(row, COL_COOLING_POWER), round(results.get("Cooling Power", 0), 1), Qt.EditRole)
                self.table_model.setData(self.table_model.index(row, COL_CSPF), "TODO: 입력부족", Qt.EditRole)
                self.table_model.setData(self.table_model.index(row, COL_HEATING_POWER), round(results.get("Heating Power", 0), 1), Qt.EditRole)
                self.table_model.setData(self.table_model.index(row, COL_HSPF2), "TODO: 입력부족", Qt.EditRole)
                self.table_model.setData(self.table_model.index(row, COL_REF_QTY), round(results.get("Ref Qty", 0), 2), Qt.EditRole)
                self.table_model.setData(self.table_model.index(row, COL_COOLING_HZ), round(results.get("Cooling Hz", 0), 1), Qt.EditRole)
                self.table_model.setData(self.table_model.index(row, COL_HEATING_HZ), round(results.get("Heating Hz", 0), 1), Qt.EditRole)
                success_count += 1
            except Exception as e:
                print(f"Row {row+1} 예측 중 오류: {e}")

        if success_count > 0:
            self.lbl_status.setText(f"✅ {success_count}개 행 예측 완료")
