# Audit 5 Next Actions — Completion Report

## 요약

`reference_files/audit_5.md`가 제시한 "지금 당장 할 수 있는 다음 작업 6개"를
모두 완료했다. 각 task는 source 커밋과 report 커밋을 분리하고,
`result_reports/active/074` ~ `079`에 단계별 결과 리포트를 추가했다.

audit_5의 추천 순서 `task 1 → 2 → 6 → 3 → 5`에 task 4 (UI happy-path)을
끼워 넣어 실제 진행 순서는 `1 → 2 → 6 → 4 → 3 → 5`로 수행했다.

| Task | 제목 | 상태 | Source commit | Report (`result_reports/active/`) |
| ---- | ---- | ---- | ------------- | --------------------------------- |
| 1 | Audit 4 이후 문서 상태 동기화 | OK | `3acc966` | `074_sync-active-docs-after-audit4.md` |
| 2 | CalculatorInputEnvelope schema 정합성 고정 | OK | `614dfd6` | `075_align-calculator-input-envelope-with-design.md` |
| 6 | EN14825 SEER profile/UI 연결 | OK | `80ef665` | `076_en14825-seer-profile-ui-wiring.md` |
| 4 | AHRI HP/HSPF2 UI happy-path smoke | OK | `223192b` | `077_ahri-hp-hspf2-ui-happy-path-smoke.md` |
| 3 | PredictedPointsEnvelope 첫 slice | OK | `f4e9d84` | `078_predicted-points-envelope-adapter-slice.md` |
| 5 | RankingCandidateEnvelope 최소 smoke | OK | `dd283dc` | `079_ranking-candidate-envelope-min-smoke.md` |

## 환경 / 도구

- 작업 브랜치: `work/iso-separation-plan`
- Python 3 + PyQt5 사용 가능 환경에서 모든 UI smoke가 실행됨.
- 검증 명령: `python3 -B -m py_compile`, `python3 -B -m pytest -q`.

## Task 1 — Audit 4 이후 문서 상태 동기화

### Goal

audit_4 이후의 실제 상태(EN SCOP UI 연결, AHRI SEER2 envelope adapter 첫
slice, schema boundary guard 강화)와 active 문서의 next-action 상태가 어긋난
것을 맞춘다.

### Changed Files

- `project_log.md`
- `docs/WORK_PLAN.md`
- `project_brief.md`

### 결과

- `project_log.md` 앞쪽에 `2026-05-17 — Audit 4 next actions completion
  (069 ~ 073)` block 추가 (Result / Decision / Verification 3 섹션, 소스/리포트
  커밋 해시 포함).
- `docs/WORK_PLAN.md` Current milestone focus에 EN14825 SCOP UI wiring,
  AHRI SEER2 envelope first slice, schema boundary guard 강화 상태를 추가.
  Near-term execution order는 design doc 정렬 → PredictedPoints → ranking
  smoke → ML caller 순으로 갱신하고 EN14825 SEER profile/UI follow-up도
  추가.
- `project_brief.md`의 Calculator UI / ML adapter 문장을 envelope adapter
  slice + schema guard 적용 상태로 갱신.

### Verification

- docs-only 변경이므로 새 pytest 실행 없음. 직전 audit_4 검증 결과를 그대로
  유효 처리.

## Task 2 — CalculatorInputEnvelope schema 정합성 고정

### Goal

design doc과 첫 slice 구현의 schema 불일치 (source vocab, 누락 필드,
test_points key, extra key 허용 여부)를 제거한다.

### Changed Files

- `core/calculator_input_adapter.py`
- `tests/test_calculator_input_adapter.py`
- `docs/designs/2026-05-17-calculator-result-envelope-ml-adapter.md`

### 결과

- Envelope top-level 재구성:
  `{calculator_profile_id, standard, region, mode, metric, measured_inputs,
  options}`. `standard / region / mode / metric`은 `CalculatorProfile`에서
  채움.
- `measured_inputs`는 `{point: {capacity, power}}` dict 구조 (tuple → dict).
- `options`는 기본적으로 `{units, source}`를 포함하고, caller가 추가 options을
  넘기면 reserved key (`units`, `source`)는 덮어쓸 수 없다.
