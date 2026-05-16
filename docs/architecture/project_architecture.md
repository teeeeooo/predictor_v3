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
- **냉매/팽창장치 One-hot 변환**: UI에서 선택된 냉매 및 팽창장치는 ML 입력 전 `ui/base_model.py`에서 실시간으로 One-hot 피처로 변환됩니다.
  - 관련 키: `R410A`, `R32`, `R290` (냉매), `EEV`, `Capi` (팽창장치)
  - 모델 예측/학습 시 DataFrame 직접 전달을 유지하여 피처 이름을 보존해야 하며, `.values` 변환으로 인해 `feature_names_in_` 속성을 잃지 않도록 주의합니다.

### ML 학습 및 모델 artifact 가드레일
- **기본 artifact 계약**: 현재 기본 모델 artifact는 `core/constants.py`의 `MODEL_FILE`이 가리키는 `model.pkl` 단일 artifact 계약을 따른다. target별 또는 모델별 artifact 분리는 별도 설계 없이 임의로 도입하지 않는다.
- **전처리 호환성 guard**: 학습/예측 전처리 호환성 확인을 위해 `preprocess_version` 또는 동등한 전처리 버전 검증 guard를 유지한다. 이 항목은 architecture contract이며, 현재 구현 완료 범위를 과장하지 않는다.
- **Train/Predict runtime boundary**: `core/trainer.py`는 학습 파이프라인용 모듈이며 예측 런타임 경로와 섞지 않는다. `core/trainer.py`와 `core/predictor.py`는 상호 import로 결합하지 않으며, 예측 경로가 학습 전용 dependency에 의존하지 않도록 유지한다.
- **Target별 학습 독립성**: target별 모델 학습은 독립적인 XGBoost model 및 독립적인 RFE feature set을 유지한다. Cooling/Heating 또는 target별 feature boundary는 `MODEL_REGISTRY.target_rules`와 train/predict feature alignment contract를 따른다.

## 3. UI 및 데이터 흐름

### UI 컬럼 구조 (COLUMNS)
UI 컬럼의 단일 소스(SSOT)는 `core/constants.py`의 `COLUMNS`이며, 크게 세 그룹으로 나뉩니다.
1. **INPUT_COLS (0~10)**: 사용자 입력 및 드롭다운 선택 (Capa, IDU, ODU 등).
2. **AUTO_COLS (11~18)**: 선택된 하드웨어 사양에 따른 자동 완성 필드 (Volume, Area, Comp 사양).
3. **RESULT_COLS (19~27)**: ML 예측 결과 및 Rule-based 계산값 (Power, EER, CSPF, HSPF2, Ref Qty, Hz 등).

### 3.2 COLUMNS 자동완성 구조
- **IDU 단순 매핑**: IDU 선택 시 `ID Volume` 자동 완성 등 단순 1단계 매핑은 `ui/base_model.py`에서 전담합니다.
- **ODU 복합 캐스케이딩**: ODU → Fin → Pi → Row로 이어지는 4단계 복합 캐스케이딩 및 그에 따른 면적/체적 매핑 로직은 단순 매핑과 분리되어 `ui/predict_window.py`가 전담합니다.

### 3.3 UI Model/View Guardrails
- **View Pattern**: `QTableWidget` 사용을 금지하고, 반드시 `QTableView` + `QAbstractTableModel` 구조를 유지한다.
- **Component Injection**: 테이블 셀 내부에 위젯을 직접 삽입하는 `setCellWidget` 사용을 금지한다. 셀 내부 콤보박스나 커스텀 상호작용은 `QStyledItemDelegate`의 `paint` 및 `editorEvent`를 활용하여 구현한다.
- **State Rendering**: 상태별 배경색을 통해 시각적 일관성을 확보한다.
  - 직접 입력 컬럼 (`INPUT_COLS`): 흰색 (`#FFFFFF`)
  - 자동 매핑 컬럼 (`AUTO_COLS`): 회색 (`#F2F2F2`) (단, 사용자가 수동 수정한 경우 흰색으로 전환)
  - 결과 출력 컬럼 (`RESULT_COLS`): 연녹색 (`#E6F3E6`)
- **Event Safety**: 무한 루프(Recursion) 및 신호 복구 누락 방지를 위해, `blockSignals(True/False)` 호출 시 반드시 `try/finally` 블록으로 감싼다.
- **Calculator Boundary**: UI 구현의 편의를 이유로 core calculator의 validation 정책을 약화하거나 우회하지 않는다. Train/Predict UI와 Calculator UI는 프로젝트 헌장(`PROJECT_CHARTER.md`)의 원칙에 따라 철저히 분리된다.

## 4. 로그 시스템
- 학습 로그는 `logs/train_log/YYYYMMDD_HHMM/` 구조로 저장됩니다 (`summary.xlsx` 포함).
- 로그 경로 및 관련 상수는 `core/constants.py`에서 관리하며, 실제 로그 처리 및 폴더 생성 유틸리티는 `core/utils.py`에서 담당합니다.
- 파일 I/O에 의한 부작용(side effect)을 방지하기 위해 `constants.py`에는 순수 상수만 선언하는 원칙을 따릅니다.

## 5. Calculator profile resolver and inverse-search architecture

이 섹션은 calculator routing, region config resolver, 역탐색 연동 작업의 architecture boundary 기준이다.

### Final target flow

장기 목표 흐름은 다음과 같다.

```text
User target
→ Candidate HW generator / inverse search
→ Calculator profile resolver
→ Regional calculator engine
→ Regional metric result
→ Ranking / recommendation
```

