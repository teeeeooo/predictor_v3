import os

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QComboBox,
                             QLabel, QTableView, QHeaderView, QAbstractItemView,
                             QApplication, QTabWidget, QPushButton, QDialog,
                             QGridLayout, QLineEdit, QCheckBox, QFrame,
                             QSizePolicy, QStyledItemDelegate, QAbstractItemDelegate)
from PyQt5.QtCore import (Qt, QAbstractTableModel, QModelIndex, QVariant,
                          pyqtSignal, QTimer, QEvent, QItemSelectionModel)
from PyQt5.QtGui import QPainter, QPen, QColor, QFont, QKeySequence, QBrush

from core.calculator_iso16358 import ISO16358Calculator

class TraceTableModel(QAbstractTableModel):
    def __init__(self):
        super().__init__()
        self._headers = ["Bin No", "Temp [°C]", "Hours", "Load [W]", "Capacity [W]", "Power [W]", "EER", "CSTL [Wh]", "CSEC [Wh]"]
        self._data = []

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self._headers)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._headers[section]
        return QVariant()

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or role != Qt.DisplayRole:
            return QVariant()
        row = index.row()
        col = index.column()
        item = self._data[row]
        
        val = None
        if col == 0: val = item.get("bin_no")
        elif col == 1: val = item.get("tj")
        elif col == 2: val = item.get("nj")
        elif col == 3: val = item.get("lc")
        elif col == 4: val = item.get("capacity")
        elif col == 5: val = item.get("power")
        elif col == 6: val = item.get("eer")
        elif col == 7: val = item.get("cstl_bin")
        elif col == 8: val = item.get("csec_bin")

        if val is None:
            return ""
        
        if isinstance(val, float):
            return f"{val:.2f}"
        return str(val)

    def set_data(self, bin_details):
        self.beginResetModel()
        self._data = bin_details or []
        self.endResetModel()

    def clear(self):
        self.set_data([])

