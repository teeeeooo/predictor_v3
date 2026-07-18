# core/ml/preprocessing.py — 전처리 및 데이터 공급 전용
import pandas as pd
# 학습 라이브러리(sklearn 등) 임포트 금지 (배포 환경 최적화)
from core.ml.features import BASE_FEATURES, TARGETS, DERIVED_FEATURES
from core.ml.derived_adapter import current_derived_evaluation_snapshot
from core.data_definition.derived.evaluator import evaluate_derived_features

def calculate_derived_features(df, definitions=None):
    """
    8가지 파생 피처(DERIVED_FEATURES)를 계산합니다.
    Pandas/Numpy 벡터 연산만 사용하여 가볍고 빠릅니다.
    """
    snapshot = definitions or current_derived_evaluation_snapshot()
    return evaluate_derived_features(df, snapshot)

def prepare_pipeline(df, config):
    """
    모델 설정에 맞춰 피처/타겟 분리 및 Leakage 제거.
    이 함수는 'Pipeline' 객체를 반환하는 것이 아니라 데이터를 정제하여 반환합니다.
    """
    # 1. 파생 피처 계산
    df_processed = calculate_derived_features(df)

    # 2. 제거할 컬럼 리스트 생성 (현재 타겟 + 전체 타겟 목록 합치기)
    # 다른 모델의 결과값이 피처로 들어가는 Data Leakage를 원천 차단합니다.
    drop_cols = list(set(config["targets"] + TARGETS))

    # 3. 학습용 피처 풀 구성 (BASE + DERIVED 중 drop_cols 제외)
    all_potential_features = BASE_FEATURES + DERIVED_FEATURES
    final_features = [f for f in all_potential_features if f in df_processed.columns and f not in drop_cols]

    # 4. Mandatory Features(필수 피처) 누락 검증
    for mf in config.get("mandatory_features", []):
        if mf not in final_features:
            raise ValueError(f"필수 피처 '{mf}'가 데이터에 없습니다. 학습/예측을 중단합니다.")

    # 5. 데이터 분리 (학습 시에는 y가 포함되나, 예측 시에는 X만 활용 가능)
    X = df_processed[final_features]

    # 타겟이 데이터프레임에 있을 때만 y 생성 (예측 시 대비)
    y = None
    target_cols = [t for t in config["targets"] if t in df_processed.columns]
    if target_cols:
        y = df_processed[target_cols]

    return X, y

def load_and_preprocess(file_path):
    """CSV 로드 및 결측치 제거"""
    df = pd.read_csv(file_path)

    # 기준 피처 중 NaN이 있는 행 제거 (데이터 무결성 확보)
    existing_features = [f for f in BASE_FEATURES if f in df.columns]
    if existing_features:
        df = df.dropna(subset=existing_features)

    return df