사용자가 목표 성능, 목표 CSPF/HSPF/SEER2/HSPF2/SCOP, 대상 지역/규격을 입력하면 역탐색이 후보 HW 조합을 만들고, 계산기는 각 후보를 지역/규격별 계절효율 기준으로 평가한다.

### Calculator role in inverse search

계산기는 ML 모델이나 UI table이 아니라 **지역/규격별 seasonal metric 평가 엔진**이다. 역탐색 단계는 후보 HW 입력을 계산기 입력으로 변환한 뒤 계산기를 호출하고, 계산 결과를 ranking/recommendation 단계에 전달한다.

### Region config vs HW candidate input

`region config`는 규격과 지역에 속한 정적 기준 데이터만 담는다.

- climate/bin hours
- standard constants
- test condition metadata
- degradation defaults
- regional calculation rules
- mode/metric/profile metadata

`HW candidate input`은 역탐색 후보 또는 사용자/ML에서 온 성능 입력값이다.

- capacity at test points
- power at test points
- compressor/fan/control candidate values
- cooling/heating performance points
- 후보 HW 조합의 계산 입력값

production region config에는 candidate 값, golden/sample/test 전용 값, ML prediction 값을 넣지 않는다.

### ML output vs calculator input

ML output은 calculator input이 아니다. 예측된 capacity/power/Hz 등은 `predicted_points → calculator_input` adapter를 거쳐 계산기에 전달한다. ML result를 region config에 섞거나, calculator가 ML feature schema를 직접 읽게 하지 않는다.

### Calculator profile resolver contract

초기 resolver는 nested schema 변환기가 아니라 기존 flat config path를 안전하게 선택하는 manifest/selector 계층이다.

초기 profile record는 최소한 다음 필드를 가진다.

- `profile_id`
- `standard`
- `region`
- `metric`
- `mode`
- `calculator_id`
- `config_path`
- `enabled`

resolver는 explicit selector/manifest/registry contract를 우선한다. filename scanning은 장기적으로 제거 대상이며, ambiguous selector combination은 fail-fast 해야 한다.

### External calculator compatibility profiles

외부 계산기 또는 공식 workbook의 exact-match convention은 common standard calculator path에 직접 섞지 않는다. 해당 convention을 재현해야 할 때는 별도 compatibility calculator/profile을 명시적으로 등록하고, common ISO/AHRI/EN path의 expected/golden과 reference type을 분리한다.

AS/NZS / Energy Rating SEER calculator Excel HSPF exact matching은 ISO16358 common HSPF expected가 아니라 AS/NZS Excel compatibility reference로 분류한다. 후보 profile record는 다음처럼 common ISO profile과 구분한다.

```text
profile_id=asnzs_excel_hspf_compat
standard=ASNZS
region=au_nz
metric=HSPF
mode=heating
calculator_id=asnzs_excel_hspf
config_path=data/region_configs/asnzs_excel_hspf.json
enabled=false
```

`enabled=false`는 구현과 golden guard가 완료되기 전 UI/배포 대상이 아님을 뜻한다. 실제 구현 후보는 `core/calculator_asnzs_hspf_excel.py` 같은 별도 compatibility module이며, `calculator_iso16358.py` common path에 Excel workbook helper cell convention을 추가하지 않는다.

Compatibility profile 선택은 opt-in이어야 한다. `region=au_nz` 또는 `standard=ASNZS` 같은 일반 metadata만으로 compatibility mode를 자동 활성화하지 않으며, common ISO calculator가 `reference_type=ASNZS_EXCEL_COMPAT`를 읽고 내부 분기하는 구조도 금지한다.

ISO16358-2 common HSPF path(Track A)와 AS/NZS Excel compatibility path(Track B)는 별도 calculator/profile/test namespace로 유지한다. Excel COM dump, golden/sample/test-only value는 production region config에 넣지 않고, compatibility reference artifact 또는 test fixture namespace에서만 다룬다.

### UI / calc_window.py routing contract

`calc_window.py`는 장기적으로 config filename을 직접 scan해서 calculator에 전달하지 않는다. UI는 `standard / region / metric / mode / profile_id` selector를 제공하고, resolver가 calculator profile과 config path를 결정한다.

UI 편의를 위해 core calculator validation을 약화하지 않는다. UI는 입력 수집과 표시를 담당하고, calculator selection과 config resolution은 manifest/profile contract를 따른다.

### Result schema boundary

Calculator result schema와 ML feature schema는 분리한다. Calculator result는 metric value, units, summary, bin details, diagnostics 같은 평가 결과를 담고, ML feature schema는 학습/예측 입력 컬럼과 target/leakage rule을 담는다.

필요하면 UI 또는 recommendation layer에서 calculator return dict를 normalized result envelope로 감싸되, core calculator public API와 diagnostics key/value는 별도 phase 없이 변경하지 않는다.

### Forbidden coupling

- region config에 HW candidate input 또는 ML prediction 값을 넣지 않는다.
- calculator engine이 `core/constants.py`의 `COLUMNS`나 `core/models.py`의 `MODEL_REGISTRY`에 직접 의존하지 않는다.
- ML feature/result schema를 calculator result schema로 재사용하지 않는다.
- nested region config를 production calculator에 직접 전달하지 않는다.
- AHRI SEER2/cooling `usa.json`과 AHRI HSPF2/heating `usa_hspf2.json`을 단순 병합하지 않는다.
- local one-off conditional로 selector/routing 문제를 덮지 않는다.
- external calculator compatibility convention을 common ISO calculator path에 직접 섞지 않는다.
- standard/region metadata만으로 external compatibility mode를 자동 선택하지 않는다.