class TwoPointTableModel(QAbstractTableModel):
    row_updated = pyqtSignal(int)
    model_results_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._headers = [
            "No", "35°C Full Cap [W]", "35°C Full Pwr [W]", 
            "35°C Half Cap [W]", "35°C Half Pwr [W]",
            "EER Full", "EER Half", "ISO CSPF", "India ISEER",
            "India CSEC [kWh]"
        ]
        self._rows = []
        self._updating = False
        self._bulk_updating = False
        self.iso_t1_calc = None
        self.iseer_calc = None
        for _ in range(3):
            self.add_row(emit=False)
            
        self._debounce_timer = QTimer()
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.setInterval(300)
        self._debounce_timer.timeout.connect(self._recalculate_pending)
        self._pending_recalc_rows = set()

    def set_calculators(self, iso_t1_calc, iseer_calc, hong_kong_calc=None):
        self.iso_t1_calc = iso_t1_calc
        self.iseer_calc = iseer_calc
        self.recalculate_rows(range(len(self._rows)))

    def rowCount(self, parent=QModelIndex()):
        return len(self._rows)

    def columnCount(self, parent=QModelIndex()):
        return len(self._headers)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._headers[section]
        return QVariant()

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        col = index.column()
        if 1 <= col <= 4:
            return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        
        row = index.row()
        col = index.column()
        item = self._rows[row]

        if role == Qt.DisplayRole or role == Qt.EditRole:
            if col == 0: return str(row + 1)
            elif col == 1: return item["full_cap"]
            elif col == 2: return item["full_pwr"]
            elif col == 3: return item["half_cap"]
            elif col == 4: return item["half_pwr"]
            elif col == 5: return f"{item['eer_full']:.2f}" if item["eer_full"] is not None else ""
            elif col == 6: return f"{item['eer_half']:.2f}" if item["eer_half"] is not None else ""
            elif col == 7: return f"{item['iso_cspf']:.2f}" if item["iso_cspf"] is not None else ""
            elif col == 8: return f"{item['iseer']:.2f}" if item["iseer"] is not None else ""
            elif col == 9: return f"{item['iseer_csec']:.1f}" if item["iseer_csec"] is not None else ""
            
        elif role == Qt.BackgroundRole:
            if col == 0: return QColor("#F0F0F0")
            elif 1 <= col <= 4: return QColor("white")
            elif 5 <= col <= 6: return QColor("#E8F5E9")
            elif 7 <= col <= 9:
                if item.get("error"):
                    return QColor("#FFEBEE")
                return QColor("#E3F2FD")
                
        elif role == Qt.ToolTipRole:
            if item.get("error") and col >= 7:
                return item["error"]

        return QVariant()

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid() or role != Qt.EditRole:
            return False
        
        col = index.column()
        if col < 1 or col > 4:
            return False

        if self._updating:
            return False
            
        row = index.row()
        val_str = str(value).strip()
        item = self._rows[row]

        if col == 1: item["full_cap"] = val_str
        elif col == 2: item["full_pwr"] = val_str
        elif col == 3: item["half_cap"] = val_str
        elif col == 4: item["half_pwr"] = val_str

        item["eer_full"] = self._calc_eer(item["full_cap"], item["full_pwr"])
        item["eer_half"] = self._calc_eer(item["half_cap"], item["half_pwr"])

        self.clear_row_results(row, emit=False)
        self.dataChanged.emit(self.index(row, 0), self.index(row, self.columnCount()-1))

        if self._bulk_updating:
            return True

        if self._is_row_ready(item):
            self._pending_recalc_rows.add(row)
            self._debounce_timer.start()
        else:
            self.row_updated.emit(row)
            self.model_results_changed.emit()

        return True
        
    def _calc_eer(self, cap_str, pwr_str):
        try:
            c = float(cap_str.replace(',', ''))
            p = float(pwr_str.replace(',', ''))
            if p > 0 and c > 0:
                return c / p
        except:
            pass
        return None

    def _is_row_ready(self, item):
        try:
            fc = float(item["full_cap"].replace(',', ''))
            fp = float(item["full_pwr"].replace(',', ''))
            hc = float(item["half_cap"].replace(',', ''))
            hp = float(item["half_pwr"].replace(',', ''))
            if fc > 0 and fp > 0 and hc > 0 and hp > 0:
                return True
        except:
            pass
        return False

    def add_row(self, emit=True):
        self.beginInsertRows(QModelIndex(), len(self._rows), len(self._rows))
        self._rows.append({
            "full_cap": "", "full_pwr": "", "half_cap": "", "half_pwr": "",
            "eer_full": None, "eer_half": None,
            "iso_cspf": None, "iseer": None, "iseer_csec": None,
            "iso_cstl": None, "iso_csec": None, "iseer_cstl": None,
            "iso_bin_details": None, "iseer_bin_details": None,
            "error": None
        })
        self.endInsertRows()
        if emit:
            self.model_results_changed.emit()

    def remove_row(self, row_index):
        if len(self._rows) <= 1:
            return
        if 0 <= row_index < len(self._rows):
            self.beginRemoveRows(QModelIndex(), row_index, row_index)
            self._rows.pop(row_index)
            self.endRemoveRows()
            self._pending_recalc_rows.discard(row_index)
            self._pending_recalc_rows = {r if r < row_index else r - 1 for r in self._pending_recalc_rows}
            self.model_results_changed.emit()

    def clear_row_results(self, row_index, emit=True):
        item = self._rows[row_index]
        item["iso_cspf"] = None
        item["iseer"] = None
        item["iseer_csec"] = None
        item["iso_cstl"] = None
        item["iso_csec"] = None
        item["iseer_cstl"] = None
        item["iso_bin_details"] = None
        item["iseer_bin_details"] = None
        item["error"] = None
        if emit:
            self.dataChanged.emit(self.index(row_index, 7), self.index(row_index, 9))
            self.row_updated.emit(row_index)
            self.model_results_changed.emit()

    def _recalculate_pending(self):
        self.recalculate_rows(list(self._pending_recalc_rows))
        self._pending_recalc_rows.clear()

    def recalculate_rows(self, row_indices):
        if not self.iso_t1_calc or not self.iseer_calc:
            return
            
        self._updating = True
        try:
            for row in row_indices:
                if 0 <= row < len(self._rows):
                    self.recalculate_row(row)
        finally:
            self._updating = False
            self.model_results_changed.emit()

    def recalculate_row(self, row_index):
        item = self._rows[row_index]
        if not self._is_row_ready(item):
            self.clear_row_results(row_index, emit=False)
            return

        try:
            inputs = {
                "35_full": {"capacity": float(item["full_cap"].replace(',', '')), "power": float(item["full_pwr"].replace(',', ''))},
                "35_half": {"capacity": float(item["half_cap"].replace(',', '')), "power": float(item["half_pwr"].replace(',', ''))}
            }
            
            iso_res = self.iso_t1_calc.calculate_cspf(inputs)
            iseer_res = self.iseer_calc.calculate_cspf(inputs)
            
            item["iso_cspf"] = iso_res.get("cspf")
            item["iso_cstl"] = iso_res.get("annual_cooling_kwh")
            item["iso_csec"] = iso_res.get("annual_power_kwh")
            item["iso_bin_details"] = iso_res.get("bin_details")

            item["iseer"] = iseer_res.get("cspf")
            item["iseer_cstl"] = iseer_res.get("annual_cooling_kwh")
            item["iseer_csec"] = iseer_res.get("annual_power_kwh")
            item["iseer_bin_details"] = iseer_res.get("bin_details")
            item["error"] = None
        except Exception as e:
            item["error"] = "계산 오류: " + str(e)
            item["iso_cspf"] = None
            item["iseer"] = None
            item["iseer_csec"] = None
            item["iso_cstl"] = None
            item["iso_csec"] = None
            item["iseer_cstl"] = None
            item["iso_bin_details"] = None
            item["iseer_bin_details"] = None
            
        self.dataChanged.emit(self.index(row_index, 7), self.index(row_index, 9))
        self.row_updated.emit(row_index)

    def get_row_result(self, row_index):
        if 0 <= row_index < len(self._rows):
            return self._rows[row_index]
        return None

    def get_available_result_rows(self):
        return [i for i, r in enumerate(self._rows) if r["iso_cspf"] is not None or r["iseer"] is not None]

    def paste_tsv(self, start_row, start_col, text):
        lines = text.strip('\n').split('\n')
        
        while start_row + len(lines) > len(self._rows):
            self.add_row(emit=False)
            
        self._updating = True
        self._bulk_updating = True
        affected_rows = set()
        try:
            for i, line in enumerate(lines):
                row = start_row + i
                vals = line.split('\t')
                for j, val in enumerate(vals):
                    col = start_col + j
                    if 1 <= col <= 4:
                        v = val.strip()
                        if col == 1: self._rows[row]["full_cap"] = v
                        elif col == 2: self._rows[row]["full_pwr"] = v
                        elif col == 3: self._rows[row]["half_cap"] = v
                        elif col == 4: self._rows[row]["half_pwr"] = v
                        
                item = self._rows[row]
                item["eer_full"] = self._calc_eer(item["full_cap"], item["full_pwr"])
                item["eer_half"] = self._calc_eer(item["half_cap"], item["half_pwr"])
                self.clear_row_results(row, emit=False)
                affected_rows.add(row)
                
                # Check row ready condition but do not trigger recalculate here
                if self._is_row_ready(item):
                    self._pending_recalc_rows.add(row)
        finally:
            self._updating = False
            self._bulk_updating = False
            self.dataChanged.emit(self.index(start_row, 1), self.index(start_row + len(lines) - 1, self.columnCount()-1))
            self.recalculate_rows(sorted(list(affected_rows)))

