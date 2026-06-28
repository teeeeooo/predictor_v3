# Project Architecture

이 문서는 `predictor_v3` 프로젝트의 주요 기술 구조, 피처 정의, UI 컬럼 매핑 및 아키텍처 패턴을 정리합니다.

## 1. 파일 구조 (File Structure)

프로젝트는 기능별 분리를 지향하며, Arc 8.5 이후 ML, predictor schema, mapping,
common paths, calculator 구현 owner는 package boundary 아래에 있습니다.
Architecture SSOT update의 source input은
`docs/architecture/project_wide_architecture_restructuring_plan.md`입니다.

- **`core/`**: 핵심 비즈니스 로직 및 엔진
  - `ml/`: 순방향 ML 예측, 학습, 전처리, feature/target, registry, artifact path owner.
  - `predictor_schema/`: `COLUMNS`, dropdown/column grouping, predictor table schema owner.
  - `mapping/`: mapping path/repository/update/autofill owner.
  - `common/`: shared pure helpers and cross-domain paths such as `LOG_DIR`.
  - `calculators/`: profile/dispatcher, calculator adapters, standard engines, result/ranking adapters owner.
- **Project-wide architecture reset note**: root compatibility wrappers were
  retired in Arc 8.5. New active code should import package owner paths directly.
- **Retired legacy `ui/` path**: the former Train/Predict GUI files were
  harvested for UX ideas and retired in Arc 9.1. New Train/Predict production
  code must live under `apps/predict/` and `apps/train/`; visual tokens live in
  `ui_common.visual_tokens`.
- **`apps/` (애플리케이션 패키지 경계)**:
  - 장기적으로 `apps/{calculator,train,predict}/` 구조를 가집니다.
  - **`apps/calculator/`**: 활성 마이그레이션된 계산기 애플리케이션 영역입니다.
    - `app.py`: 계산기 메인 실행 진입점.
    - `ui/`: 마이그레이션이 완료된 calculator-only Tkinter UI 패키지. generic `ui/`로 이름을 섞거나 변경하지 않습니다.
      - **Reusable UI / Common Shell**: `metric_input_table.py`, `result_panel.py` 등 공용 재사용 컴포넌트와 윈도우 쉘 파일들이 위치합니다.
      - **Feature Packages**: `en14825/`, `batch/` 등 특정 계산 규격/피처 전용 패키지로, 피처별 model, adapter, table model, helper 파일들을 캡슐화하여 둡니다.
      - **`sections/`**: 개별 계산 섹션을 조립하는 thin glue 및 registration/routing 성격의 코드로 역할을 제한하며, 피처 전용 model, adapter, table model 파일들을 흩뿌려 두는 dumping ground로 사용하지 않습니다.
  - **`apps/train/` 및 `apps/predict/`**: PySide6 Train/Predict rewrite의 승인된 신규 package boundary입니다. 물리적 폴더 생성은 foundation slice에서 수행되었으며, 새 Train/Predict PySide6 production code는 legacy `ui/`가 아니라 이 경계 아래에 둡니다.
- **`data/`**: 규격 설정(JSON) 및 학습 데이터
- **`scripts/`**: 데이터 변환 및 전처리 유틸리티
- **`tests/`**: 테스트 코드 영역으로, 소스 코드 소유주(source owner) 및 패키지 경계를 그대로 반영한 focused tests 구성을 최우선으로 합니다. (예: `test_apps_calculator_ui_en14825.py`)
- **`tools/`**: standalone 형태의 관리 및 코드 정적 분석/검사 툴만 제한적으로 허용합니다. (예: `check_code_structure.py`)

### 1.1 Project-wide target package boundary

The final target is real package-boundary separation. Arc 8.5 retired the root
compatibility wrapper files after active caller migration.

Long-term target:

