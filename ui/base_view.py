# ui/base_view.py — QTableView 및 커스텀 Delegate (UI 표현 및 상호작용 전담)
from PyQt5.QtWidgets import (
    QTableView, QStyledItemDelegate, QComboBox, QStyle, 
    QStyleOptionComboBox, QApplication, QAbstractItemView
)
from PyQt5.QtCore import Qt, QEvent, QTimer
from core.predictor_schema.columns import COLUMNS

class DropdownDelegate(QStyledItemDelegate):
    """
    콤보박스(드롭다운) 컬럼을 위한 커스텀 Delegate.
    셀이 편집 모드가 아닐 때도 화살표(▼)를 그려주어 드롭다운임을 명시하고,
    클릭 시 즉시 팝업이 전개되는(One-click popup) UX를 제공합니다.
    """
    def __init__(self, parent=None, items_map=None):
        super().__init__(parent)
        # {열 인덱스: ["목록1", "목록2"]} 형태의 딕셔너리를 주입받음
        self.items_map = items_map or {}

    def update_items(self, col: int, new_items: list):
        """특정 열의 드롭다운 목록을 동적으로 갱신합니다."""
        self.items_map[col] = new_items

    def paint(self, painter, option, index):
        """기본 배경과 텍스트를 그린 후, 우측에 콤보박스 화살표를 덧그립니다."""
        super().paint(painter, option, index)

        col = index.column()
        if col in self.items_map:
            opt = QStyleOptionComboBox()
            opt.rect = option.rect
            opt.state = option.state | QStyle.State_Enabled
            
            opt.subControls = QStyle.SC_ComboBoxArrow
            QApplication.style().drawComplexControl(QStyle.CC_ComboBox, opt, painter)

    def createEditor(self, parent, option, index):
        """셀 편집이 시작될 때 QComboBox 위젯을 생성합니다."""
        col = index.column()
        if col in self.items_map:
            cb = QComboBox(parent)
            # 현재 갱신되어 있는 최신 목록 아이템 추가
            cb.addItems(self.items_map[col])
            
            # [UX 마법] 에디터가 생성되자마자 팝업을 즉시 펼침
            QTimer.singleShot(0, cb.showPopup)
            return cb
            
        return super().createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        """Model의 현재 값을 콤보박스의 선택된 값으로 세팅합니다."""
        if isinstance(editor, QComboBox):
            current_text = str(index.data(Qt.DisplayRole))
            idx = editor.findText(current_text)
            if idx >= 0:
                editor.setCurrentIndex(idx)
        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        """콤보박스에서 선택된 값을 Model로 전달합니다."""
        if isinstance(editor, QComboBox):
            model.setData(index, editor.currentText(), Qt.EditRole)
        else:
            super().setModelData(editor, model, index)

    def editorEvent(self, event, model, option, index):
        """사용자의 마우스 클릭 이벤트를 가로채어 즉각 편집 모드로 진입시킵니다."""
        col = index.column()
        if col in self.items_map and event.type() == QEvent.MouseButtonRelease:
            if isinstance(self.parent(), QAbstractItemView):
                self.parent().edit(index)
            return True
        return super().editorEvent(event, model, option, index)


class HVACTableView(QTableView):
    """
    V3의 메인 데이터 입출력을 담당하는 뷰 테이블.
    디자인 설정과 Delegate 적용을 전담합니다.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self.delegate = None

    def _setup_ui(self):
        """테이블 기본 시각적 속성 설정"""
        self.setSelectionMode(QTableView.SingleSelection)
        self.setAlternatingRowColors(False) 
        
        self.verticalHeader().setDefaultSectionSize(35)
        self.horizontalHeader().setStretchLastSection(True)
        
        for i, col_info in enumerate(COLUMNS):
            width = col_info.get("width", 100)
            self.setColumnWidth(i, width)

    def setup_delegates(self, mapping_data):
        """
        constants.py를 분석하여 드롭다운 컬럼을 찾고 Delegate를 장착합니다.
        """
        items_map = {}
        
        for i, col_info in enumerate(COLUMNS):
            if col_info.get("type") == "dropdown":
                mapping_section = col_info.get("mapping") 
                
                if mapping_section and mapping_section in mapping_data:
                    items_map[i] = list(mapping_data[mapping_section].keys())
                
                elif col_info["key"] == "ref_type":
                    items_map[i] = ["R410A", "R32", "R290"]
                elif col_info["key"] == "exp_type":
                    items_map[i] = ["EEV", "Capi"]
                else:
                    items_map[i] = [] 

        self.delegate = DropdownDelegate(self, items_map)
        
        for col_idx in items_map.keys():
            self.setItemDelegateForColumn(col_idx, self.delegate)

    def update_dropdown_items(self, col_index: int, new_items: list):
        """
        외부(Window)에서 특정 열의 드롭다운 목록을 동적으로 변경할 때 호출합니다.
        예: ODU 선택 시 종속된 Fin, Pi, Row 드롭다운 목록 갱신
        """
        if self.delegate is not None:
            self.delegate.update_items(col_index, new_items)
