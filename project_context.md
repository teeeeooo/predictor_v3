# predictor_v3 프로젝트 컨텍스트
# 새 대화 시작 시 반드시 이 파일을 첨부할 것

## 프로젝트 개요
벽걸이형 1:1 에어컨(Air-to-Air) HVAC 시스템의
성능/효율 ML 예측 및 HW 조합 역탐색 프로그램.
코딩 비전문가 엔지니어가 VSCode + Cline / Claude Code로 개발 중.

## 개발 환경
- 언어: Python
- ML: XGBoost
- GUI: PyQt5
- 패키징: PyInstaller
- 데이터: pandas, numpy
- 최적화: Optuna
- 학습 데이터: Practice_4.csv (약 349행)

## 버전 히스토리
- V1: Tkinter + RandomForest (종료)
- V2: PyQt5 + XGBoost (완료, HVAC_V2_Archive 보관)
- V3: 현재 진행 중

## predictor_v3 최종 목표
1. 순방향: HW 사양 입력 → 소비전력/효율 예측
2. 역방향: 목표 성능/효율 입력 → HW 조합 추천
3. 규격 계산: ISO16358-1, SEER 등 rule-based
4. 열교환기 치수 계산: 핀피치/두께 입력 → 전열면적/내용적

## 개발 로드맵
1. models.py 구조 개선 (타겟별 leakage 분리) ← 완료
2. 재학습 및 예측 검증 ← 진행 중 (별도 창)
3. 테스트 하네스 구축 (tests/ 폴더)
4. train_window 예측 검증 기능 추가
5. core/calculator 효율 계산기 구현 ← Phase 1 scope 정리 및 UI 연결 예정
   Phase 1: 검증 완료 profile 중심 Calculator UI v1 배포 범위
     5-1. [완료] Korea KS C 9306 CSPF/HSPF
          CSPF golden sample 검증 완료 (CSPF 6.504 일치)
          HSPF profile / validation / golden / smoke 완료
     5-2. [완료] ISO 16358-1 T1 default 2-point CSPF production config
     5-3. [완료] India ISEER xlsx-compatible path
     5-4. [완료] Hong Kong custom bin 2-point config
          source golden mismatch는 Phase 2에서 cspf_profile schema 이후 재검토
     5-5. [완료] EN 14825 SEER/SCOP
     5-6. [완료] AHRI 210/240 SEER2/HSPF2 full variable-capacity path
          (상세: docs/skills/ahri_hspf2.md 참조)
          golden case 검증 완료 (5개 케이스, AHRI 공식 계산기 대비 diff < 0.001)
Phase 2: ISO16358 official sheet structure expansion
  5-7. [완료] ISO16358 cspf_test_profile Phase R1/R2
       - 완료: variable/inverter-only profile resolver
       - 완료: T1 required_only / with_optional_test smoke/sanity
       - 완료: T3 required_only / with_optional_test resolver/smoke
       - 완료: legacy ISO T1 default path parity 확인
       - 완료: SASO T3 official xlsm golden regression
       - 전체 pytest: 97 passed, 1 xfailed
       - 범위: variable/inverter-only profile path. fixed/two-stage/multi-stage는 scope 밖
  5-8. [완료] SASO T3 Phase R2
  5-9. ISO16358 official sheet full optional matrix 단계적 구현
   대상: Non-ducted, Air-to-Air, Variable capacity 1:1

   Phase 3: 예측기 연동
     5-10. predictor.py 예측 결과를 계산기 입력으로 변환
     5-11. ML 예측값 기반 CSPF/SEER/HSPF 자동 산출
     5-12. app_predict.py 결과 컬럼 확장

6. 1차 배포 (PyInstaller 패키징)
7. 역방향 탐색 설계 (core/optimizer.py)
8. 열교환기 면적/내용적 계산 (core/physics.py)
- [ ] 유산용 docs 및 전체 폴더 구조 리팩토링 (docs/REFACTOR_PLAN.md 참조)

## 아키텍처 핵심 결정사항 (절대 원칙)

