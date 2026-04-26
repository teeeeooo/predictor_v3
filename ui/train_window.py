# ui/train_window.py — 모델 학습 및 데이터 관리 윈도우 (엔지니어/관리자용)
import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QFileDialog, QTextEdit, QMessageBox, QLineEdit
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from core.constants import TRAIN_DATA_FILE
from core.trainer import train_all_models # 모델 학습 메인 함수 (가정)
from scripts.update_mapping import select_excel_file, update_mapping_to_json

class TrainWorker(QThread):
    """무거운 ML 학습 작업을 백그라운드에서 처리하기 위한 워커 스레드"""
    log_signal = pyqtSignal(str)           
    finished_signal = pyqtSignal(bool, str) 

    def __init__(self, data_path):
        super().__init__()
        self.data_path = data_path

    def run(self):
        """스레드가 시작되면 실행되는 메인 로직"""
        self.log_signal.emit(f"🚀 백그라운드 학습 스레드 시작...\n📁 대상 파일: {self.data_path}")
        try:
            # ✅ 사용자님의 수정본 완벽 적용: 반환값을 summary_report로 받기
            summary_report = train_all_models(
                data_path=self.data_path,
                log_callback=self.log_signal.emit
            )
            # ✅ 하드코딩된 메시지 대신 요약 리포트를 시그널로 전달!
            self.finished_signal.emit(True, summary_report)
            
        except Exception as e:
            self.finished_signal.emit(False, f"❌ 학습 중 치명적 오류 발생:\n{str(e)}")

class TrainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HVAC V3 - Trainer & Admin Data Manager")
        self.resize(800, 600)
        self.worker = None # 스레드 객체 보관용

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 1. 관리자용 데이터 도구 (JSON 업데이트)
        mapping_layout = QHBoxLayout()
        self.btn_update_mapping = QPushButton("📁 매핑 데이터(Excel) 업데이트")
        self.btn_update_mapping.setStyleSheet("background-color: #FFF2CC; font-weight: bold;")
        self.btn_update_mapping.setToolTip("엑셀 파일을 선택하여 mapping.json을 최신화합니다.")
        mapping_layout.addWidget(self.btn_update_mapping)
        mapping_layout.addStretch()
        layout.addLayout(mapping_layout)

        layout.addWidget(QLabel("<hr>")) # 구분선

        # 2. 학습 데이터 선택 영역
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("학습 데이터 (CSV):"))
        self.txt_file_path = QLineEdit(TRAIN_DATA_FILE) # 기본값 세팅
        self.txt_file_path.setReadOnly(True)
        self.btn_find_file = QPushButton("파일 찾기")
        
        file_layout.addWidget(self.txt_file_path)
        file_layout.addWidget(self.btn_find_file)
        layout.addLayout(file_layout)

        # 3. 학습 실행 버튼
        self.btn_start_train = QPushButton("⚙️ 머신러닝 모델 학습 시작 (Train All Models)")
        self.btn_start_train.setMinimumHeight(50)
        self.btn_start_train.setStyleSheet("background-color: #E6F3E6; font-size: 14px; font-weight: bold;")
        layout.addWidget(self.btn_start_train)

        # 4. 로그 출력 창 (진행 상황 표시)
        layout.addWidget(QLabel("진행 상황 로그:"))
        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        self.txt_log.setStyleSheet("background-color: #F8F9FA; font-family: Consolas;")
        layout.addWidget(self.txt_log)

    def _connect_signals(self):
        self.btn_update_mapping.clicked.connect(self.on_update_mapping_clicked)
        self.btn_find_file.clicked.connect(self.on_find_file_clicked)
        self.btn_start_train.clicked.connect(self.on_start_train_clicked)

    def on_update_mapping_clicked(self):
        """엑셀 매핑 파일을 JSON으로 변환하는 관리자 기능"""
        excel_file = select_excel_file()
        if excel_file:
            self.append_log(f"🔄 매핑 데이터 업데이트 중... ({os.path.basename(excel_file)})")
            update_mapping_to_json(excel_file)
            self.append_log("✅ mapping.json 업데이트 완료! (앱을 재시작하면 UI에 반영됩니다.)")

    def on_find_file_clicked(self):
        """학습용 CSV 파일 선택 다이얼로그"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "학습용 CSV 데이터 선택", "", "CSV Files (*.csv)"
        )
        if file_path:
            self.txt_file_path.setText(file_path)

    def on_start_train_clicked(self):
        """학습 시작 로직"""
        data_path = self.txt_file_path.text()
        if not os.path.exists(data_path):
            QMessageBox.warning(self, "파일 오류", "지정된 경로에 학습 데이터 파일이 없습니다.")
            return

        # 이중 실행 방지 (버튼 비활성화)
        self.btn_start_train.setEnabled(False)
        self.btn_start_train.setText("⏳ 학습 진행 중... (기다려주세요)")
        self.txt_log.clear()

        # -----------------------------------------------------
        # QThread 워커 생성 및 시그널 연결 (핵심 로직)
        # -----------------------------------------------------
        self.worker = TrainWorker(data_path)
        self.worker.log_signal.connect(self.append_log)
        self.worker.finished_signal.connect(self.on_training_finished)
        self.worker.start() # 스레드 시작 (run 메서드 백그라운드 실행)

    def append_log(self, text):
        """워커 스레드에서 받은 텍스트를 로그 창에 안전하게 추가"""
        self.txt_log.append(text)
        # 스크롤을 항상 맨 아래로 유지
        scrollbar = self.txt_log.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def on_training_finished(self, success, message):
        """학습 스레드가 종료되었을 때 호출됨"""
        self.append_log("-" * 40)
        self.append_log(message)
        
        if success:
            QMessageBox.information(self, "학습 완료", "모델 학습이 성공적으로 끝났습니다.\n예측 화면에서 바로 사용할 수 있습니다.")
        else:
            QMessageBox.critical(self, "학습 실패", message)

        # 버튼 원상복구
        self.btn_start_train.setEnabled(True)
        self.btn_start_train.setText("⚙️ 머신러닝 모델 학습 시작 (Train All Models)")
        self.worker = None # 스레드 객체 정리

