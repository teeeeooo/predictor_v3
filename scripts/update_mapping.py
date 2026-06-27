# scripts/update_mapping.py — 엑셀 매핑 테이블을 투 트랙 JSON으로 변환하는 유틸리티
import os
import sys

from PyQt5.QtWidgets import QApplication, QFileDialog

# 프로젝트 루트 경로를 시스템 패스에 추가하여 core 모듈 접근 가능하게 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.mapping.update import update_mapping_to_json

def select_excel_file():
    """윈도우 탐색기를 열어 엑셀 또는 CSV 파일을 선택하게 합니다."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
        
    file_path, _ = QFileDialog.getOpenFileName(
        None, 
        "매핑용 파일(Excel/CSV) 선택", 
        "", 
        "Excel/CSV Files (*.xlsx *.xls *.csv)" 
    )
    return file_path

if __name__ == "__main__":
    print("=" * 50)
    print("🔄 매핑 테이블(Excel -> JSON) 업데이트 시작")
    print("=" * 50)
    
    target_excel = select_excel_file()
    if target_excel:
        update_mapping_to_json(target_excel)
    else:
        print("❌ 파일 선택이 취소되었습니다.")