- `source` vocabulary는 `manual_candidate / ml_prediction / fixture`만 허용.
  legacy `manual / predicted`는 fail-fast.
- `ALLOWED_SOURCE_VALUES` 모듈-level tuple export.
- extra point key, point 내부 extra key, extra unit key 전부 fail-fast.
- 새 helper `measured_inputs_as_test_points(envelope)`: 곧바로
  `AHRICalculator.calculate_seer2(...)`에 쓸 수 있는 tuple form 반환. 계산기
  public API 미변경.
- design doc에 "Implementation Status (as of 2026-05-17 audit_5 task 2)"
  섹션 추가.

### Verification

- `python3 -B -m pytest tests/test_calculator_input_adapter.py
  tests/test_calculator_result_adapter.py
  tests/test_calculator_schema_boundaries.py tests/test_ahri_seer2_smoke.py -q`
  → `29 passed`
- 전체 suite → `324 passed, 23 xfailed`.

## Task 6 — EN14825 SEER profile / UI 연결

### Goal

이미 구현되어 있는 `EN14825Calculator.calculate_seer()`를 profile / dispatcher /
UI 흐름에서도 사용할 수 있게 연결한다. SCOP 경로 동작은 보존.

### Changed Files

- `core/calculator_profiles.py`
- `tests/test_calculator_profiles.py`
- `tests/test_calculator_dispatcher.py`
- `ui/calc_window.py`
- `tests/test_app_calculator_ui_smoke.py`

### 결과

- 새 profile `en14825_seer` (standard=EN_14825, region=europe, metric=SEER,
  mode=cooling, calculator_id=en14825). 별도 SEER config는 만들지 않고
  `data/region_configs/en14825_scop.json`을 재사용 (SEER 경로는 SCOP config
  정적 키를 읽지 않음).
- dispatcher는 기존에 `calculator_id="en14825"`를 지원하므로 추가 수정 없이
  새 profile로 EN14825Calculator를 반환.
- EN combo가 SCOP/SEER profile을 모두 노출 (SCOP 우선 정렬).
- 새 입력 `p_design_c (kW, SEER)` 추가. `p_design_h / climate / TOL / Tbiv`는
  SCOP 전용으로 label에 명시.
- `on_region_changed_en`이 `self.en_profile`을 저장하고,
  `calculate_en()`은 `self.en_profile.metric`에 따라 `calculate_seer` 또는
  `calculate_scop`를 호출. SEER 결과 label: `EN14825 SEER 결과: <seer>`.

### Verification

- `python3 -B -m pytest tests/test_calculator_profiles.py
  tests/test_calculator_dispatcher.py tests/test_app_calculator_ui_smoke.py
  tests/test_en14825_golden.py -q` → `48 passed`
- 전체 suite → `329 passed, 23 xfailed`.

## Task 4 — AHRI HP/HSPF2 UI happy-path smoke

### Goal

기존 AHRI UI smoke는 AC 경로와 HSPF2 validation만 보호. HP 모드에서 SEER2 +
HSPF2 v3 결과가 result label에 함께 출력되는지 확인하는 happy-path가 없었다.

### Changed Files

- `tests/test_app_calculator_ui_smoke.py`

### 결과

- 새 smoke `test_ahri_hp_calculate_button_displays_seer2_and_hspf2_results`:
  - HP 모드 선택.
  - AHRI SEER2 5 포인트 (`A_Full..F_Low`) + HSPF2 v3 7 포인트
    (`H01..H32`) + `t_off/t_on/defrost_t_test_minutes/defrost_t_max_minutes`
    입력.
  - 입력 값은 `tests/test_ahri_hspf2_v3_smoke.py`에서 가져와 HSPF2 계산이
    안정적으로 수치를 만들 수 있게 함.
  - 버튼 클릭 후 result label에 `"AHRI SEER2 (HP) 결과:"`와
    `"HSPF2 v3 결과:"`가 모두 포함되는지 substring 검증.
- 계산기/UI 코드 변경 없음.

### Verification

- `python3 -B -m pytest tests/test_app_calculator_ui_smoke.py -q` → `10 passed`.

## Task 3 — PredictedPointsEnvelope 첫 slice

### Goal