### UI
- QTableWidget 금지
- QTableView + QAbstractTableModel 구조만 허용
- 입력/자동/결과 컬럼이 단일 QTableView에 통합
- COLUMNS (core/constants.py) 단일 소스 원칙
- COLUMNS 키 구조:
  공통: key, header, width, group, bg_color
  조건부: type, mapping, source, mapping_key, ml_feature, readonly

### ML
- model.fit()에 .values 변환 금지
  (DataFrame 직접 전달 → feature_names_in_ 보존)
- MODEL_REGISTRY (core/models.py) 단일 소스
- model.pkl 단일 파일 통합 저장 구조:
  {"models": {타겟명: xgb객체},
   "features": {타겟명: [피처목록]},
   "preprocess_version": "v1.0"}
- Lite 안전장치 v1.0 적용 (preprocess_version 체크)
- models.py 타겟별 leakage 분리 구조 적용 확인 필요 (1차완료)
  (모델 단위 공유 → 타겟 단위 분리로 변경)

### 아키텍처
- app_train.py: 학습 + 예측 검증 (마스터)
- app_predict.py: 예측 전용 (배포용)
- predictor.py에 학습용 라이브러리 금지
  (optuna, sklearn, shap, matplotlib)
- blockSignals 사용 시 반드시 try/finally
- scripts/ 폴더: 독립 실행 도구 모음 (공식 디렉토리)

### 계산기 아키텍처
- 최종 목표: ML 예측값 → 효율 계산기 → CSPF/SEER 등 자동 산출
- 파이프라인: predictor.py → calculator_iso16358.py → 결과 표시
- 독립 배포: app_calculator.py로 계산기만 별도 패키징 가능
- Phase 1 배포 원칙: 검증 완료 profile만 UI에 노출한다. SASO T3는 official golden regression 완료 상태이나 UI 노출 여부는 Calculator UI v1 연결 단계에서 별도 검토한다.
- 엔진 구조:
  calculator_iso16358.py     — ISO 16358 공통 CSPF/HSPF 엔진 + region 확장 (한국 KS C 9306, ISO T1 default, India, Hong Kong 등)
  calculator_en14825.py      — EN 14825 (유럽: EU SEER/SCOP)
  calculator_ahri_seer2.py   — AHRI 210/240 SEER2
  calculator_ahri_hspf2.py   — AHRI 210/240 HSPF2
