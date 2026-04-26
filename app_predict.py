# app_predict.py — HVAC 예측 시스템 메인 실행 파일 (사용자용)
import sys
from PyQt5.QtWidgets import QApplication

# 글로벌 에러 핸들러 임포트 (앱이 튕기는 현상 방지 및 로그 기록)
from core.utils import setup_global_exception_handler
from ui.predict_window import PredictWindow

def main():
    # 1. 글로벌 예외 핸들러 등록
    setup_global_exception_handler()

    # 2. PyQt5 애플리케이션 객체 생성
    app = QApplication(sys.argv)
    
    # OS 기본 스타일 적용 (선택 사항: Windows, Fusion 등)
    app.setStyle("Fusion")

    # 3. 메인 예측 윈도우 생성 및 표시
    print("🚀 HVAC 예측 시스템(V3)을 시작합니다...")
    window = PredictWindow()
    window.show()

    # 4. 이벤트 루프 실행
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

