# core/ml/inference.py — 순방향 예측 엔진 (Inference Only)
import os
import joblib
import pandas as pd
import numpy as np

# 데이터 전처리 로직 재사용 (sklearn 의존성 없음)
from core.ml.preprocessing import calculate_derived_features
from core.ml.features import TARGETS, BASE_FEATURES

# 현재 시스템의 전처리 버전 (Lite 안전장치 v1.0)
CURRENT_PREPROCESS_VERSION = "v1.0"

def load_model(model_file):
    """
    통합 모델 파일(model.pkl)을 로드하고 버전을 검증합니다.
    """
    if not os.path.exists(model_file):
        raise FileNotFoundError(f"모델 파일을 찾을 수 없습니다: {model_file}")

    try:
        model_data = joblib.load(model_file)
    except Exception as e:
        raise IOError(f"모델 로드 중 오류 발생: {e}")

    # 1. preprocess_version 체크 (Lite 안전장치)
    model_version = model_data.get("preprocess_version")
    if model_version != CURRENT_PREPROCESS_VERSION:
        raise ValueError(
            f"모델 버전 불일치 (모델: {model_version}, 코드: {CURRENT_PREPROCESS_VERSION}). "
            "데이터 파이프라인이 변경되었으므로 재학습이 필요합니다."
        )

    return model_data

def build_input_df(row_dict):
    """
    UI에서 전달된 딕셔너리를 바탕으로 파생 피처가 포함된 DataFrame을 생성합니다.
    row_dict: {"Cooling Capa": 3500, "R32": 1, ...} 형태 (ml_feature 기준)
    """
    # 1. 딕셔너리를 단일 행 DataFrame으로 변환
    df = pd.DataFrame([row_dict])

    # 2. 누락된 기본 피처가 있는지 확인 (백그라운드 피처 포함)
    for feature in BASE_FEATURES:
        if feature not in df.columns:
            # TODO: ID/OD 온도 변수 (데이터 축적 후 추가 예정)
            # 현재는 0으로 채우며, BASE_FEATURES에 없으므로 실제로 실행 되지 않음
            df[feature] = 0.0

    # 3. 파생 피처 계산 (safe_divide 및 벡터 연산 적용됨)
    df_processed = calculate_derived_features(df)

    return df_processed


def predict_row(model_data, row_dict):
    """
    로드된 모델 데이터와 입력 딕셔너리를 사용하여 모든 타겟에 대한 예측을 수행합니다.
    """
    # 1. 입력 데이터 가공
    input_df = build_input_df(row_dict)

    results = {}

    # 2. 각 타겟별로 개별 모델 예측 수행
    for target in TARGETS:
        # 해당 타겟 학습 시 사용된 피처 리스트 로드
        required_features = model_data["features"].get(target)
        model = model_data["models"].get(target)

        if not required_features or not model:
            # 특정 모델이 누락된 경우 건너뛰거나 에러 처리
            continue

        # 3. 피처 존재 여부 엄격 검증
        for f in required_features:
            if f not in input_df.columns:
                raise ValueError(f"예측 불가: 필수 피처 '{f}'가 입력 데이터에 없습니다. (Target: {target})")

        # 4. 필요한 피처만 순서대로 추출하여 예측 (.values 없이 DataFrame 전달)
        # feature_names_in_ 보존을 위해 컬럼 순서까지 일치시킴
        X_input = input_df[required_features]

        pred_value = model.predict(X_input)

        # XGBoost는 기본적으로 배열을 반환하므로 첫 번째 값 추출
        results[target] = float(pred_value[0])

    return results

if __name__ == "__main__":
    # 테스트 코드 (사용 예시)
    from core.ml.artifacts import MODEL_FILE

    try:
        # 모델은 전역에서 한 번만 로드
        m_data = load_model(MODEL_FILE)

        # 테스트용 샘플 데이터 (ml_feature 명칭 사용)
        sample_row = {
            "Cooling Capa": 3500,
            "Heating Capa": 4000,
            "ID Volume": 0.015,
            "Evap Area": 12.5,
            "Evap Volume": 0.002,
            "OD Volume": 0.045,
            "Cond Area": 25.0,
            "Cond Volume": 0.005,
            "Comp EER": 3.5,
            "Comp cc": 10.5,
            "R32": 1,
            "R410A": 0,
            "R290": 0,
            "EEV": 1,
            "Capi": 0
        }

        # 예측 실행
        prediction = predict_row(m_data, sample_row)
        print("\n--- 예측 결과 ---")
        for k, v in prediction.items():
            print(f"{k}: {v:.2f}")

    except Exception as e:
        print(f"오류 발생: {e}")
