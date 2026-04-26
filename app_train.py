# app_train.py — 모델 학습 및 매핑 데이터 관리 메인 실행 파일 (관리자용)
import sys
from PyQt5.QtWidgets import QApplication

# 글로벌 에러 핸들러 임포트
from core.utils import setup_global_exception_handler
from ui.train_window import TrainWindow

def main():
    # 1. 글로벌 예외 핸들러 등록
    setup_global_exception_handler()

    # 2. PyQt5 애플리케이션 객체 생성
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # 3. 모델 학습 및 관리 윈도우 생성 및 표시
    print("⚙️ HVAC Trainer 및 Data Manager를 시작합니다...")
    window = TrainWindow()
    window.show()

    # 4. 이벤트 루프 실행
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