ML / manual candidate 출력을 CalculatorInputEnvelope로 넘기기 전 단계
(`PredictedPointsEnvelope`) 의 첫 slice를 추가. AHRI SEER2 한정, 단위 변환
없음.

### Changed Files

- `core/calculator_prediction_adapter.py` (new)
- `tests/test_calculator_prediction_adapter.py` (new)
- `tests/test_calculator_schema_boundaries.py` (ADAPTER_MODULES 갱신)

### 결과

- `build_predicted_points_envelope(profile_id, points, source,
  model_target, metadata)`:
  - 지원 profile: `ahri_usa_seer2` 단일.
  - 각 point는 `capacity, power, capacity_unit, power_unit` 4 키 필수.
    다른 키 reject.
  - 단위는 `capacity_unit="Btu/h"`, `power_unit="W"`만 허용.
  - `source` vocabulary는 input adapter와 동일 (`manual_candidate /
    ml_prediction / fixture`).
  - `model_target` vocabulary: `cooling / heating / multi`. profile.mode와
    호환되어야 함 — AHRI SEER2 cooling profile은 heating target reject.
  - `metadata`는 `{model_version, candidate_id}`만 허용. 다른 키 reject.
- `predicted_points_to_calculator_input_envelope(envelope, profile_id)`:
  - capacity/power만 추려서 기존 input adapter를 재사용.
  - `source`는 그대로 보존 (`options["source"]`로 흘러감).
  - `candidate_id / model_version / model_target`은 `options`로 복사.
- 새 테스트 18건. PredictedPoints → CalculatorInput →
  `calculate_seer2(...)` end-to-end smoke 포함.

### Verification

- `python3 -B -m pytest tests/test_calculator_prediction_adapter.py
  tests/test_calculator_input_adapter.py
  tests/test_calculator_result_adapter.py
  tests/test_calculator_schema_boundaries.py -q` → `49 passed`
- 전체 suite → `352 passed, 23 xfailed`.

## Task 5 — RankingCandidateEnvelope 최소 smoke

### Goal

ML 복귀 전, `CalculatorResultEnvelope`을 ranking layer가 소비할 수 있는
최소 형태로 변환하는 adapter slice를 추가한다.

### Changed Files

- `core/calculator_ranking_adapter.py` (new)
- `tests/test_calculator_ranking_adapter.py` (new)
- `tests/test_calculator_schema_boundaries.py` (ADAPTER_MODULES 갱신)

### 결과

- `build_ranking_candidate_envelope(candidate_id, result_envelope,
  score=None, ranking_features=None)`:
  - 입력은 `CalculatorResultEnvelope` mapping. raw calculator dict 직접 받지
    않음 (design contract).
  - 출력 shape (audit_5 task 5 지시):
    `{candidate_id, calculator_profile_id, metric, value, units, score,
    ranking_features}`.
  - `score`는 caller 미지정 시 `result_envelope["value"]`로 기본 설정.
  - `ranking_features`는 dict로 얕은 복사. caller mutate가 envelope에
    유출되지 않음을 테스트로 보장.
  - `raw_result`, `diagnostics`는 ranking envelope에 노출하지 않음 — ranker는
    envelope fields만 소비해야 한다는 design contract 강제.
  - fail-fast: 빈/non-string `candidate_id`, non-mapping `result_envelope`,
    필수 키 누락, non-mapping `ranking_features`.
- `predicted_points_ref`, `calculator_result_ref` 같은 design doc의 추가
  식별자는 registry가 필요할 때까지 의도적으로 제외.
- 새 테스트 12건.

### Verification

- `python3 -B -m pytest tests/test_calculator_ranking_adapter.py
  tests/test_calculator_prediction_adapter.py
  tests/test_calculator_input_adapter.py
  tests/test_calculator_result_adapter.py
  tests/test_calculator_schema_boundaries.py -q` → `61 passed`
- 전체 suite → `364 passed, 23 xfailed`.

## 종합 검증

