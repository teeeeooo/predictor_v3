"""
core/utils.py - 공통 유틸리티 및 헬퍼 함수 모음

[포함된 기능 요약]
1. 수학 및 연산 안전장치 (0 나누기 방지 등)
2. 데이터 타입 및 딕셔너리 안전 변환
3. 외부 정적 데이터(JSON) 로드
4. 전역 시스템 에러 핸들링

[주의] 이 파일에는 sklearn, optuna, xgboost 등 무거운 ML 라이브러리를 절대 import 하지 마세요.
"""

import sys
import traceback
import os
from typing import Optional, Union
import datetime
import pandas as pd

from core.mapping.repository import load_mapping_data

# =============================================================================
# 1. 수학 및 연산 안전장치
# =============================================================================

def safe_divide(n: Union[int, float], d: Union[int, float]) -> float:
    """
    0 나누기(ZeroDivisionError)를 방지하는 안전한 나눗셈 함수입니다.
    분모가 0이거나 유효하지 않은 값이면 0.0을 반환합니다.
    """
    try:
        if d == 0:
            return 0.0
        return float(n) / float(d)
    except (TypeError, ValueError):
        return 0.0


# =============================================================================
# 2. 데이터 타입 및 딕셔너리 안전 변환
# =============================================================================

def safe_float_convert(value: any, default: float = 0.0) -> float:
    """
    입력값을 안전하게 float으로 변환합니다. 
    빈 문자열이나 변환 불가능한 값이면 default 값을 반환합니다.
    """
    if value is None:
        return default
    if isinstance(value, str) and not value.strip():
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def get_mapping_value(mapping_dict: dict, key: str, fallback: any = None) -> any:
    """
    딕셔너리에서 안전하게 값을 가져옵니다.
    키가 존재하지 않거나 빈 문자열인 경우 fallback 값을 반환합니다.
    """
    if not key or key not in mapping_dict:
        return fallback
    return mapping_dict[key]


# =============================================================================
# 4. 전역 시스템 에러 핸들링
# =============================================================================

def global_exception_handler(exc_type, exc_value, exc_traceback):
    """
    프로그램 전체의 처리되지 않은 예외(Unhandled Exception)를 잡아냅니다.
    UI 스레드가 뻗어버리는 것을 방지하고, 에러 로그를 명확히 남깁니다.
    """
    print("=" * 50, file=sys.stderr)
    print("🚨 치명적 오류 발생 (Unhandled Exception) 🚨", file=sys.stderr)
    print("=" * 50, file=sys.stderr)
    traceback.print_exception(exc_type, exc_value, exc_traceback)
    print("=" * 50, file=sys.stderr)

def setup_global_exception_handler():
    """
    글로벌 예외 핸들러를 시스템에 등록합니다.
    메인 애플리케이션 최상단에서 한 번 호출해야 합니다.
    """
    sys.excepthook = global_exception_handler

# =============================================================================
# 5. 학습 로그 저장
# =============================================================================
def get_timestamp_dir(log_type: str) -> str:
    """YYMMDD_HHMM 형식의 타임스탬프 폴더를 생성하고 경로를 반환합니다."""
    from core.common.paths import LOG_DIR
    now = datetime.datetime.now().strftime("%y%m%d_%H%M")
    path = os.path.join(LOG_DIR, log_type, now)
    os.makedirs(path, exist_ok=True)
    return path

def save_train_log_to_excel(results_list: list) -> str:
    """학습 결과 리스트를 엑셀 파일로 저장하고 저장 경로를 반환합니다."""
    log_path = get_timestamp_dir("train_log")
    file_path = os.path.join(log_path, "summary.xlsx")
    df = pd.DataFrame(results_list)
    df.to_excel(file_path, index=False)
    return file_path

# =============================================================================
# 6. 단위 변환 유틸리티
# =============================================================================


def w_to_kw(w: float) -> float:
    """W → kW 변환 (UI 출력 또는 EN 14825 규격 텍스트 매칭용)"""
    return w / 1000.0

def kw_to_w(kw: float) -> float:
    """kW → W 변환"""
    return kw * 1000.0

def w_to_btuh(w: float) -> float:
    """W → Btu/h 변환 (AHRI 계산기 입력용)"""
    return w * 3.41214

def btuh_to_w(btuh: float) -> float:
    """Btu/h → W 변환 (AHRI 계산 결과를 UI에 Metric으로 보여줄 때)"""
    return btuh / 3.41214

def celsius_to_fahrenheit(c: float) -> float:
    """°C → °F 변환 (AHRI 테스트 조건 매핑용)"""
    return c * 9.0 / 5.0 + 32.0

def fahrenheit_to_celsius(f: float) -> float:
    """°F → °C 변환"""
    return (f - 32.0) * 5.0 / 9.0