```text
core/
  common/
    numeric.py
    units.py
    paths.py
    errors.py

  predictor_schema/
    columns.py
    dropdowns.py
    result_columns.py

  mapping/
    paths.py
    repository.py
    autofill.py
    update.py

  ml/
    artifacts.py
    features.py
    registry.py
    preprocessing.py
    inference.py
    training.py
    logging.py

  calculators/
    profiles.py
    dispatcher.py
    adapters/
      input_adapter.py
      prediction_adapter.py
      unit_adapter.py
    standards/
      iso16358.py
      ks_c9306.py
      en14825.py
      ahri_seer2.py
      ahri_hspf2.py
      asnzs_hspf_excel.py
```

Migration principles:

- Split migration into no-behavior-change slices.
- After package boundary foundation exists, new production code should import
  from approved package owner paths.
- Arc 7 owns ML, predictor schema, and mapping package restructure:
  `core/ml`, `core/predictor_schema`, and `core/mapping`.
- Arc 8 owns the calculator package restructure:
  `core/calculators`, `core/calculators/adapters`, and
  `core/calculators/standards`.
- Calculator engines live under `core/calculators/standards/`.
- ML pipeline ownership lives under `core/ml/`.
- Former `core/constants.py` responsibilities live under predictor schema, ML
  feature/artifact, mapping, and common owners.
- Mapping update pure logic lives under `core/mapping/`; UI/file-dialog
  script wrappers stay outside core.
- Detailed implementation steps belong to `docs/WORK_PLAN.md` and future
  approved migration prompts.

## 2. ML 피처 및 데이터 구조

### 피처 정의 (Feature Definition)
- **BASE_FEATURES (20개)**: 능력(Capa), 치수(Area/Volume), 압축기 사양(EER/cc), 냉매/팽창장치 종류, 전력/주파수 등.
- **DERIVED_FEATURES (8개)**: 능력 대비 효율/면적 비율 등 유도 변수 (0 나누기 방지 적용).

### Data Leakage 주의사항
- CSPF, HSPF 등 계산 결과값은 피처 풀에서 제외합니다.
- 특정 모델(예: 전력) 학습 시 다른 타겟(예: 냉매량)이 입력으로 포함되지 않도록 `core/ml/registry.py`에서 타겟별 Leakage 리스트를 엄격히 관리합니다.

### 전처리 전략
- **냉매/팽창장치 One-hot 변환**: UI에서 선택된 냉매 및 팽창장치는
  PySide6 Predict adapter 경계에서 ML 입력 전 one-hot 피처로 변환됩니다.
  - 관련 키: `R410A`, `R32`, `R290` (냉매), `EEV`, `Capi` (팽창장치)
  - 모델 예측/학습 시 DataFrame 직접 전달을 유지하여 피처 이름을 보존해야 하며, `.values` 변환으로 인해 `feature_names_in_` 속성을 잃지 않도록 주의합니다.

### ML 학습 및 모델 artifact 가드레일
- **기본 artifact 계약**: 현재 기본 모델 artifact는 `core/ml/artifacts.py`의 `MODEL_FILE`이 가리키는 `model.pkl` 단일 artifact 계약을 따른다. target별 또는 모델별 artifact 분리는 별도 설계 없이 임의로 도입하지 않는다.
- **전처리 호환성 guard**: 학습/예측 전처리 호환성 확인을 위해 `preprocess_version` 또는 동등한 전처리 버전 검증 guard를 유지한다. 이 항목은 architecture contract이며, 현재 구현 완료 범위를 과장하지 않는다.
- **Train/Predict runtime boundary**: `core/ml/training.py`는 학습 파이프라인용 모듈이며 예측 런타임 경로와 섞지 않는다. `core/ml/training.py`와 `core/ml/inference.py`는 상호 import로 결합하지 않으며, 예측 경로가 학습 전용 dependency에 의존하지 않도록 유지한다.
- **Train/Predict PySide6 rewrite boundary**: `app_predict.py`는 Predict 전용 thin entrypoint, `app_train.py`는 Predict workspace + Train / Model + Data Mapping을 제공하는 관리자/개발자용 thin entrypoint로 전환한다. `PredictWorkspace`는 `apps.predict`에서 정의하고 `apps.train`의 Predict tab에서 재사용한다. Governing architecture contract는 `docs/architecture/pyside6_train_predict_architecture.md`이며, 설계 결정 기록은 `docs/designs/2026-06-27-pyside6-train-predict-rewrite-design-gate.md`를 따른다.
- **Application-usecase portability boundary**: core package separation alone is
  not sufficient for reusable Train/Predict workflows. Predict execution,
  Train execution, and future Calculator execution corrections need explicit
  UI/runtime-neutral usecase or port boundaries when the same workflow may run
  under PySide6, Tkinter, another GUI toolkit, Web UI, CLI smoke runner, remote
  worker, or automation shell.
