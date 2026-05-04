# Project Architecture

이 문서는 `predictor_v3` 프로젝트의 주요 기술 구조, 피처 정의, UI 컬럼 매핑 및 아키텍처 패턴을 정리합니다.

## 1. 파일 구조 (File Structure)

프로젝트는 기능별로 엄격히 분리된 구조를 가집니다.

- **`core/`**: 핵심 비즈니스 로직 및 엔진
  - `constants.py`: `COLUMNS`, 경로, 피처 상수 등 모든 설정의 단일 소스 (SSOT)
  - `calculator_*.py`: 규격별 효율 계산 엔진 (ISO16358, AHRI, EN14825)
  - `predictor.py`: 순방향 ML 예측 로직
  - `trainer.py`: 모델 학습 및 로그 관리
- **`ui/`**: PyQt5 기반 GUI 구성 요소
  - `base_model.py`: `QAbstractTableModel`을 상속받은 데이터 모델
  - `predict_window.py`: 예측 UI 및 ODU 캐스케이딩 로직 전담
- **`data/`**: 규격 설정(JSON) 및 학습 데이터
- **`scripts/`**: 데이터 변환 및 전처리 유틸리티

## 2. ML 피처 및 데이터 구조

### 피처 정의 (Feature Definition)
- **BASE_FEATURES (20개)**: 능력(Capa), 치수(Area/Volume), 압축기 사양(EER/cc), 냉매/팽창장치 종류, 전력/주파수 등.
- **DERIVED_FEATURES (8개)**: 능력 대비 효율/면적 비율 등 유도 변수 (0 나누기 방지 적용).

### Data Leakage 주의사항
- CSPF, HSPF 등 계산 결과값은 피처 풀에서 제외합니다.
- 특정 모델(예: 전력) 학습 시 다른 타겟(예: 냉매량)이 입력으로 포함되지 않도록 `core/models.py`에서 타겟별 Leakage 리스트를 엄격히 관리합니다.

### 전처리 전략
- **One-hot Encoding**: 냉매(R410A, R32 등) 및 팽창장치(EEV, Capi)는 `base_model.py`에서 실시간으로 One-hot 변환되어 ML 입력으로 전달됩니다.

## 3. UI 및 데이터 흐름

### UI 컬럼 구조 (COLUMNS)
`core/constants.py`의 `COLUMNS` 정의를 따르며 크게 세 그룹으로 나뉩니다.
1. **INPUT_COLS (0~10)**: 사용자 입력 및 드롭다운 선택 (Capa, IDU, ODU 등).
2. **AUTO_COLS (11~18)**: 선택된 하드웨어 사양에 따른 자동 완성 필드 (Volume, Area, Comp 사양).
3. **RESULT_COLS (19~27)**: ML 예측 결과 및 Rule-based 계산값 (Power, EER, CSPF, HSPF2, Ref Qty, Hz 등).

### 데이터 연동 로직
- **1단계 매핑**: IDU 선택 시 `ID Volume` 자동 완성 등 단순 매핑은 `base_model.py`에서 처리합니다.
- **4단계 캐스케이딩**: ODU → Fin → Pi → Row로 이어지는 복합 선택 및 그에 따른 면적/체적 매핑은 `predict_window.py`에서 전담합니다.

## 4. 로그 시스템
- 학습 결과는 `logs/train_log/YYYYMMDD_HHMM/` 폴더에 `summary.xlsx` 형태로 저장됩니다.
- 로그 유틸리티는 `core/utils.py`에 구현되어 있으며, 경로는 `constants.py`에서 관리합니다.
