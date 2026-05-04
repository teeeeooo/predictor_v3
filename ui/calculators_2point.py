from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QComboBox,
                             QLabel, QTableView, QHeaderView, QAbstractItemView,
                             QApplication, QTabWidget)
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex, QVariant, pyqtSignal, QTimer
from PyQt5.QtGui import QPainter, QPen, QColor, QFont, QKeySequence

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
            "EER Full", "EER Half", "ISO CSPF", "ISEER", "ISEER CSEC [kWh]"
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

    def set_calculators(self, iso_t1_calc, iseer_calc):
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
            elif col == 7: return f"{item['iso_cspf']:.3f}" if item["iso_cspf"] is not None else ""
            elif col == 8: return f"{item['iseer']:.3f}" if item["iseer"] is not None else ""
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

    def set_data(self, bin_details):
        self.bin_details = bin_details or []
        self.update()

    def clear(self):
        self.bin_details = []
        self.update()

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

            # Draw Load
            painter.setPen(QPen(QColor("red"), 2))
            for i in range(len(pts_lc)-1):
                painter.drawLine(int(pts_lc[i][0]), int(pts_lc[i][1]), int(pts_lc[i+1][0]), int(pts_lc[i+1][1]))
            # Draw Capacity
            painter.setPen(QPen(QColor("green"), 2))
            for i in range(len(pts_cap)-1):
                painter.drawLine(int(pts_cap[i][0]), int(pts_cap[i][1]), int(pts_cap[i+1][0]), int(pts_cap[i+1][1]))

            # Legend
            painter.setPen(QColor("red"))
            painter.drawText(self.width() - 120, margin_t + 10, "Cooling Load")
            painter.setPen(QColor("green"))
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