- **Target별 학습 독립성**: target별 모델 학습은 독립적인 XGBoost model 및 독립적인 RFE feature set을 유지한다. Cooling/Heating 또는 target별 feature boundary는 `MODEL_REGISTRY.target_rules`와 train/predict feature alignment contract를 따른다.

### MODEL_REGISTRY 확장성 패턴
- **SSOT**: target별 mandatory, excluded, leakage, RFE 사용 여부, result key는 `core/ml/registry.py`의 `MODEL_REGISTRY`를 기준으로 관리한다.
- **확장 규칙**: 새 모델 target 추가 시 trainer, predictor, feature tests에 하드코딩 분기를 반복하지 않고 registry entry를 통해 순회 가능하게 유지한다.
- **단일 artifact**: V2에서 target별 artifact를 분리했다가 버전 불일치 위험이 커졌으므로, 기본 저장 단위는 `model.pkl` 단일 artifact 계약을 유지한다.
- **호환성 주의**: pkl 저장 구조를 단순 dict로 바꾸면 SHAP 등 외부 라이브러리 호환성이 깨질 수 있다. 모델 dict value는 `OptimalModel` 같은 wrapper object로 유지하고, save-data root에 metadata를 추가하는 방향을 우선한다.
- **자동 테스트 방향**: feature/leakage 테스트는 target별 하드코딩보다 `MODEL_REGISTRY`를 순회해 mandatory/leakage/snapshot contract를 확인한다.

## 3. UI 및 데이터 흐름

### UI 컬럼 구조 (COLUMNS)
UI 컬럼의 단일 소스(SSOT)는 `core/predictor_schema/columns.py`의 `COLUMNS`이며, 크게 세 그룹으로 나뉩니다.
1. **INPUT_COLS (0~10)**: 사용자 입력 및 드롭다운 선택 (Capa, IDU, ODU 등).
2. **AUTO_COLS (11~18)**: 선택된 하드웨어 사양에 따른 자동 완성 필드 (Volume, Area, Comp 사양).
3. **RESULT_COLS (19~27)**: ML 예측 결과 및 Rule-based 계산값 (Power, EER, CSPF, HSPF2, Ref Qty, Hz 등).

### 3.2 COLUMNS 자동완성 구조
- **IDU 단순 매핑**: IDU 선택 시 `ID Volume` 자동 완성 등 단순 1단계
  매핑은 `core/mapping/autofill.py`와 PySide6 app-side controller 경계에서
  처리합니다.
- **ODU 복합 캐스케이딩**: ODU → Fin → Pi → Row로 이어지는 복합
  캐스케이딩 및 면적/체적 매핑은 `core/mapping/autofill.py`의 pure logic과
  PySide6 controller/state 경계에서 처리합니다.
- **드롭다운-자동입력 SSOT**: 드롭다운과 자동입력 대상 컬럼 관계는 `DROPDOWN_TARGET` 같은 `Dict[int, list[int]]` 형태로 `core/predictor_schema/columns.py`에서 관리한다.
- **안전한 target lookup**: target column 조회는 직접 인덱싱보다 `.get(col, [])`를 사용해 매핑 없는 열의 `KeyError`를 방지한다.
- **ML feature name mapping**: UI 표시 header와 ML feature name이 다를 수 있으므로 `COLUMNS`에는 `ml_feature` 같은 명시적 mapping key를 둔다. `core/ml/inference.py`에 header 보정 dict를 하드코딩하지 않는다.
- **Cascading autofill 단계**: 계층형 자동완성은 데이터 조회, signal-blocked value write, UI 상태/rendering update의 3단계를 분리한다.
- **단방향 상태 원칙**: AUTO_COLS editable/read-only 상태는 마스터 드롭다운 값, 특히 `직접 입력` 여부를 기준으로만 바꾼다. Delete/paste 같은 다른 경로에서도 먼저 마스터 상태를 확인한다.