class TwoPointTableView(QTableView):
    def keyPressEvent(self, event):
        if event.matches(QKeySequence.Paste):
            model = self.model()
            if model and hasattr(model, 'paste_tsv'):
                clipboard = QApplication.clipboard()
                text = clipboard.text()
                indexes = self.selectedIndexes()
                if indexes:
                    start_row = min(i.row() for i in indexes)
                    start_col = min(i.column() for i in indexes)
                    if 1 <= start_col <= 4:
                        model.paste_tsv(start_row, start_col, text)
            return
        super().keyPressEvent(event)

class BinGraphWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(200)
        self.mode = "bin_hours"
        self.bin_details = []

    def set_mode(self, mode):
        self.mode = mode
        self.update()
        self.repaint()

    def set_data(self, bin_details):
        self.bin_details = bin_details or []
        self.update()
        self.repaint()

    def clear(self):
        self.bin_details = []
        self.update()
        self.repaint()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor("white"))

        if not self.bin_details:
            painter.setPen(QColor("gray"))
            painter.drawText(self.rect(), Qt.AlignCenter, "Trace data not available")
            return

        margin_l, margin_r, margin_t, margin_b = 50, 20, 20, 40
        w = self.width() - margin_l - margin_r
        h = self.height() - margin_t - margin_b

        # Draw axes
        painter.setPen(QPen(QColor("black"), 1))
        painter.drawLine(margin_l, margin_t, margin_l, margin_t + h)
        painter.drawLine(margin_l, margin_t + h, margin_l + w, margin_t + h)

        tj_vals = [d["tj"] for d in self.bin_details]
        min_tj, max_tj = min(tj_vals), max(tj_vals)
        if max_tj == min_tj: max_tj = min_tj + 1

        def get_x(tj):
            return margin_l + (tj - min_tj) / (max_tj - min_tj) * w

        if self.mode == "bin_hours":
            y_vals = [d["nj"] for d in self.bin_details]
            max_y = max(y_vals) if y_vals else 1
            max_y = max_y * 1.1 if max_y > 0 else 1

            def get_y(val):
                return margin_t + h - (val / max_y) * h

            painter.setPen(QPen(QColor("blue"), 2))
            pts = []
            for d in self.bin_details:
                x = get_x(d["tj"])
                y = get_y(d["nj"])
                pts.append((x, y))
                painter.drawEllipse(int(x)-2, int(y)-2, 4, 4)
            for i in range(len(pts)-1):
                painter.drawLine(int(pts[i][0]), int(pts[i][1]), int(pts[i+1][0]), int(pts[i+1][1]))

            painter.setPen(QColor("black"))
            painter.drawText(margin_l, margin_t - 5, "Hours")

        elif self.mode == "load_capacity":
            y_vals1 = [d["lc"] for d in self.bin_details]
            y_vals2 = [d["capacity"] for d in self.bin_details]
            max_y = max(max(y_vals1 + y_vals2), 1) * 1.1

            def get_y(val):
                return margin_t + h - (val / max_y) * h

            pts_lc = []
            pts_cap = []
            for d in self.bin_details:
                x = get_x(d["tj"])
                pts_lc.append((x, get_y(d["lc"])))
                pts_cap.append((x, get_y(d["capacity"])))

            capacity_pen = QPen(QColor("#2E7D32"), 3)
            load_pen = QPen(QColor("#C62828"), 2)
            load_pen.setStyle(Qt.DashLine)

            painter.setPen(capacity_pen)
            for i in range(len(pts_cap)-1):
                painter.drawLine(int(pts_cap[i][0]), int(pts_cap[i][1]), int(pts_cap[i+1][0]), int(pts_cap[i+1][1]))
            painter.setBrush(QBrush(QColor("#2E7D32")))
            for x, y in pts_cap:
                painter.drawRect(int(x) - 3, int(y) - 3, 6, 6)

            painter.setPen(load_pen)
            for i in range(len(pts_lc)-1):
                painter.drawLine(int(pts_lc[i][0]), int(pts_lc[i][1]), int(pts_lc[i+1][0]), int(pts_lc[i+1][1]))
            painter.setBrush(QBrush(QColor("#C62828")))
            for x, y in pts_lc:
                painter.drawEllipse(int(x) - 3, int(y) - 3, 6, 6)

            # Legend
            painter.setBrush(Qt.NoBrush)
            painter.setPen(QColor("#C62828"))
            painter.drawText(self.width() - 120, margin_t + 10, "Cooling Load")
            painter.setPen(QColor("#2E7D32"))
            painter.drawText(self.width() - 120, margin_t + 25, "Capacity")
            painter.setPen(QColor("black"))
            painter.drawText(margin_l, margin_t - 5, "Watts")

class TraceDetailPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.two_point_model = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("대상:"))
        self.combo_row_select = QComboBox()
        top_layout.addWidget(self.combo_row_select)
        top_layout.addStretch()
        layout.addLayout(top_layout)

        self.std_tabs = QTabWidget()
        
        # ISO Tab
        self.tab_iso = QWidget()
        self.layout_iso = QVBoxLayout(self.tab_iso)
        self.iso_summary = QLabel()
        self.iso_summary.setStyleSheet("background: #F5F5F5; border-radius: 6px; padding: 8px 12px; font-weight: bold; font-size: 14px;")
        self.layout_iso.addWidget(self.iso_summary)
        
        self.iso_graph_combo = QComboBox()
        self.iso_graph_combo.addItems(["bin_hours", "load_capacity"])
        self.iso_graph_combo.currentTextChanged.connect(lambda text: self.iso_graph.set_mode(text))
        self.layout_iso.addWidget(self.iso_graph_combo)
        
        self.iso_graph = BinGraphWidget()
        self.layout_iso.addWidget(self.iso_graph)
        
        self.iso_table_view = QTableView()
        self.iso_table_model = TraceTableModel()
        self.iso_table_view.setModel(self.iso_table_model)
        self.iso_table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout_iso.addWidget(self.iso_table_view)
        
        self.std_tabs.addTab(self.tab_iso, "ISO 16358 T1")
        
        # ISEER Tab
        self.tab_iseer = QWidget()
        self.layout_iseer = QVBoxLayout(self.tab_iseer)
        self.iseer_summary = QLabel()
        self.iseer_summary.setStyleSheet("background: #F5F5F5; border-radius: 6px; padding: 8px 12px; font-weight: bold; font-size: 14px;")
        self.layout_iseer.addWidget(self.iseer_summary)
        
        self.iseer_graph_combo = QComboBox()
        self.iseer_graph_combo.addItems(["bin_hours", "load_capacity"])
        self.iseer_graph_combo.currentTextChanged.connect(lambda text: self.iseer_graph.set_mode(text))
        self.layout_iseer.addWidget(self.iseer_graph_combo)
        
        self.iseer_graph = BinGraphWidget()
        self.layout_iseer.addWidget(self.iseer_graph)
        
        self.iseer_table_view = QTableView()
        self.iseer_table_model = TraceTableModel()
        self.iseer_table_view.setModel(self.iseer_table_model)
        self.iseer_table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout_iseer.addWidget(self.iseer_table_view)
        
        self.std_tabs.addTab(self.tab_iseer, "India ISEER")

        layout.addWidget(self.std_tabs)

        self.combo_row_select.currentIndexChanged.connect(self.update_for_selected_row)
        self.std_tabs.currentChanged.connect(self.update_for_selected_row)

    def set_table_model(self, model):
        self.two_point_model = model

    def refresh_available_rows(self):
        if not self.two_point_model:
            return
        
        current_data = self.combo_row_select.currentData()
        self.combo_row_select.blockSignals(True)
        self.combo_row_select.clear()
        
        avail_rows = self.two_point_model.get_available_result_rows()
        for r in avail_rows:
            self.combo_row_select.addItem(f"No.{r+1}", r)
            
        # Try to restore selection
        if current_data is not None:
            idx = self.combo_row_select.findData(current_data)
            if idx >= 0:
                self.combo_row_select.setCurrentIndex(idx)
                
        self.combo_row_select.blockSignals(False)
        self.update_for_selected_row()

    def update_for_selected_row(self):
        idx = self.combo_row_select.currentIndex()
        if idx < 0 or not self.two_point_model:
            self.clear()
            return
            
        row = self.combo_row_select.itemData(idx)
        res = self.two_point_model.get_row_result(row)
        if not res:
            self.clear()
            return
            
        is_iso = self.std_tabs.currentIndex() == 0
        if is_iso:
            self.iso_summary.setText(f"CSPF: {res.get('iso_cspf', '')} | CSTL: {res.get('iso_cstl', '')} kWh | CSEC: {res.get('iso_csec', '')} kWh")
            bdetails = res.get("iso_bin_details", [])
            self.iso_table_model.set_data(bdetails)
            self.iso_graph.set_data(bdetails)
        else:
            self.iseer_summary.setText(f"ISEER: {res.get('iseer', '')} | CSTL: {res.get('iseer_cstl', '')} kWh | CSEC: {res.get('iseer_csec', '')} kWh")
            bdetails = res.get("iseer_bin_details", [])
            self.iseer_table_model.set_data(bdetails)
            self.iseer_graph.set_data(bdetails)

    def clear(self):
        self.iso_summary.setText("결과 없음")
        self.iso_table_model.clear()
        self.iso_graph.clear()
        self.iseer_summary.setText("결과 없음")
        self.iseer_table_model.clear()
        self.iseer_graph.clear()


class ProfileInputGridModel(QAbstractTableModel):
    values_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._points = []
        self._values = []
        self._bulk_updating = False
        self._undo_stack = []

    def rowCount(self, parent=QModelIndex()):
        return 2

    def columnCount(self, parent=QModelIndex()):
        return len(self._points)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal and 0 <= section < len(self._points):
                return self._points[section][0]
            if orientation == Qt.Vertical:
                return ("Capacity [W]", "Power [W]")[section]
        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        return QVariant()

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return QVariant()
        row = index.row()
        col = index.column()
        if role in (Qt.DisplayRole, Qt.EditRole):
            return self._values[row][col]
        if role == Qt.BackgroundRole:
            return QColor("#FFFFFF")
        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        return QVariant()

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid() or role != Qt.EditRole:
            return False
        new_value = str(value).strip()
        row = index.row()
        col = index.column()
        old_value = self._values[row][col]
        if old_value == new_value:
            return True
        if not self._bulk_updating:
            self._undo_stack.append([(row, col, old_value)])
        self._values[row][col] = new_value
        self.dataChanged.emit(index, index)
        if not self._bulk_updating:
            self.values_changed.emit()
        return True

    def set_points(self, points):
        old = {}
        for col, (_, key) in enumerate(self._points):
            if self._values:
                old[key] = (self._values[0][col], self._values[1][col])

        self.beginResetModel()
        self._points = list(points)
        self._values = [["" for _ in self._points], ["" for _ in self._points]]
        for col, (_, key) in enumerate(self._points):
            if key in old:
                self._values[0][col], self._values[1][col] = old[key]
        self._undo_stack = []
        self.endResetModel()
        self.values_changed.emit()

    def paste_tsv(self, start_row, start_col, text):
        if not text:
            return
        rows = text.strip("\n").split("\n")
        if not rows:
            return
        self._bulk_updating = True
        changed = False
        undo_entry = []
        try:
            for r_offset, line in enumerate(rows):
                row = start_row + r_offset
                if row >= self.rowCount():
                    break
                for c_offset, value in enumerate(line.split("\t")):
                    col = start_col + c_offset
                    if col >= self.columnCount():
                        break
                    new_value = value.strip()
                    old_value = self._values[row][col]
                    if old_value != new_value:
                        undo_entry.append((row, col, old_value))
                        self._values[row][col] = new_value
                        changed = True
        finally:
            self._bulk_updating = False
        if changed:
            self._undo_stack.append(undo_entry)
            top = self.index(start_row, start_col)
            bottom = self.index(self.rowCount() - 1, self.columnCount() - 1)
            self.dataChanged.emit(top, bottom)
            self.values_changed.emit()

    def undo(self):
        if not self._undo_stack:
            return
        entry = self._undo_stack.pop()
        changed_indexes = []
        for row, col, old_value in entry:
            if 0 <= row < self.rowCount() and 0 <= col < self.columnCount():
                self._values[row][col] = old_value
                changed_indexes.append(self.index(row, col))
        if not changed_indexes:
            return
        min_row = min(index.row() for index in changed_indexes)
        max_row = max(index.row() for index in changed_indexes)
        min_col = min(index.column() for index in changed_indexes)
        max_col = max(index.column() for index in changed_indexes)
        self.dataChanged.emit(self.index(min_row, min_col), self.index(max_row, max_col))
        self.values_changed.emit()

    def parsed_points(self, required_keys=None):
        required = set(required_keys or [key for _, key in self._points])
        parsed = {}
        for col, (_, key) in enumerate(self._points):
            if key not in required:
                continue
            cap = self._parse_cell(self._values[0][col])
            pwr = self._parse_cell(self._values[1][col])
            if cap is None or pwr is None:
                return None
            parsed[key] = {"capacity": cap, "power": pwr}
        return parsed

    def value(self, point_key, field):
        row = 0 if field == "capacity" else 1
        for col, (_, key) in enumerate(self._points):
            if key == point_key:
                return self._parse_cell(self._values[row][col])
        return None

    def _parse_cell(self, text):
        value = str(text).replace(",", "").strip()
        if not value:
            return None
        try:
            number = float(value)
        except ValueError:
            return None
        return number if number > 0 else None


