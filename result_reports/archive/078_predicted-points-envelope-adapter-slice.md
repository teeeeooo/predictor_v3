# 078 PredictedPointsEnvelope adapter slice

## Goal

audit_5 task 3: ML / manual candidate 출력 형태를 CalculatorInputEnvelope로
넘기기 전 단계인 `PredictedPointsEnvelope`의 첫 slice를 추가한다. AHRI SEER2
한정. 단위 변환은 하지 않는다.

## Scope

- `core/calculator_prediction_adapter.py` (신규)
- `tests/test_calculator_prediction_adapter.py` (신규)
- `tests/test_calculator_schema_boundaries.py` (adapter modules set 확장)

## Non-goals

- 실제 ML model 호출
- ranking 구현
- region config 변경
- calculator public API 변경
- 단위 변환

## Verification

- `python3 -B -m py_compile core/calculator_prediction_adapter.py
  tests/test_calculator_prediction_adapter.py` → passed
- `python3 -B -m pytest tests/test_calculator_prediction_adapter.py
  tests/test_calculator_input_adapter.py
  tests/test_calculator_result_adapter.py
  tests/test_calculator_schema_boundaries.py -q` → `49 passed`
- `python3 -B -m pytest -q` → `352 passed, 23 xfailed` (회귀 없음)

## Task Results

- task 3: OK
  - 새 함수 `build_predicted_points_envelope(profile_id, points,
    source, model_target, metadata)`:
    - 지원 profile: `ahri_usa_seer2` (다른 profile은 `ValueError`).
    - 필수 point: `A_Full, B_Full, B_Low, E_Int, F_Low`.
    - 각 point는 `capacity, power, capacity_unit, power_unit` 4 키를
      반드시 가져야 함. 다른 키는 fail-fast.
    - 단위는 `capacity_unit="Btu/h"`, `power_unit="W"`만 허용 (단위 변환
      없음).
    - `source` vocabulary: `manual_candidate / ml_prediction / fixture`.
      legacy `manual / predicted`는 reject.
    - `model_target` vocabulary: `cooling / heating / multi`. profile.mode
      와 호환되어야 함 (AHRI SEER2는 cooling profile이라 heating target은
      reject).
    - `metadata`는 `{model_version, candidate_id}`만 허용. 다른 key는
      reject.
  - 새 함수 `predicted_points_to_calculator_input_envelope(envelope,
    profile_id)`:
    - capacity/power만 추려서 기존 `build_calculator_input_envelope`에
      전달.
    - `source`는 그대로 보존 (`options["source"]`로 흘러감).
    - `candidate_id, model_version, model_target`은 옵션으로
      `options`에 채워 calculator-layer가 후속 단계에서 참고 가능.
  - `tests/test_calculator_schema_boundaries.py`의 `ADAPTER_MODULES`
    set에 새 모듈 추가 — adapter-owned vocabulary 사용 정당화.
  - 새 테스트 18건:
    - shape match, allowed source/model_target parametrized,
      legacy source reject, unknown model_target reject,
      missing/extra point keys, missing/extra inner keys, unit reject
      (capacity / power), non-positive value reject, unsupported profile
      reject, metadata key reject, allowed metadata pass-through,
      converter preserves source/metadata, end-to-end calculator-ready
      flow, malformed dict reject.

## Test Results

- `tests/test_calculator_prediction_adapter.py` → 18 passed
- `tests/test_calculator_input_adapter.py` → 18 passed (회귀 없음)
- `tests/test_calculator_result_adapter.py` → 4 passed (회귀 없음)
- `tests/test_calculator_schema_boundaries.py` → 3 passed (회귀 없음)
- 전체 suite → 352 passed, 23 xfailed.

## Changed Files

- `core/calculator_prediction_adapter.py` (new)
- `tests/test_calculator_prediction_adapter.py` (new)
- `tests/test_calculator_schema_boundaries.py` (`ADAPTER_MODULES` set 갱신)

## Known Failures / Risks

- 단일 profile (AHRI SEER2)만 지원. EN14825 / KS C 9306 / ISO 16358 등의
  cooling/heating profile은 후속 slice에서 추가해야 한다.
- 단위 변환 미지원. ML 모듈이 다른 단위를 쓰는 경우 caller가 먼저 변환해야
  한다 (계획된 설계 결정).
- AHRI SEER2 cooling profile에서 `model_target="multi"`는 통과한다. 향후
  multi-target 모델이 들어오면 어떤 mode와 호환되어야 하는지 명세를 더
  타이트하게 잡아야 한다. 현재는 "어떤 mode와도 호환"으로 단순화.

## Next Suggested Action

- audit_5 task 5 (RankingCandidateEnvelope 최소 smoke)

## Scope Compliance

- 실제 ML model 호출 없음.
- ranking 구현 없음.
- region config 미수정.
- calculator public API 미변경.
- 새 adapter 모듈은 `core.calculator_profiles`와
  `core.calculator_input_adapter`만 의존. UI/ML/numpy/pandas 미사용.

## Commit / Push

- Source commit: `f4e9d84`.
- Report commit: 별도로 추가 예정.