### 3.3 UI Model/View Guardrails

> [!NOTE]
> Legacy Train/Predict `ui/` files are retired. Current Train/Predict UI
> implementation follows the PySide6 rewrite architecture contract. Current
> calculator UI follows `apps/calculator/ui/` and the relevant UI/UX adapter
> rules.

- **Spreadsheet behavior owner**: spreadsheet-like UX, copy/paste (TSV),
  multi-cell paste, Delete clear, undo, Tab/Enter navigation, numeric
  validation, paste path isolation, and dropdown/editor lifecycle details are
  owned by `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md` and applicable
  toolkit adapters.
- **View Pattern**: `QTableWidget` 사용을 금지하고, 반드시 `QTableView` + `QAbstractTableModel` 구조를 유지한다.
- **Component Injection**: 테이블 셀 내부에 위젯을 직접 삽입하는 `setCellWidget` 사용을 금지한다. 셀 내부 콤보박스나 커스텀 상호작용은 `QStyledItemDelegate`의 `paint` 및 `editorEvent`를 활용하여 구현한다.
- **State Rendering**: 상태별 배경색을 통해 시각적 일관성을 확보한다.
  - 직접 입력 컬럼 (`INPUT_COLS`): 흰색 (`#FFFFFF`)
  - 자동 매핑 컬럼 (`AUTO_COLS`): 회색 (`#F2F2F2`) (단, 사용자가 수동 수정한 경우 흰색으로 전환)
  - 결과 출력 컬럼 (`RESULT_COLS`): 연녹색 (`#E6F3E6`)
- **Event Safety**: 무한 루프(Recursion) 및 신호 복구 누락 방지를 위해, `blockSignals(True/False)` 호출 시 반드시 `try/finally` 블록으로 감싼다.
- **1-click editor UX**: 드롭다운 editor를 한 번의 클릭으로 열어야 할 때는 `QStyledItemDelegate`의 editor lifecycle 안에서 `QTimer.singleShot(0, editor.showPopup)` 패턴을 사용한다. `time.sleep`으로 UI event timing을 제어하지 않는다.
- **Paste path isolation**: 붙여넣기는 dropdown change event와 다른 경로로 들어오므로 `on_paste_complete()` 같은 별도 처리 흐름에서 값 검증과 자동입력 상태 복구를 수행한다.
- **Handler naming stability**: dropdown 변경 handler 이름을 `_apply_mapping()` / `on_dropdown_changed()`처럼 섞지 않는다. 이벤트 wiring 이름이 바뀌면 AttributeError가 paste/autofill 경로에서 늦게 드러날 수 있다.
- **Deprecated examples**: old widget/delegate examples are historical evidence
  only and must not be copied into current PySide6 production code.
- **Calculator Boundary**: UI 구현의 편의를 이유로 core calculator의 validation 정책을 약화하거나 우회하지 않는다. Train/Predict UI와 Calculator UI는 프로젝트 헌장(`PROJECT_CHARTER.md`)의 원칙에 따라 철저히 분리된다.

## 4. 로그 시스템
- 학습 로그는 `logs/train_log/YYYYMMDD_HHMM/` 구조로 저장됩니다 (`summary.xlsx` 포함).
- 로그 경로 및 관련 상수는 `core/common/paths.py`에서 관리하며, 실제 로그 처리 및 폴더 생성 유틸리티는 `core/utils.py`에서 담당합니다.
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

