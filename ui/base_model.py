# ui/base_model.py — SSOT 원칙이 적용된 데이터 관리 모델
from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex
from PyQt5.QtGui import QColor

# 프로젝트 상수 및 유틸리티 임포트
from core.predictor_schema.columns import COLUMNS, DROPDOWN_TARGET
from core.utils import safe_float_convert

class HVACTableModel(QAbstractTableModel):
    def __init__(self, mapping_data=None, num_rows=10):
        super().__init__()
        self.mapping_data = mapping_data if mapping_data is not None else {}
        # 2차원 리스트 기반 데이터 저장소 (rows x cols)
        self._data = [["" for _ in range(len(COLUMNS))] for _ in range(num_rows)]
        # 빠른 조회를 위한 key-index 매핑
        self.key_to_col = {col_info["key"]: i for i, col_info in enumerate(COLUMNS)}

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(COLUMNS)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()
        col_info = COLUMNS[col]

        if role == Qt.DisplayRole:
            return str(self._data[row][col])

        if role == Qt.BackgroundRole:
            color_hex = col_info.get("bg_color", "#FFFFFF")
            return QColor(color_hex)

        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

        return None

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid() or role != Qt.EditRole:
            return False

        row = index.row()
        col = index.column()
        col_info = COLUMNS[col]

        # 1. 데이터 저장
        self._data[row][col] = value
        
        # 2. 드롭다운 변경 시 연쇄 자동완성 (Cascading Auto-fill)
        if col_info.get("group") == "input" and col_info.get("type") == "dropdown":
            self.on_dropdown_changed(row, col, value)

        # 3. 데이터 변경 알림
        self.dataChanged.emit(index, index, [role])
        return True

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return COLUMNS[section]["header"]
        return None

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags

        col_info = COLUMNS[index.column()]
        group = col_info.get("group")
        base_flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable

        # RESULT 및 AUTO 그룹은 읽기 전용
        if group in ["result", "auto"]:
            return base_flags
        
        # INPUT 그룹만 편집 가능
        if group == "input":
            return base_flags | Qt.ItemIsEditable

        return base_flags

    def on_dropdown_changed(self, row, col, value):
        """
        [전략 A 적용] 각 컬럼의 'source' 속성을 참조하여 연쇄 데이터를 자동 입력합니다.
        """
        col_key = COLUMNS[col]["key"] # 현재 변경된 드롭다운의 키 (예: 'idu')
        
        # 1. mapping.json의 어느 섹션을 뒤져야 하는지 파악 (DROPDOWN_TARGET 참조)
        section_name = DROPDOWN_TARGET.get(col_key)
        if not section_name or not self.mapping_data:
            return

        # 2. 매핑 데이터에서 해당 모델의 세부 정보(spec) 추출
        selected_spec = self.mapping_data.get(section_name, {}).get(value)
        if not selected_spec:
            return

        # 3. [핵심] 모든 컬럼을 돌며 '나를 소스로 삼는 자동입력 컬럼'을 찾아 값 기입
        for i, col_info in enumerate(COLUMNS):
            if col_info.get("group") == "auto" and col_info.get("source") == col_key:
                m_key = col_info.get("mapping_key")
                if m_key and m_key in selected_spec:
                    self._data[row][i] = selected_spec[m_key]

        # 4. 행 전체 갱신 (시각적 일관성을 위해 행 단위 emit)
        top_left = self.index(row, 0)
        bottom_right = self.index(row, self.columnCount() - 1)
        self.dataChanged.emit(top_left, bottom_right, [Qt.EditRole])

    def get_row_as_ml_dict(self, row):
        """
        특정 행의 데이터를 모델 예측용 피처 딕셔너리로 변환 (Categorical 처리 포함)
        """
        row_data = self._data[row]
        ml_dict = {}

        for i, col_info in enumerate(COLUMNS):
            ml_key = col_info.get("ml_feature")
            val = row_data[i]

            # 1. ml_feature가 직접 정의된 경우 (Capa, Load, Volume 등)
            if ml_key:
                ml_dict[ml_key] = safe_float_convert(val)
                continue

            # 2. [특수 변환] ml_feature는 없지만 범주형(Categorical) 변환이 필요한 경우
            col_key = col_info.get("key")
            
            # 냉매(Ref) One-hot 변환
            if col_key == "ref_type":
                for r in ["R410A", "R32", "R290"]:
                    ml_dict[r] = 1.0 if val == r else 0.0

            # 팽창장치(Exp) One-hot 변환
            elif col_key == "exp_type":
                for e in ["EEV", "Capi"]:
                    ml_dict[e] = 1.0 if val == e else 0.0

        return ml_dict
