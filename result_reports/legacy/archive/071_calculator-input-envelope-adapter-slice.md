# 071 Calculator input envelope adapter slice

## Goal

audit_4 task 3: 061 envelope design의 다음 slice로, ML/manual candidate input을
calculator input으로 변환하는 최소 adapter를 추가한다. `ahri_usa_seer2`만
지원하고 calculator public API는 변경하지 않는다.

## Scope

- `core/calculator_input_adapter.py` (신규)
- `tests/test_calculator_input_adapter.py` (신규)
- `tests/test_calculator_schema_boundaries.py` (어댑터 module 예외 확장)

## Non-goals

- ML/inverse-search caller 구현
- calculator return schema 변경
- region config schema 변경
- 여러 profile 지원 확장 (현재 ahri_usa_seer2만)
- 단위 변환 구현

## Verification

- `python3 -B -m py_compile core/calculator_input_adapter.py tests/test_calculator_input_adapter.py`
  - passed
- `python3 -B -m pytest tests/test_calculator_input_adapter.py tests/test_calculator_result_adapter.py tests/test_calculator_schema_boundaries.py tests/test_ahri_seer2_smoke.py -q`
  - `17 passed`
- 신규 테스트 `test_envelope_is_calculator_ready_for_ahri_seer2`가 envelope의
  `test_points`를 직접 `AHRICalculator.calculate_seer2(...)`에 전달해 결과
  `SEER2 > 0`를 확인. → envelope이 calculator 입력 계약과 호환됨을 증명.

## Task Results

- task 3: OK
  - 새 모듈 `core/calculator_input_adapter.py`에 `build_calculator_input_envelope`
    함수 추가:
    - 지원 profile: `ahri_usa_seer2` (다른 profile은 `ValueError`).
    - 필수 point: `A_Full, B_Full, B_Low, E_Int, F_Low`.
    - 입력 포인트는 `(capacity, power)` tuple 또는
      `{"capacity": ..., "power": ...}` dict 모두 수용.
    - capacity 단위는 `Btu/h`, power 단위는 `W`만 허용. 다른 단위 명시 시 즉시
      에러 (단위 변환은 의도적으로 제외).
    - 음수/0 값, 누락된 point, 잘못된 형식에 대해 fail-fast.
    - 반환 envelope:
      `{calculator_profile_id, calculator_id, test_points, units, source}`.
      `test_points`는 곧바로 `calculate_seer2(test_points=...)`에 전달 가능.
  - 새 테스트 8건은 tuple/dict 입력 정상 경로, predicted source 태깅,
    calculator-ready compatibility, fail-fast 4가지 (지원되지 않는 profile,
    누락된 point, 음수 값, 잘못된 단위, 잘못된 형식) 모두 cover.
  - `tests/test_calculator_schema_boundaries.py`는 기존에 result adapter
    한 모듈만 envelope term 예외로 두고 있었음. input adapter도 동등하게
    adapter-owned이므로 `ADAPTER_MODULES` set으로 확장.

## Test Results

- `tests/test_calculator_input_adapter.py` → 8 passed (신규)
- `tests/test_calculator_result_adapter.py` → 4 passed (회귀 없음)
- `tests/test_calculator_schema_boundaries.py` → 3 passed
- `tests/test_ahri_seer2_smoke.py` → 2 passed
- 총 17 passed

## Changed Files

- `core/calculator_input_adapter.py` (new)
- `tests/test_calculator_input_adapter.py` (new)
- `tests/test_calculator_schema_boundaries.py` (`ADAPTER_MODULE` →
  `ADAPTER_MODULES` set, 새 input adapter 모듈 포함)

## Known Failures / Risks

- 현재는 `ahri_usa_seer2` 단일 프로파일만 지원. EN14825, KS C 9306, ISO 16358
  profile 확장은 후속 slice로 분리해야 한다.
- 단위 변환을 구현하지 않으므로, ML 모듈이 다른 단위를 사용할 경우 caller가
  먼저 변환해야 한다. 이는 envelope이 단위 변환 책임을 떠안지 않도록 의도된
  설계.
- envelope schema (특히 `source` 필드)는 아직 caller가 없으므로 작은 확장
  여지가 있다. 추후 ML caller가 추가되면 schema lock 필요.

## Next Suggested Action

- audit_4 task 4 (adapter schema boundary guard 강화: region config 금지 key
  추가 + adapter-owned term guard 보강)

## Scope Compliance

- 계산기 public API 미변경 (signature, return dict 모두 동일).
- region config 미수정.
- calculator return schema 미변경.
- 새 모듈 import 경계: `core.calculator_profiles`만 의존. UI/ML/numpy/pandas
  미사용.
- adapter-owned 용어(`PredictedPointsEnvelope`, `CalculatorInputEnvelope`,
  `prediction` 등)는 새 adapter 안에서만 등장하고, calculator core 모듈에는
  유입되지 않음 (boundary guard 통과).

## Commit / Push

- 본 보고서 작성 시점 source 커밋: `f7c7527`.
- 다음: report 커밋 후 push.