`data/region_configs/`는 ISO16358 전용 저장소가 아니라, 여러 calculator가 공유할 수 있는 정적 standard/region config 저장소이다. calculator code에 하드코딩하지 않을 정적 standard/region 데이터를 한 곳에 모으는 것이 1차 목적이며, ISO16358 / KS C 9306 / AHRI / EN14825 등 각 calculator가 자기 모듈에서 직접 해당 JSON을 해석한다. 어떤 calculator가 어떤 JSON을 읽는지는 [[calculator-module-boundary-iso-ks-asnzs]] 섹션 boundary를 따른다.

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

2026-05-17 Design Gate에서 `ML output or HW candidate → PredictedPointsEnvelope → CalculatorInputEnvelope → core calculator call → CalculatorResultEnvelope → RankingCandidateEnvelope` 흐름을 확정했다. 상세 data shape와 migration path는 `docs/designs/2026-05-17-calculator-result-envelope-ml-adapter.md`를 따른다.

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

### Calculator module boundary (ISO / KS / ASNZS)

계산기 모듈은 세 축으로 분리한다. resolver는 `calculator_id`를 통해 세 모듈을 명시적으로 구분해야 하며, 한 모듈에 다른 규격의 책임을 합치지 않는다. `data/region_configs/`의 JSON은 어느 한 calculator의 전용 저장소가 아니며, 아래 boundary가 어떤 JSON을 어떤 calculator가 직접 해석하는지를 정한다.

- `core/calculators/standards/iso16358.py` — ISO 16358 전용 계산기.
  - ISO16358-1 CSPF, ISO16358-2 HSPF를 담당한다.
  - Hong Kong / India / SASO / ISO T1 default 등 ISO 16358 기반 regional profile을 region config (`data/region_configs/hong_kong.json`, `india_iseer.json`, `saso.json`, `iso_t1_default_2point.json` 등)로 구현하는 대표 사례이다.
  - resolver에서는 `calculator_id=iso16358`로 식별한다.
- `core/calculators/standards/ks_c9306.py` — KS C 9306 전용 special calculator.
  - KS CSPF, KS HSPF를 담당한다.
  - AHRI / EN14825처럼 ISO common path와 분리된 special calculator로 취급한다.
  - `data/region_configs/korea.json`을 사용할 수 있으나, 해당 config는 ISO common path가 아니라 `KSC9306Calculator`가 직접 해석해야 한다. ISO16358 common path와 KS region config 해석을 섞지 않는다.
  - resolver에서는 `calculator_id=ks_c9306`으로 식별한다.
- `core/calculators/standards/asnzs_hspf_excel.py` — AS/NZS workbook oracle / Excel compatibility 전용.
  - ISO common HSPF/CSPF expected와 분리된 explicit opt-in compatibility calculator이다.
  - AS/NZS workbook oracle convention을 ISO common path에 섞지 않으며, 자체 compatibility config로 opt-in 한다.
  - Current workbook HSPF/CSPF snapshot exact-match는 `ASNZS_EXCEL_COMPAT` fixture namespace에서만 다룬다. Historical case3 full-dump 재현은 별도 Z-phase로 유지한다.
  - resolver에서는 `calculator_id=asnzs_excel_hspf`로 식별한다.

AHRI 등 다른 special calculator도 동일 원칙을 따른다. AHRI calculator는 `data/region_configs/usa.json`(SEER2/cooling)과 `data/region_configs/usa_hspf2.json`(HSPF2/heating)을 사용할 수 있으며, 이 JSON들은 ISO common path가 아니라 AHRI calculator가 해석한다.
EN14825 calculator는 `data/region_configs/en14825.json`을 사용할 수 있으며, resolver에서는 `calculator_id=en14825`로 식별한다.

resolver는 `calculator_id` 값으로 모듈을 명시적으로 라우팅하고, `region` 또는 `standard` metadata만으로 KS C 9306 또는 AS/NZS Excel compatibility를 자동 활성화하지 않는다.

#### Calculator series reset direction (2026-05-17 결정)