class ProfileInputGridDelegate(QStyledItemDelegate):
    def __init__(self, view):
        super().__init__(view)
        self.view = view

    def createEditor(self, parent, option, index):
        editor = super().createEditor(parent, option, index)
        editor.installEventFilter(self)
        if hasattr(editor, "setAlignment"):
            editor.setAlignment(Qt.AlignCenter)
        return editor

    def eventFilter(self, editor, event):
        if event.type() == QEvent.KeyPress and event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.commitData.emit(editor)
            self.closeEditor.emit(editor, QAbstractItemDelegate.NoHint)
            self.view.move_to_next_cell()
            return True
        return super().eventFilter(editor, event)


class ProfileInputGridView(QTableView):
    def __init__(self):
        super().__init__()
        self.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setItemDelegate(ProfileInputGridDelegate(self))
        self.setShowGrid(True)
        self.setGridStyle(Qt.SolidLine)
        self.setCornerButtonEnabled(False)
        self.setTabKeyNavigation(True)
        self.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.verticalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.verticalHeader().setDefaultSectionSize(34)
        self.verticalHeader().setHighlightSections(False)
        self.horizontalHeader().setHighlightSections(False)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setAlternatingRowColors(False)
        self.setFixedHeight(96)
        self.setStyleSheet("""
            QTableView {
                background: #FFFFFF;
                gridline-color: #AEB8C4;
                border: 1px solid #AEB8C4;
                selection-background-color: #CFE5FF;
                selection-color: #102A43;
            }
            QTableView::item {
                border: 1px solid #C4CCD6;
                padding: 4px;
            }
            QHeaderView::section {
                background: #F3F6F9;
                border: 1px solid #B7C0CC;
                padding: 4px;
                font-weight: 600;
            }
        """)

    def fit_to_contents(self):
        height = self.horizontalHeader().height() + self.verticalHeader().length() + (2 * self.frameWidth())
        self.setFixedHeight(max(height, 90))

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.Paste):
            model = self.model()
            indexes = self.selectedIndexes()
            if model and hasattr(model, "paste_tsv") and indexes:
                model.paste_tsv(
                    min(index.row() for index in indexes),
                    min(index.column() for index in indexes),
                    QApplication.clipboard().text(),
                )
            return
        if event.matches(QKeySequence.Undo):
            model = self.model()
            if model and hasattr(model, "undo"):
                model.undo()
            return
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.move_to_next_cell()
            return
        super().keyPressEvent(event)

    def move_to_next_cell(self):
        model = self.model()
        current = self.currentIndex()
        if not model or not current.isValid():
            return
        row = current.row()
        col = current.column() + 1
        if col >= model.columnCount():
            col = 0
            row += 1
        if row >= model.rowCount():
            row = model.rowCount() - 1
            col = model.columnCount() - 1
        next_index = model.index(row, col)
        self.setCurrentIndex(next_index)
        self.selectionModel().select(next_index, QItemSelectionModel.ClearAndSelect)
        self.edit(next_index)


class RegionResultTableModel(QAbstractTableModel):
    def __init__(self):
        super().__init__()
        self._headers = []
        self._rows = []

    def rowCount(self, parent=QModelIndex()):
        return len(self._rows)

    def columnCount(self, parent=QModelIndex()):
        return len(self._headers)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._headers[section]
        return QVariant()

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return QVariant()

        row = self._rows[index.row()]
        col = index.column()
        if role == Qt.DisplayRole:
            return row[col] if col < len(row) else ""
        if role == Qt.BackgroundRole:
            if col == 0:
                return QColor("#F4F6F8")
            if row[0] and any(row[1:]):
                return QColor("#EAF4FF")
            return QColor("#FAFAFA")
        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        return QVariant()

    def set_schema(self, headers, rows):
        self.beginResetModel()
        self._headers = headers
        self._rows = rows
        self.endResetModel()

    def clear(self):
        self.beginResetModel()
        self._rows = []
        self.endResetModel()