- 단계별 부분 검증은 각 task 절에 기재.
- 최종 종합:
  - `python3 -B -m pytest tests/test_app_calculator_ui_smoke.py
    tests/test_calculator_result_adapter.py
    tests/test_calculator_input_adapter.py
    tests/test_calculator_prediction_adapter.py
    tests/test_calculator_ranking_adapter.py
    tests/test_calculator_schema_boundaries.py
    tests/test_calculator_profiles.py tests/test_calculator_dispatcher.py
    tests/test_en14825_golden.py tests/test_ahri_seer2_smoke.py -q`
    → `112 passed`.
  - `python3 -B -m pytest -q` → `364 passed, 23 xfailed`.

## 커밋 / push 기록

각 task의 source 커밋과 report 커밋을 분리하고, 본 reference report는 별도
final commit으로 추가한다.

| # | Commit | 내용 |
| - | ------ | ---- |
| 1 | `3acc966` | docs: sync active docs to audit_4 completion state |
| 2 | `0759744` | report: record post-audit-4 active docs sync |
| 3 | `614dfd6` | feat: align CalculatorInputEnvelope with design doc shape |
| 4 | `9fe1097` | report: record CalculatorInputEnvelope design alignment |
| 5 | `80ef665` | feat: add EN14825 SEER profile and wire it through the UI |
| 6 | `01b6909` | report: record EN14825 SEER profile and UI wiring |
| 7 | `223192b` | test: add AHRI HP happy-path smoke covering SEER2 + HSPF2 |
| 8 | `73180d2` | report: record AHRI HP / HSPF2 UI happy-path smoke |
| 9 | `f4e9d84` | feat: add PredictedPointsEnvelope adapter slice for AHRI SEER2 |
| 10 | `379f4e3` | report: record PredictedPointsEnvelope adapter slice |
| 11 | `dd283dc` | feat: add RankingCandidateEnvelope minimum smoke adapter |
| 12 | `754dd94` | report: record RankingCandidateEnvelope minimum smoke |

push는 사용자가 검토 후 직접 진행하는 것이 본 프로젝트 규약이므로 본 작업
범위에서는 push를 수행하지 않았다.

## 남은 위험 / 후속 작업 후보

- PredictedPoints / CalculatorInput / CalculatorResult / RankingCandidate
  4단계 envelope chain은 인접 쌍 smoke로 보호되지만, 4단계 end-to-end smoke
  하나로 묶어두면 ML caller 도입 시 schema drift를 더 빨리 잡을 수 있다.
- envelope adapter는 모두 `ahri_usa_seer2` 단일 profile만 지원한다. EN14825
  SEER/SCOP, KS C 9306 CSPF/HSPF, ISO 16358 CSPF profile은 후속 slice
  대상.
- 단위 변환 (capacity Btu/h ↔ kW, power W ↔ kW)은 의도적으로 envelope 밖.
  ML 모듈이 다른 단위를 사용할 가능성이 높으므로, caller 측 단위 정규화
  helper를 별도 모듈로 추가하는 것이 다음 단계로 자연스럽다.
- UI는 SEER/SCOP 모두 단일 form layout에 항목을 추가해 입력이 길어졌다.
  매우 작은 화면에서는 후속 UI 정리가 필요하다.
- `reference_files/`는 `.gitignore` 대상이므로 본 보고서는 `git add -f`로
  강제 추적한다 (audit_3 / audit_4와 동일 패턴).

## Scope Compliance

- 각 task의 "수정 대상" 외 파일은 수정하지 않았다.
- 계산기 공식, golden expected, region config, ML 본체 코드는 모두 미변경.
- adapter-owned 용어가 calculator core로 새어 들어오지 않음을 정적 가드
  (`tests/test_calculator_schema_boundaries.py::ADAPTER_MODULES`)로 보장.
- audit_5 각 task 금지 항목 준수:
  - task 1: code/test/adapter schema/UI 미수정 (docs-only).
  - task 2: ML caller / public API / 공식 / 다중 profile 확장 미수행.
  - task 6: SEER 공식 / golden / SCOP 경로 / EN UI redesign / ML adapter
    혼합 미수행.
  - task 4: HSPF2 공식 / golden / UI redesign 미수행.
  - task 3: 실제 ML model 호출 / ranking / region config / calculator API
    변경 미수행.
  - task 5: inverse-search / multi-objective ranking / ML predictor /
    calculator result schema 변경 미수행.