위 boundary는 목표 구조이며, 2026-05-17 series reset 작업에서 기존 ISO 구현은 legacy/reference로 격하되고 새 파일들이 이 책임 경계에 맞춰 재작성되고 있다.

- 기존 혼재 구현은 `core/_legacy/calculator_iso16358_legacy.py`로 격하했다.
- `core/calculators/standards/iso16358.py`는 ISO 16358 CSPF/HSPF common standard logic만 담당한다. KS / ASNZS / workbook oracle 책임은 포함하지 않는다.
- `core/calculators/standards/ks_c9306.py`는 KS C 9306 전용 special calculator로 유지하며, `data/region_configs/korea.json`을 직접 해석한다. ISO calculator가 KS config를 대신 해석하지 않는다.
- `core/calculators/standards/asnzs_hspf_excel.py`는 AS/NZS workbook oracle compatibility 전용 calculator로 유지한다. Current workbook HSPF/CSPF snapshot exact-match는 이 경로에서만 검증하고, historical case3 full-dump parity는 Z-phase로 유지한다.
- `data/region_configs/`는 ISO 전용이 아닌 다중 calculator 공유 정적 standard/region config 저장소이며, 각 JSON은 boundary에서 정한 calculator가 직접 해석한다.
- tests 정책: legacy implementation behavior를 고정하는 테스트는 그대로 유지하지 않는다. 필요한 regression만 새 calculator 기준으로 이전하고, diagnostic/workbook-mixed 테스트는 삭제 또는 legacy/archive로 격리한다. (자세한 실행 순서는 `docs/WORK_PLAN.md`와 `docs/REFACTOR_PLAN.md` 참조.)
- profile / dispatcher / UI 연결은 새 calculator series boundary를 유지한 상태에서만 확장한다.

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

`enabled=false`는 구현과 golden guard가 완료되기 전 UI/배포 대상이 아님을 뜻한다. 실제 구현 후보는 `core/calculators/standards/asnzs_hspf_excel.py` 같은 별도 compatibility module이며, ISO common path에 Excel workbook helper cell convention을 추가하지 않는다.

Compatibility profile 선택은 opt-in이어야 한다. `region=au_nz` 또는 `standard=ASNZS` 같은 일반 metadata만으로 compatibility mode를 자동 활성화하지 않으며, common ISO calculator가 `reference_type=ASNZS_EXCEL_COMPAT`를 읽고 내부 분기하는 구조도 금지한다.

ISO16358-2 common HSPF path(Track A)와 AS/NZS Excel compatibility path(Track B)는 별도 calculator/profile/test namespace로 유지한다. Excel COM dump, golden/sample/test-only value는 production region config에 넣지 않고, compatibility reference artifact 또는 test fixture namespace에서만 다룬다.

### PyQt Legacy Calculator Reference (Retired)

> [!NOTE]
> The retired legacy `ui/` folder is no longer an active implementation path.
> Current calculator UI is `apps/calculator/ui/`. `app_calculator.py` is the
> `apps.calculator.app:main` wrapper.

이 섹션은 PyQt calculator-only source retirement(Report 353) 이전의 routing contract와 module boundary 설계 결정을 historical record로 보존합니다. 아래 내용은 더 이상 current implementation 설명이 아닙니다.

**Retired routing contract summary (historical)**:
- `calc_window.py`는 `standard / region / metric / mode / profile_id` selector와 resolver 기반 calculator construction(`create_calculator_for_profile()`) 경로를 설계 기준으로 했습니다.
- `ui/calculators_2point.py::IsoCspfSingleWidget`이 ISO tab UI owner였습니다.
- `ui/calculator_errors.py`는 validation error styling/message routing을 담당했습니다.

**Current state**:
- Current calculator UI: `apps/calculator/ui/`
- Current Train/Predict UI: `apps/predict/`, `apps/train/`
- Current toolkit-neutral visual tokens: `ui_common/visual_tokens.py`


### Result schema boundary

Calculator result schema와 ML feature schema는 분리한다. Calculator result는 metric value, units, summary, bin details, diagnostics 같은 평가 결과를 담고, ML feature schema는 학습/예측 입력 컬럼과 target/leakage rule을 담는다.