class RegionDetailTab(QWidget):
    def __init__(self, title):
        super().__init__()
        self.title = title
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        self.summary = QLabel("결과 없음")
        self.summary.setStyleSheet(
            "background: #F4F6F8; border: 1px solid #D8DEE6; "
            "border-radius: 8px; padding: 10px 12px; font-weight: bold;"
        )
        layout.addWidget(self.summary)

        selector_row = QHBoxLayout()
        selector_row.addWidget(QLabel("Graph"))
        self.graph_combo = QComboBox()
        self.graph_combo.addItem("Bin Hours", "bin_hours")
        self.graph_combo.addItem("Load vs Capacity", "load_capacity")
        selector_row.addWidget(self.graph_combo)
        selector_row.addStretch()
        layout.addLayout(selector_row)

        self.graph = BinGraphWidget()
        self.graph.setMinimumHeight(210)
        layout.addWidget(self.graph)

        self.table_model = TraceTableModel()
        self.table = QTableView()
        self.table.setModel(self.table_model)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setMinimumHeight(260)
        layout.addWidget(self.table)

        self.graph_combo.currentIndexChanged.connect(self._on_graph_mode_changed)

    def _on_graph_mode_changed(self):
        self.graph.set_mode(self.graph_combo.currentData())

    def set_result(self, result):
        if not result:
            self.clear()
            return
        self.summary.setText(
            f"CSPF: {_fmt(result.get('cspf'), 2)}   "
            f"CSTL [kWh]: {_fmt(result.get('annual_cooling_kwh'), 1)}   "
            f"CSEC [kWh]: {_fmt(result.get('annual_power_kwh'), 1)}"
        )
        details = result.get("bin_details") or []
        self.table_model.set_data(details)
        self.graph.set_data(details)

    def clear(self):
        self.summary.setText("결과 없음")
        self.table_model.clear()
        self.graph.clear()


class BatchTwoPointDialog(QDialog):
    def __init__(self, calculators, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ISO/ISEER 2점식 Multi 입력")
        self.resize(1180, 540)

        layout = QVBoxLayout(self)
        title = QLabel("ISO/ISEER 2점식 Multi 입력")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)

        self.model = TwoPointTableModel()
        self.model.set_calculators(
            calculators.get("iso"),
            calculators.get("india"),
        )
        self.view = TwoPointTableView()
        self.view.setModel(self.model)
        self.view.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.view.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.view.verticalHeader().setVisible(False)
        self.view.setAlternatingRowColors(True)
        layout.addWidget(self.view)

        buttons = QHBoxLayout()
        self.btn_add = QPushButton("행 추가")
        self.btn_remove = QPushButton("행 삭제")
        self.status = QLabel("입력 컬럼에 붙여넣으면 자동 계산됩니다.")
        buttons.addWidget(self.btn_add)
        buttons.addWidget(self.btn_remove)
        buttons.addWidget(self.status)
        buttons.addStretch()
        layout.addLayout(buttons)

        self.btn_add.clicked.connect(self.model.add_row)
        self.btn_remove.clicked.connect(self._remove_selected_row)
        self.model.model_results_changed.connect(lambda: self.status.setText("자동 계산 완료"))

    def _remove_selected_row(self):
        indexes = self.view.selectionModel().selectedIndexes()
        if not indexes:
            return
        self.model.remove_row(min(index.row() for index in indexes))


