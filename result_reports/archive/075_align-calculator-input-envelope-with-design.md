# 075 Align CalculatorInputEnvelope with design doc

## Goal

audit_5 task 2: AHRI SEER2 첫 slice의 envelope shape을 design doc
(`docs/designs/2026-05-17-calculator-result-envelope-ml-adapter.md`)과
정렬한다. source vocabulary를 design vocab로 고정하고, profile에서
standard/region/mode/metric을 채우고, measured_inputs key 구조를 정렬하고,
extra key는 fail-fast로 처리한다.

## Scope

- `core/calculator_input_adapter.py` (shape 재구성, source vocab lock, helper 추가)
- `tests/test_calculator_input_adapter.py` (새 shape에 맞춘 테스트 재작성)
- `docs/designs/2026-05-17-calculator-result-envelope-ml-adapter.md`
  (Implementation Status section 추가, source 위치 명시)

## Non-goals

- ML caller 구현
- calculator public API 변경 (`calculate_seer2` signature/return 그대로 유지)
- AHRI SEER2 공식 수정
- 여러 profile 지원 확장 (여전히 `ahri_usa_seer2` 단일)

## Verification

- `python3 -B -m py_compile core/calculator_input_adapter.py
  tests/test_calculator_input_adapter.py` → passed
- `python3 -B -m pytest tests/test_calculator_input_adapter.py
  tests/test_calculator_result_adapter.py
  tests/test_calculator_schema_boundaries.py tests/test_ahri_seer2_smoke.py -q`
  → `29 passed`
- `python3 -B -m pytest -q` → `324 passed, 23 xfailed` (회귀 없음)

## Task Results

- task 2: OK
  - envelope top-level이 design doc shape과 일치:
    `{calculator_profile_id, standard, region, mode, metric, measured_inputs,
    options}`. `standard / region / mode / metric`은 `CalculatorProfile`에서
    채워 넣음.
  - `measured_inputs`는 `{point: {capacity, power}}` dict 구조 (이전 tuple
    저장 방식 제거).
  - `options`는 `{units, source}`를 기본 포함하고, caller가 추가 options을
    전달하면 reserved key (`units`, `source`)를 덮어쓸 수 없음.
  - `source` vocabulary는 `manual_candidate / ml_prediction / fixture` 만
    허용. legacy `manual` / `predicted`는 `ValueError`로 reject.
  - 새 모듈-level `ALLOWED_SOURCE_VALUES` tuple export.
  - extra point key, point 내부 extra key (`capacity, power` 외), unit
    extra key 모두 fail-fast.
  - 새 helper `measured_inputs_as_test_points(envelope)`: envelope을 곧바로
    `AHRICalculator.calculate_seer2(test_points=...)`에 쓸 수 있는 tuple
    dict로 변환. calculator public API는 변경하지 않음.
  - design doc에 "Implementation Status (as of 2026-05-17 audit_5 task 2)"
    섹션 추가: 실제 구현된 shape, source vocab lock, unit handling, helper
    설명.

## Test Results

- `tests/test_calculator_input_adapter.py` → 18 passed
  - 신규: design shape, measured_inputs dict, options 구성, default source,
    parametrized allowed source, legacy vocab reject, extra point/inner/unit
    key reject, options reserved key reject, options pass-through,
    measured_inputs_as_test_points helper, end-to-end calculator-ready.
  - 기존: unsupported profile, missing point, non-positive value, unsupported
    unit, malformed point value 모두 유지.
- `tests/test_calculator_result_adapter.py` → 4 passed (회귀 없음)
- `tests/test_calculator_schema_boundaries.py` → 3 passed (회귀 없음)
- `tests/test_ahri_seer2_smoke.py` → 2 passed
- 전체 suite → 324 passed, 23 xfailed (회귀 없음)

## Changed Files

- `core/calculator_input_adapter.py`
- `tests/test_calculator_input_adapter.py`
- `docs/designs/2026-05-17-calculator-result-envelope-ml-adapter.md`

## Known Failures / Risks

- envelope shape이 직전 audit_4 first slice와 호환되지 않는다. 아직 외부
  caller가 없으므로 schema migration cost는 0이지만, 향후 ML caller가
  실제로 들어오면 추가 변경 없이 이 shape을 그대로 사용해야 한다.
- `source`를 `options["source"]`에 넣는 결정은 design doc의 본문 schema와는
  미세하게 어긋난다 (design doc은 PredictedPointsEnvelope에만 source를
  두고 CalculatorInputEnvelope에는 두지 않음). 이번 task에서는 source
  vocabulary를 끊김 없이 전달해야 하는 실용적 이유로 `options["source"]`
  형태로 보존하고, 그 결정을 design doc Implementation Status에 명시했다.
- helper `measured_inputs_as_test_points`는 의도적으로 AHRI SEER2 tuple
  form만 지원한다. 다른 profile이 추가될 때 helper도 함께 일반화해야 한다.

## Next Suggested Action

- audit_5 task 6 (EN14825 SEER profile/UI 연결)

## Scope Compliance

- region config, ML model, UI 미수정.
- calculator public API (`calculate_seer2`) 미변경.
- AHRI SEER2 공식 미변경.
- 여러 profile 확장 안함 (여전히 `ahri_usa_seer2` 단일 slice).

## Commit / Push

- Source commit: `614dfd6`.
- Report commit: 별도로 추가 예정.