- 지역별 설정은 data/region_configs/*.json 또는 data/usa*.json으로 분리 (data-driven)
- calculator 계열 파일 제약: numpy/pandas 금지, 순수 파이썬만
- ISO16358 문서 구조:
  docs/iso16358/iso16358_notes.md — ISO16358 공통 계산 구조
  docs/iso16358/iso16358_dev_notes.md — ISO16358 공통 구현 지침
  docs/iso16358/iso16358_design_notes.md — ISO16358 공통 설계 인사이트
  docs/iso16358/iso16358_glossary.md — ISO16358 공통 용어 SSOT
- KS C 9306 문서 구조:
  docs/iso16358/regions/ks_c_9306/ks_c_9306_notes.md — 한국 region 계산 기준
  docs/iso16358/regions/ks_c_9306/ks_c_9306_dev_notes.md — 한국 region 구현 지침
  docs/iso16358/regions/ks_c_9306/ks_c_9306_design_notes.md — 한국 region 설계 heuristic
  docs/iso16358/regions/ks_c_9306/ks_c_9306_glossary.md — 한국 region 용어 SSOT
- ISO16358 CSPF는 기존 flat config path를 유지하면서, `cspf_test_profile` opt-in path를 병렬로 운영한다.
- 현재 `cspf_test_profile`은 variable/inverter-only 대상이며, fixed/two-stage/multi-stage는 프로젝트 scope 밖이다.
- SASO T3 official golden 경로는 `climate_profile=T3`, `test_selection=with_optional_test`, `t_100_load=46.0`, `t_0_load=20.0`, `reference_point="46_full"`, `Cd=0.27`, `power_interpolation_method="iso_boundary_eer"`이다.
- T3 boundary EER는 `_iso_boundary_eer_t3_piecewise()` helper가 T3 `cspf_test_profile` guard 안에서만 처리한다.

### HSPF2 구현 현황 (calculator_ahri_hspf2.py)
- 적용 규격: AHRI 210/240-2026
- 대상: non-ducted, single-split, variable-capacity, air-to-air heat pump
- 우선 지역: Region IV
- 상태: full variable-capacity path 구현 완료, golden case 검증 완료
- 상세 구현 내용: docs/skills/ahri_hspf2.md 참조
- v2 legacy path 보존 (calculate_hspf2_v2 수정 금지)
- 데이터: data/usa_hspf2.json (Region IV bin table)

### bin_details 표준 구조 (디버그/검증용)

- temp_F
- hours
- building_load
- q_full
- q_low
- q_j
- q_comp
- q_aux
- E_j
- e_comp
- e_aux
- operating_case
- C_D

검증:
- q_j = q_comp + q_aux
- E_j = e_comp + e_aux
- q_j = building_load × hours

### COLUMNS 자동완성 구조
- 단순 1단계 매핑: base_model.py의 on_dropdown_changed() 처리
  (idu→id_volume, evap_index→evap_area 등)
- ODU 4단계 캐스케이딩: predict_window.py 전담
  (ODU → fin_type → pi → row → cond_area/cond_volume)
- mapping.json 투 트랙 구조:
  "odu_cascade": 드롭다운 목록용
  "cond_specs": 조합키(ODU+Fin+Pi+Row) → 사양 매핑용

### 냉매/팽창장치 One-hot 변환
- mapping.json에 정의하지 않고 코드에서 처리
- base_model.py get_row_as_ml_dict()에서 변환
  ref_type: {"R410A":0, "R32":0, "R290":0} 중 선택값만 1
  exp_type: {"EEV":0, "Capi":0} 중 선택값만 1

### 로그 시스템
- logs/ 폴더 자동 생성
  train_log/YYMMDD_HHMM/summary.xlsx — 학습 결과
  error_log/ — 런타임 에러 (미구현)
  crash_log/ — 강제 종료 (미구현)
- LOG_DIR: constants.py에 정의
- get_timestamp_dir(), save_train_log_to_excel(): utils.py에 구현

## 파일 구조
predictor_v3/
├── app_train.py               학습+검증 마스터 UI
├── app_predict.py             예측 전용 배포 UI
├── app_calculator.py          효율 계산기 독립 실행 진입점
├── AGENTS.md                  Claude Code / Cline 공통 에이전트 규칙
├── core/
│   ├── constants.py           COLUMNS, 경로, 피처 상수 (SSOT)
│   ├── models.py              MODEL_REGISTRY
│   ├── data_pipeline.py       전처리 전용
│   ├── trainer.py             학습 로직 (log_callback, 엑셀 로그 지원)
│   ├── predictor.py           순방향 예측 (학습 라이브러리 금지)
│   ├── calculator_iso16358.py ISO 16358 CSPF/HSPF 엔진 (CSPF 1차 수정 완료)
│   ├── calculator_en14825.py  EN 14825 SEER/SCOP 엔진
│   ├── calculator_ahri_seer2.py  AHRI 210/240 SEER2 엔진
│   ├── calculator_ahri_hspf2.py  AHRI 210/240 HSPF2 엔진
│   ├── optimizer.py           역탐색 추천 (미구현)
│   ├── constraints.py         열역학 물리 제약 (미구현)
│   ├── physics.py             열교환기 치수 계산 (미구현)
│   └── utils.py               공통 유틸 + load_mapping_data() + 로그 유틸
├── ui/
│   ├── base_model.py          HVACTableModel (QAbstractTableModel)
│   ├── base_view.py           HVACTableView + DropdownDelegate
│   ├── predict_window.py      예측 윈도우 + ODU 캐스케이딩
│   ├── train_window.py        학습 윈도우 + QThread 워커
│   └── calc_window.py         효율 계산기 GUI
├── scripts/
│   └── update_mapping.py      Excel/CSV→JSON 변환 도구
├── model/
│   └── model.pkl              통합 모델 파일
├── data/
│   ├── Practice_4.csv         학습 데이터
│   ├── mapping.json           HW 매핑 데이터
│   ├── usa.json               AHRI SEER2 bin table (냉방)
│   ├── usa_hspf2.json         AHRI HSPF2 bin table, Region IV (난방)
│   └── region_configs/        지역별 효율 규격 설정
│       ├── iso_t1_default_2point.json  ISO 16358-1 T1 default 2-point CSPF
│       ├── korea.json                  KS C 9306 CSPF/HSPF
│       ├── india_iseer.json            India ISEER xlsx-compatible
│       ├── hong_kong.json              Hong Kong custom bin 2-point CSPF
│       ├── saso.json                   SASO T3 official xlsm golden regression
│       ├── eu.json                     EN 14825 SEER
│       ├── en14825_scop.json           EN 14825 SCOP
│       └── usa.json                    AHRI SEER2 region config
├── logs/
│   ├── train_log/             학습 결과 엑셀 로그
│   ├── error_log/             런타임 에러 로그 (미구현)
│   └── crash_log/             강제 종료 로그 (미구현)
├── tests/
│   ├── test_hspf2_smoke.py          HSPF2 v2 smoke test
│   ├── test_hspf2_v3_smoke.py       HSPF2 v3 smoke test (PLF 전후 비교 포함)
│   └── test_hspf2_v3_bincheck.py    bin-level sanity check
├── docs/
│   ├── DOCS_GUIDELINES.md
│   ├── STANDARD_DOC_TEMPLATE.md
│   ├── iso16358/
│   │   ├── iso16358_notes.md
│   │   ├── iso16358_dev_notes.md
│   │   ├── iso16358_design_notes.md
│   │   ├── iso16358_glossary.md
│   │   └── regions/
│   │       └── ks_c_9306/
│   │           ├── ks_c_9306_notes.md
│   │           ├── ks_c_9306_dev_notes.md
│   │           ├── ks_c_9306_design_notes.md
│   │           └── ks_c_9306_glossary.md
│   └── skills/
│       └── ahri_hspf2.md
├── .clinerules
├── BUILD_GUIDE.md
└── project_context.md    ← 이 파일

## 피처 정의

### BASE_FEATURES (20개)
Cooling Capa, Heating Capa,
ID Volume, Evap Area, Evap Volume,
OD Volume, Cond Area, Cond Volume,
Comp EER, Comp cc,
R410A, R32, R290, EEV, Capi,
Ref Qty,
Cooling Power, Heating Power,
Cooling Hz, Heating Hz

### DERIVED_FEATURES (8개)
Cool_Capa_per_EER, Cool_Capa_per_CondArea,
Cool_Capa_per_EvapArea, Cool_Capa_per_cc,
Heat_Capa_per_EER, Heat_Capa_per_CondArea,
Heat_Capa_per_EvapArea, Heat_Capa_per_cc
계산: np.where 벡터 연산 (0 나누기 방지)

### 모델별 피처 설정 (확인 필요)

#### 현재 구조 문제점
- leakage가 모델 단위로 공유되어 타겟별 교차 능력값 제외 불가
- Heating Power 학습 시 Cooling Capa가 상위 피처로 노출되는 문제 발견
- Ref Qty 학습 시 고정 피처 외 다른 피처가 포함되는 문제 발견

#### 변경 후 목표 구조 (타겟별 leakage 분리)

| 모델 | 타겟 | 방식 | Mandatory | Leakage |
|---|---|---|---|---|
| model_power | Cooling Power | RFE | R410A,R32,R290 | Heating Power, Cooling Hz, Heating Hz, Ref Qty, Heating Capa |
| model_power | Heating Power | RFE | R410A,R32,R290 | Cooling Power, Cooling Hz, Heating Hz, Ref Qty, Cooling Capa |
| model_ref_qty | Ref Qty | 고정 | OD Volume, ID Volume, Evap Volume, Cond Volume, R410A,R32,R290 | Cooling Power, Heating Power, Cooling Hz, Heating Hz |
| model_hz | Cooling Hz | RFE | R410A,R32,R290, Cooling Load, Heating Load, EEV, Capi | Heating Hz, Cooling Power, Heating Power, Ref Qty |
| model_hz | Heating Hz | RFE | R410A,R32,R290, Cooling Load, Heating Load, EEV, Capi | Cooling Hz, Cooling Power, Heating Power, Ref Qty |

#### 변경 시 영향 파일
- core/models.py — 타겟별 leakage 구조로 변경
- core/data_pipeline.py — prepare_pipeline() 타겟별 leakage 처리
- core/trainer.py — 타겟별 leakage 조회 로직 수정

### Data Leakage 주의사항
- CSPF, HSPF: Rule-based 계산값, 피처 풀에 없음
- Ref Qty: 모델2 타겟이므로 모델1,3 학습 시 누수 주의
- 교차 능력값: Cooling Power 학습 시 Heating Capa 제외,
  Heating Power 학습 시 Cooling Capa 제외

## UI 컬럼 구조 (COLUMNS)

### INPUT_COLS (0~10, 11개)
| index | key | 설명 | type |
|---|---|---|---|
| 0 | cooling_capa | 냉방 능력 | text |
| 1 | heating_capa | 난방 능력 | text |
| 2 | idu | 실내기 | dropdown |
| 3 | evap_index | 증발기 종류 | dropdown |
| 4 | odu | 실외기 | dropdown |
| 5 | fin_type | FIN 종류 | dropdown (ODU 연동) |
| 6 | pi | PI | dropdown (ODU 연동) |
| 7 | row | ROW | dropdown (ODU 연동) |
| 8 | compressor | 압축기 | dropdown |
| 9 | ref_type | 냉매 종류 | dropdown |
| 10 | exp_type | 팽창장치 | dropdown |

### AUTO_COLS (11~18, 8개)
| index | key | ml_feature | source | mapping_key |
|---|---|---|---|---|
| 11 | id_volume | ID Volume | idu | ID Volume |
| 12 | evap_area | Evap Area | evap_index | Evap Area |
| 13 | evap_volume | Evap Volume | evap_index | Evap Volume |
| 14 | od_volume | OD Volume | odu | OD Volume |
| 15 | cond_area | Cond Area | odu* | Cond Area |
| 16 | cond_volume | Cond Volume | odu* | Cond Volume |
| 17 | comp_eer | Comp EER | compressor | Comp EER |
| 18 | comp_cc | Comp cc | compressor | Comp cc |
* cond_area/cond_volume은 predict_window.py에서 ODU+Fin+Pi+Row 조합으로 처리

### RESULT_COLS (19~25, 7개)
| index | key | 설명 |
|---|---|---|
| 19 | cooling_power | 냉방 소비전력 |
| 20 | eer | EER (rule-based) |
| 21 | heating_power | 난방 소비전력 |
| 22 | cop | COP (rule-based) |
| 23 | ref_qty | 냉매량 |
| 24 | cooling_hz | 냉방 운전주파수 |
| 25 | heating_hz | 난방 운전주파수 |

## V2 주요 시행착오 요약
- .values 변환으로 feature_names_in_ 소실 경험
- header vs ml_feature 불일치로 KeyError 발생
- blockSignals 없이 자동완성 시 이벤트 무한루프
- _apply_mapping vs on_dropdown_changed 혼용
- pkl 분리 저장 → 버전 불일치 위험 → 통합으로 전환
- QTableWidget 이벤트 꼬임 → V3에서 QTableView 전환
- constants.py에 파일 I/O 넣으면 import 시 부작용 발생
  → load_mapping_data()는 utils.py에 배치
- DataFrame 인덱스 중복 시 to_dict('index') 에러
  → dropna + drop_duplicates 안전장치 적용
- leakage를 모델 단위로 공유하면 타겟별 교차 능력값 제외 불가
  → 타겟별 leakage 분리 구조로 변경 예정
- constants.py의 EXCLUDED_FEATURES와 models.py target_rules 중복 → EXCLUDED_FEATURES 삭제
- models.py exclude 피처명과 data_pipeline.py 실제 생성명 불일치 → 피처명 통일
- BASE_FEATURES에 Load(%) 변수 포함 시 단위 불일치 문제 → 제거

## 현재 진행 상태

### ML / 예측
- [x] core/ 레이어 전체 완성
- [x] ui/ 레이어 전체 완성
- [x] app_train.py / app_predict.py 진입점 완성
- [x] models.py 타겟별 leakage 분리 구조 변경
- [ ] 재학습 및 예측 검증

### 계산기 — 냉방
- [x] ISO 16358-1 / KS C 9306 CSPF 계산기 완료
  - 한국 경로 시험값 정수 반올림 적용 (ROUND_HALF_UP)
  - KS 교점 방식 전력 보간 분리 적용
  - 29°C 미만/35°C 초과 외삽 및 max capacity 초과 구간 처리 수정
  - golden sample 검증 완료 (CSPF 6.504 일치)
- [x] ISO T1 default 2-point CSPF production config 완료
  - `iso_t1_default_2point.json` 기준 regression 유지
- [x] India ISEER xlsx-compatible path 완료
  - boundary temperature rounding opt-in 적용
  - xlsx-compatible regression 유지
- [x] Hong Kong custom bin 2-point config 완료
  - current-engine regression 유지
  - source golden mismatch는 Phase 2 보류
- [x] SASO T3 official xlsm golden regression 완료
  - `cspf_test_profile`: `climate_profile=T3`, `test_selection=with_optional_test`
  - load line: `t_100_load=46.0`, `t_0_load=20.0`, `reference_point="46_full"`, `Cd=0.27`
  - power model: `power_interpolation_method="iso_boundary_eer"`
  - T3 helper: `_iso_boundary_eer_t3_piecewise()`
  - T3 29_full default point 동작 확인/유지: capacity `1.077 × 35_full`, power `0.914 × 35_full`
  - golden result: CSTL ≈ 21,547.386 kWh, CSEC ≈ 4,349.020 kWh, CSPF ≈ 4.955 W/W
  - official target: CSTL ≈ 21,546 kWh, CSEC ≈ 4,349 kWh, CSPF ≈ 4.954 W/W
  - 전체 pytest: 97 passed, 1 xfailed
- [x] ISO16358 / KS C 9306 문서 구조 정규화
  - ISO 공통 문서: docs/iso16358/
  - KS region 문서: docs/iso16358/regions/ks_c_9306/
- [x] KS C 9306 Cd 원본 확인 (성적서 대조 필요)
- [x] 35_half 목표 성능 계산 helper 구현
- [ ] 35_half 목표 성능 계산 UI 연동
- [ ] Cd UI 입력 기능 추가
- [x] EN 14825 SEER 엔진 구현 (calculator_en14825.py)
- [x] EN 14825 SCOP 엔진 구현
- [x] EN 14825 SEER GUI 탭 연동 (calc_window.py)
- [x] data/region_configs/eu.json 생성
- [x] AHRI 210/240 SEER2 엔진 구현 (calculator_ahri_seer2.py)
- [x] AHRI 210/240 SEER2 GUI 연동
- [x] calc_window.py 다중 탭 구조 구성

### 계산기 — 난방 HSPF2
- [x] AHRI 210/240 HSPF2 simplified canonical path 구현
  - canonical schema (H12/H32/H42), H42 외삽
  - BL 공식 규격화 (Eq. 11.104, C_vs/t_zl/t_OD)
  - fractional bin hours × HLH 적용
  - PLF = 1 - Cd × (1 - PLR) cycling 보정
  - bin-level sanity check 및 bincheck 스크립트
  - v2 legacy path 보존
  - AGENTS.md 생성
- [x] HSPF2 full variable-capacity path 구현 완료
      golden case 검증 완료 (5개 케이스)
      상세: docs/skills/ahri_hspf2.md
- [x] ISO 16358-2 HSPF KS C 9306 profile / validation / golden / smoke 완료
  - [x] KS C 9306 HSPF golden/validation smoke 통과
  - [x] Korea HSPF 31-bin 적용
- [ ] 한국 외 ISO 16358-2 HSPF production 확장 확인 필요
- [ ] ISO 16358-2 HSPF load line capacity source 지역별 확인
  - Korea / KS C 9306: 공식 계산 시트 기준 `rated_heating_capacity × 0.82`로 임시 확정
  - Spec text에는 `BLc(35) × 0.82` cooling reference가 있어 주석 유지 필요
  - Australia / New Zealand AS/NZS 3823.4.2는 원문 확인 전 임의 구현 금지

### 공통
- [ ] predictor → calculator 파이프라인 연동
- [ ] 테스트 하네스 구축

## 다음 작업
1. docs/REFACTOR_PLAN.md 기준 계산기 Phase 1 scope 정리
2. app_calculator.py / calc_window.py Calculator UI v1 연결
3. predictor → calculator pipeline 연결
4. 역방향 예측 MVP 설계
5. Hong Kong source golden CSPF 4.83 formula review pending xfail 검토 (후순위)
6. ISO16358 official sheet full optional matrix 단계적 구현 검토
7. AHRI 설정 파일 위치 재정리 검토
   - `data/usa_hspf2.json`은 AHRI HSPF2 bin table, test point schema, alias를 함께 담고 있어 `data/region_configs/`로 단순 이동하기 전 구조 검토 필요
   - 후보: `data/ahri/usa_hspf2.json` 또는 AHRI 전용 config 디렉터리



## 2026-05-04 — Calculator UI 2점식 ISO/ISEER 1차 구현 및 다음 작업 메모
## 임시 작성이므로 Calculator UI 1차 구현 완료시 삭제할것

### 오늘 완료된 작업

- `core/calculator_iso16358.py`
  - `calculate_cspf()` 및 관련 CSPF profile 경로 반환값에 `bin_details` 추가.
  - 기존 핵심 반환값인 `cspf`, `annual_cooling_kwh`, `annual_power_kwh` 계산 로직은 유지.
  - `bin_details`는 UI 상세보기의 Trace Table / graph 표시용 데이터로 사용 예정.

- `ui/calculators_2point.py`
  - 2점식 ISO/ISEER batch 계산 UI 신규 파일로 분리 구현.
  - `QTableView + QAbstractTableModel` 기반 `TwoPointTableModel` 구현.
  - `TraceTableModel`, `TraceDetailPanel`, `BinGraphWidget` 구현.
  - ISO T1과 India ISEER을 별도 config/calculator로 분리 계산.
    - ISO: `data/region_configs/iso_t1_default_2point.json`
    - ISEER: `data/region_configs/india_iseer.json`
  - 실시간 자동 계산 구조 구현.
  - 입력값 부족/오류 시 결과 clear 처리.
  - 대량 붙여넣기 성능 방어를 위해 `_bulk_updating` 플래그 및 affected rows 일괄 재계산 구조 추가.
  - QPainter 기반 단순 graph 2종 구현.
    - Bin Hours
    - Load vs Capacity
  - `matplotlib`, `pyqtgraph` 등 외부 그래프 의존성은 추가하지 않음.

- `ui/calc_window.py`
  - 기존 Calculator UI에 2점식 ISO/ISEER UI를 연결했으나, legacy UI가 완전히 제거되지 않은 상태.

### 검증 상태

- `py_compile` 통과:
  - `core/calculator_iso16358.py`
  - `ui/calc_window.py`
  - `ui/calculators_2point.py`

- `CalculatorWindow()` 생성 테스트는 macOS에서 크래시 없이 통과.
- ISO T1 / bin_details 관련 테스트는 통과 확인.
- 전체 pytest는 SASO T3 Phase R2-2 완료 후 `97 passed, 1 xfailed` 상태.
  - 남은 xfailed는 Hong Kong source golden CSPF 4.83 formula review pending이며, 이번 2점식 ISO/ISEER UI 작업과 직접 관련된 실패는 아님.

### 현재 UI 문제

현재 UI는 기능이 일부 구현되었지만, 기존 ISO legacy UI 위에 새 2점식 UI가 덧붙은 형태라 최종 의도와 다름.

확인된 문제:

1. 기존 legacy UI가 남아 있음
   - 하단에 `[계산하기]` 버튼이 그대로 표시됨.
   - `"결과 대기 중..."` 같은 legacy 결과 라벨이 남아 있음.
   - 실시간 자동 계산 UI로 확정했으므로 계산 실행 버튼은 없어야 함.

2. 테이블 선택 UX 문제
   - 셀 하나를 클릭해도 행 전체가 선택된 것처럼 보임.
   - 실제 입력은 해당 셀에만 들어가지만, 사용자가 현재 셀을 선택한 것인지 행을 선택한 것인지 구분하기 어려움.
   - 셀 단위 선택/편집 UX로 조정 필요.

3. 엑셀 복사/붙여넣기 미동작
   - 엑셀에서 값을 복사해 batch table에 붙여넣는 기능이 기대대로 동작하지 않음.
   - macOS 기준 `Cmd+V`, 가능하면 `Ctrl+V`도 확인 필요.
   - `TwoPointTableView.keyPressEvent`, clipboard TSV parsing, `model.paste_tsv()` 연결을 우선 점검해야 함.

4. 메인 테이블 가로 폭 문제
   - 행/컬럼 전체 너비 대비 프로그램 창 너비가 좁아 많은 열이 보이지 않음.
   - 기본 창 크기, 컬럼 폭, horizontal scroll, header resize mode 재조정 필요.

5. 상세보기 Trace Table 높이 문제
   - 상세보기 토글 오픈 시 trace table 영역에 행이 약 2개만 보여서 검증이 불편함.
   - trace table이 최소 10~15행 이상 보이도록 상세 영역 높이 조정 필요.
   - 필요하면 `QSplitter` 또는 scroll/resize 정책 검토.

6. 디자인/스타일 미흡
   - 첨부한 스타일 레퍼런스처럼 rounded / soft / card-like UI가 충분히 반영되지 않음.
   - 현재는 기본 PyQt 스타일에 가까움.
   - 단, 다음 작업의 최우선은 legacy 제거와 UX 정리이며, 디자인은 과한 리팩토링 없이 최소 개선부터 진행.

### 다음 작업 방향

다음 작업은 기능 추가가 아니라 **Calculator ISO 탭 UI 재구성 / legacy 제거 / UX 안정화**가 목표다.

핵심 방향:

- 전체 앱을 밀지 않는다.
- core 계산 로직은 건드리지 않는다.
- `bin_details` 추가와 `ui/calculators_2point.py`의 모델/계산 구조는 유지한다.
- `calc_window.py`의 기존 ISO legacy UI만 과감히 제거한다.
- ISO 탭 content는 새 `TwoPointCalculatorWidget` 또는 equivalent wrapper 하나로 교체한다.
- `calc_window.py`는 최상위 탭 조립과 placeholder 배치 중심으로 최소화한다.

다음 작업 권장 순서:

1. 기존 ISO legacy UI 제거
   - `[계산하기]` 버튼 제거
   - `lbl_result` / `"결과 대기 중..."` 제거
   - `combo_region_iso` 기반 legacy flow 제거
   - `on_calculate()`에서 ISO 탭 처리 제거

2. ISO 탭을 새 2점식 UI 전용 위젯으로 교체
   - `ui/calculators_2point.py`의 구조를 활용
   - `calc_window.py`에는 새 위젯만 배치

3. 엑셀 붙여넣기 기능 수정
   - macOS `Cmd+V` 확인
   - TSV paste 후 affected rows만 계산

4. 테이블 선택/편집 UX 개선
   - 행 전체 선택처럼 보이지 않게 수정
   - 셀 단위 선택이 명확히 보이도록 조정

5. 창 크기 / 테이블 컬럼 폭 / 상세보기 높이 개선
   - 기본 창 크기 확대
   - 주요 컬럼 가시성 개선
   - trace table 최소 표시 행 수 확대

6. 이후 Korea CSPF / SASO T3 / EN14825 / AHRI210240 UI 확장은 2점식 탭 UX 안정화 후 진행