필요하면 UI 또는 recommendation layer에서 calculator return dict를 normalized result envelope로 감싸되, core calculator public API와 diagnostics key/value는 별도 phase 없이 변경하지 않는다.

Normalized envelope는 adapter/recommendation boundary의 계약이며, core calculator가 UI table schema 또는 `MODEL_REGISTRY`를 읽는 구조로 확장하지 않는다. 기존 calculator return dict는 envelope의 `raw_result` 아래에 보존한다.

### Forbidden coupling

- region config에 HW candidate input 또는 ML prediction 값을 넣지 않는다.
- calculator engine이 `core/predictor_schema/columns.py`의 `COLUMNS`나 `core/ml/registry.py`의 `MODEL_REGISTRY`에 직접 의존하지 않는다.
- ML feature/result schema를 calculator result schema로 재사용하지 않는다.
- nested region config를 production calculator에 직접 전달하지 않는다.
- AHRI SEER2/cooling `usa.json`과 AHRI HSPF2/heating `usa_hspf2.json`을 단순 병합하지 않는다.
- local one-off conditional로 selector/routing 문제를 덮지 않는다.
- external calculator compatibility convention을 common ISO calculator path에 직접 섞지 않는다.
- standard/region metadata만으로 external compatibility mode를 자동 선택하지 않는다.

## 6. New module / script boundary

본 섹션은 UI에 한정하지 않고, `core/`, `ui/`, `apps/calculator/ui/`, `scripts/`, `tools/`, ML adapter, packaging probe 등 새 module / script / feature를 추가할 때 공통으로 적용되는 boundary 원칙이다. 전체 규칙은 `AGENTS.md` New Code Quality Gate가 owner이며, 본 섹션은 아키텍처 관점의 요약이다.

- Layer import 방향: `core/` → UI / CLI / Tkinter / PyQt / script 어느 layer도 import하지 않는다. UI / CLI / script는 `core` public 진입점 (`core.calculators.dispatcher.create_calculator_for_profile`, adapter, resolver 등) 으로만 core를 호출한다. `core/` 안에서 `ui`, `apps.calculator.ui`, `legacy Qt binding`, `tkinter`를 import하지 않는다.
- Tkinter shell 독립성: `apps/calculator/ui/`는 retired legacy `ui` package를
  import하지 않는다. Calculator and Train/Predict remain separate deployment
  surfaces over shared core owners.
- Thin entrypoint: `app_*.py` 는 import + 한 두 줄 entrypoint 함수만 둔다 (class 정의 금지, module-level 함수 3개 이하, 80 LOC 이하). 실제 책임은 layer 모듈에 둔다.
- Multi-responsibility 한 파일 금지: shell / orchestration / business logic / data transform / formatting / I/O를 한 파일에 섞지 않는다. 새 작업에서 3개 이상 신규 책임 영역이 발생하면 skeleton/interface 작업과 구현 작업을 분리한다.
- Hard-coded 값 격리: region, profile, metric, result key, default 값은 SSOT (config, constants, resolver, token module) 한 곳에서만 정의한다. 2곳 이상 반복되는 literal/mapping/formatting은 helper/registry 후보로 본다.
- Soft limit (warning): 새 파일은 250 LOC / class 3개 / 함수 60~80 LOC 이내가 기본. 초과 예상 시 분리 계획을 먼저 보고한다. 기존 known-large / historical 파일은 `tools/check_code_structure.py`의 allowlist로 일시 면제한다.
- Spike 예외 없음: feasibility spike도 shell + input + result + resolver + core call + formatting을 한 파일에 동시에 담지 않는다 (116 spike → 118 reset 사례 참고).

자동 검사는 `tools/check_code_structure.py`가 conservative한 첫 버전으로 제공한다 (layer import 금지, app entrypoint thin, apps/calculator/ui multi-책임 anti-pattern, LOC / class soft limit). 코드 구조에 영향을 주는 작업의 검증에 포함한다.