class IsoCspfSingleWidget(QWidget):
    PROFILE_TWO_POINT = "ISO / ISEER 2점식"
    PROFILE_HONG_KONG = "Hong Kong CSPF"
    PROFILE_SASO_T3 = "SASO T3"

    TWO_POINT_REGIONS = [
        ("iso", "ISO 16358-1"),
        ("india", "India ISEER"),
    ]

    TWO_POINT_INPUTS = [("35 Full", "35_full"), ("35 Half", "35_half")]
    SASO_INPUTS_REQUIRED = [("46 Full", "46_full"), ("35 Full", "35_full"), ("35 Half", "35_half")]
    SASO_INPUTS_WITH_MIN = SASO_INPUTS_REQUIRED + [("35 Min", "35_min")]

    def __init__(self, config_dir, parent=None):
        super().__init__(parent)
        self.config_dir = config_dir
        self.calculators = {}
        self.saso_path = os.path.join(self.config_dir, "saso.json")
        self.results = {}
        self._updating_profile = False
        self._load_calculators()
        self._init_ui()
        self._apply_profile()

    def _load_calculators(self):
        paths = {
            "iso": "iso_t1_default_2point.json",
            "india": "india_iseer.json",
            "hong_kong": "hong_kong.json",
            "saso": "saso.json",
        }
        for key, filename in paths.items():
            self.calculators[key] = ISO16358Calculator(os.path.join(self.config_dir, filename))

    def _init_ui(self):
        self.setStyleSheet("""
            QWidget { background: #F6F7F9; }
            QFrame#panel { background: #FFFFFF; border: 1px solid #DCE1E7; border-radius: 8px; }
            QLineEdit { background: #FFFFFF; border: 1px solid #C8D0DA; border-radius: 5px; padding: 6px; }
            QLineEdit:disabled { background: #EEF1F4; color: #8A94A3; }
            QPushButton { background: #2F6F9F; color: white; border: 0; border-radius: 6px; padding: 8px 12px; }
            QPushButton:hover { background: #285F88; }
            QTableView { background: #FFFFFF; alternate-background-color: #F8FAFC; gridline-color: #E1E6EE; }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        top = self._panel()
        top_layout = QHBoxLayout(top)
        top_layout.addWidget(QLabel("Profile"))
        self.combo_profile = QComboBox()
        self.combo_profile.addItems([self.PROFILE_TWO_POINT, self.PROFILE_HONG_KONG, self.PROFILE_SASO_T3])
        top_layout.addWidget(self.combo_profile)
        top_layout.addStretch()
        self.btn_batch = QPushButton("Multi 입력")
        top_layout.addWidget(self.btn_batch)
        layout.addWidget(top)

        self.input_panel = self._panel()
        self.input_layout = QVBoxLayout(self.input_panel)
        self.input_layout.setSpacing(8)
        layout.addWidget(self.input_panel)

        result_panel = self._panel()
        result_layout = QVBoxLayout(result_panel)
        result_layout.addWidget(QLabel("Region/Profile 결과"))
        self.result_model = RegionResultTableModel()
        self.result_table = QTableView()
        self.result_table.setModel(self.result_model)
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.result_table.verticalHeader().setVisible(False)
        self.result_table.setAlternatingRowColors(True)
        self.result_table.setMinimumHeight(132)
        result_layout.addWidget(self.result_table)
        self.status = QLabel("계산 대기")
        self.status.setStyleSheet("color: #526071;")
        result_layout.addWidget(self.status)
        layout.addWidget(result_panel)

        self.btn_detail = QPushButton("상세 보기 ↓")
        self.btn_detail.setStyleSheet(
            "background: #FFFFFF; color: #2F455C; border: 1px solid #C8D0DA; "
            "border-radius: 6px; padding: 8px 12px;"
        )
        layout.addWidget(self.btn_detail)

        self.detail_panel = self._panel()
        self.detail_layout = QVBoxLayout(self.detail_panel)
        self.detail_tabs = QTabWidget()
        self.detail_layout.addWidget(self.detail_tabs)
        self.detail_panel.setVisible(False)
        layout.addWidget(self.detail_panel)
        layout.addStretch()

        self.combo_profile.currentIndexChanged.connect(self._apply_profile)
        self.btn_batch.clicked.connect(self._open_batch_dialog)
        self.btn_detail.clicked.connect(self._toggle_detail)

    def _panel(self):
        panel = QFrame()
        panel.setObjectName("panel")
        panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        return panel

    def _apply_profile(self):
        self._updating_profile = True
        try:
            self._clear_layout(self.input_layout)
            self.results = {}
            self.result_model.clear()
            self._clear_detail_tabs()
            profile = self.combo_profile.currentText()
            if profile == self.PROFILE_SASO_T3:
                self._build_saso_inputs()
                self._build_detail_tabs([("saso", "SASO T3")])
                self.btn_batch.setEnabled(False)
                self.btn_batch.setToolTip("SASO T3 Multi 입력은 후속 지원 예정입니다.")
            elif profile == self.PROFILE_HONG_KONG:
                self._build_hong_kong_inputs()
                self._build_detail_tabs([("hong_kong", "Hong Kong CSPF")])
                self.btn_batch.setEnabled(False)
                self.btn_batch.setToolTip("Hong Kong Multi 입력은 후속 지원 예정입니다.")
            else:
                self._build_two_point_inputs()
                self._build_detail_tabs(self.TWO_POINT_REGIONS)
                self.btn_batch.setEnabled(True)
                self.btn_batch.setToolTip("")
            self.status.setText("계산 대기")
        finally:
            self._updating_profile = False
        self._recalculate()

    def _build_two_point_inputs(self):
        self.input_layout.addWidget(QLabel("시험 입력"))
        self._install_input_grid(self.TWO_POINT_INPUTS)

    def _build_hong_kong_inputs(self):
        top = QHBoxLayout()
        label = QLabel("Rated/Declared Capacity [W]")
        self.declared_capacity = QLineEdit()
        self.declared_capacity.setPlaceholderText("예: 3500")
        self.declared_capacity.textChanged.connect(self._recalculate)
        top.addWidget(label)
        top.addWidget(self.declared_capacity)
        top.addStretch()
        self.input_layout.addLayout(top)
        self.input_layout.addWidget(QLabel("시험 입력"))
        self._install_input_grid(self.TWO_POINT_INPUTS)

    def _build_saso_inputs(self):
        self.chk_saso_min = QCheckBox("35°C Minimum 사용")
        self.input_layout.addWidget(self.chk_saso_min)
        self.chk_saso_min.toggled.connect(self._on_saso_min_toggled)
        self.input_layout.addWidget(QLabel("시험 입력"))
        self._install_input_grid(self.SASO_INPUTS_REQUIRED)

    def _on_saso_min_toggled(self, checked):
        self.input_model.set_points(self.SASO_INPUTS_WITH_MIN if checked else self.SASO_INPUTS_REQUIRED)
        QTimer.singleShot(0, self.input_view.fit_to_contents)
        self._recalculate()

    def _install_input_grid(self, points):
        self.input_model = ProfileInputGridModel()
        self.input_view = ProfileInputGridView()
        self.input_view.setModel(self.input_model)
        self.input_model.values_changed.connect(self._recalculate)
        self.input_model.set_points(points)
        self.input_layout.addWidget(self.input_view)
        QTimer.singleShot(0, self.input_view.fit_to_contents)

    def _recalculate(self):
        if self._updating_profile:
            return
        profile = self.combo_profile.currentText()
        if profile == self.PROFILE_SASO_T3:
            self._recalculate_saso()
        elif profile == self.PROFILE_HONG_KONG:
            self._recalculate_hong_kong()
        else:
            self._recalculate_two_point()

    def _recalculate_two_point(self):
        measured = self.input_model.parsed_points()
        headers = ["Region/Profile", "EER-Full", "EER-Half", "CSPF/SEER", "CSTL [kWh]", "CSEC [kWh]"]
        blank_rows = [[label, "", "", "", "", ""] for _, label in self.TWO_POINT_REGIONS]
        if measured is None:
            self.results = {}
            self.result_model.set_schema(headers, blank_rows)
            self._resize_result_table()
            self._update_detail_tabs()
            self.status.setText("입력값 부족")
            return

        rows = []
        self.results = {}
        for key, label in self.TWO_POINT_REGIONS:
            try:
                result = self.calculators[key].calculate_cspf(measured)
                self.results[key] = result
                rows.append([
                    label,
                    _fmt(_eer(measured, "35_full"), 2),
                    _fmt(_eer(measured, "35_half"), 2),
                    _fmt(result.get("cspf"), 2),
                    _fmt(result.get("annual_cooling_kwh"), 1),
                    _fmt(result.get("annual_power_kwh"), 1),
                ])
            except Exception:
                rows.append([label, "", "", "", "", ""])
        self.result_model.set_schema(headers, rows)
        self._resize_result_table()
        self._update_detail_tabs()
        self.status.setText("자동 계산 완료" if self.results else "계산 대기")

    def _recalculate_hong_kong(self):
        measured = self.input_model.parsed_points()
        declared_capacity = _parse_positive_number(self.declared_capacity.text())
        headers = ["Region/Profile", "EER-Full", "EER-Half", "CSPF", "CSTL [kWh]", "CSEC [kWh]"]
        if measured is None or declared_capacity is None:
            self.results = {}
            self.result_model.set_schema(headers, [["Hong Kong CSPF", "", "", "", "", ""]])
            self._resize_result_table()
            self._update_detail_tabs()
            self.status.setText("입력값 부족")
            return

        try:
            result = self.calculators["hong_kong"].calculate_cspf(
                measured,
                declared_capacity=declared_capacity,
            )
            self.results = {"hong_kong": result}
            row = [
                "Hong Kong CSPF",
                _fmt(_eer(measured, "35_full"), 2),
                _fmt(_eer(measured, "35_half"), 2),
                _fmt(result.get("cspf"), 2),
                _fmt(result.get("annual_cooling_kwh"), 1),
                _fmt(result.get("annual_power_kwh"), 1),
            ]
            self.status.setText("자동 계산 완료")
        except Exception:
            self.results = {}
            row = ["Hong Kong CSPF", "", "", "", "", ""]
            self.status.setText("계산 대기")
        self.result_model.set_schema(headers, [row])
        self._resize_result_table()
        self._update_detail_tabs()

    def _recalculate_saso(self):
        use_min = self.chk_saso_min.isChecked()
        points = self.SASO_INPUTS_WITH_MIN if use_min else self.SASO_INPUTS_REQUIRED
        measured = self.input_model.parsed_points([key for _, key in points])
        headers = [
            "Region/Profile", "EER 46-Full", "EER 35-Full", "EER 35-Half",
            "EER 35-Min", "CSPF", "CSTL [kWh]", "CSEC [kWh]"
        ]
        if measured is None:
            self.results = {}
            self.result_model.set_schema(headers, [["SASO T3", "", "", "", "", "", "", ""]])
            self._resize_result_table()
            self._update_detail_tabs()
            self.status.setText("입력값 부족")
            return

        try:
            result = self._saso_calculator(use_min).calculate_cspf(measured)
            self.results = {"saso": result}
            row = [
                "SASO T3",
                _fmt(_eer(measured, "46_full"), 2),
                _fmt(_eer(measured, "35_full"), 2),
                _fmt(_eer(measured, "35_half"), 2),
                _fmt(_eer(measured, "35_min"), 2) if use_min else "",
                _fmt(result.get("cspf"), 2),
                _fmt(result.get("annual_cooling_kwh"), 1),
                _fmt(result.get("annual_power_kwh"), 1),
            ]
            self.status.setText("자동 계산 완료")
        except Exception:
            self.results = {}
            row = ["SASO T3", "", "", "", "", "", "", ""]
            self.status.setText("계산 대기")
        self.result_model.set_schema(headers, [row])
        self._resize_result_table()
        self._update_detail_tabs()

    def _saso_calculator(self, use_min):
        calculator = ISO16358Calculator(self.saso_path)
        if not use_min:
            calculator.config.setdefault("cspf_test_profile", {})["test_selection"] = "required_only"
        return calculator

    def _build_detail_tabs(self, tabs):
        self.detail_widgets = {}
        for key, label in tabs:
            tab = RegionDetailTab(label)
            self.detail_widgets[key] = tab
            self.detail_tabs.addTab(tab, label)

    def _clear_detail_tabs(self):
        self.detail_widgets = {}
        while self.detail_tabs.count():
            self.detail_tabs.removeTab(0)

    def _update_detail_tabs(self):
        for key, widget in self.detail_widgets.items():
            widget.set_result(self.results.get(key))

    def _resize_result_table(self):
        header = self.result_table.horizontalHeader()
        if self.result_model.columnCount() > 0:
            header.setSectionResizeMode(0, QHeaderView.Interactive)
            self.result_table.setColumnWidth(0, 180)
        for col in range(1, self.result_model.columnCount()):
            header.setSectionResizeMode(col, QHeaderView.Stretch)

    def _toggle_detail(self):
        visible = not self.detail_panel.isVisible()
        self.detail_panel.setVisible(visible)
        self.btn_detail.setText("상세 닫기 ↑" if visible else "상세 보기 ↓")
        if visible:
            self._update_detail_tabs()

    def _open_batch_dialog(self):
        if not self.btn_batch.isEnabled():
            return
        dialog = BatchTwoPointDialog(self.calculators, self)
        dialog.exec_()

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            child_layout = item.layout()
            if child_layout:
                self._clear_layout(child_layout)
            widget = item.widget()
            if widget:
                widget.deleteLater()


def _fmt(value, digits):
    if value is None:
        return ""
    try:
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return ""


def _parse_positive_number(text):
    try:
        value = float(str(text).replace(",", "").strip())
    except ValueError:
        return None
    return value if value > 0 else None


def _eer(measured, point_key):
    point = measured.get(point_key)
    if not point:
        return None
    power = point.get("power")
    if not power:
        return None
    return point.get("capacity") / power
