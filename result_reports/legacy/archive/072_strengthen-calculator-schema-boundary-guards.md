# 072 Strengthen calculator schema boundary guards

## Goal

audit_4 task 4: ML 복귀 전에 region config / calculator core 오염 방지 범위를
조금 더 넓힌다. 새 input envelope 관련 용어와 candidate/ranking 식별자를
adapter 경계 밖에서 차단한다.

## Scope

- `tests/test_calculator_schema_boundaries.py`
  - `BANNED_REGION_RUNTIME_KEYS` 확장
  - `ADAPTER_ONLY_TERMS` 확장

## Non-goals

- region config 값 수정 (모든 production region config는 새 guard에서 그대로
  통과)
- calculator logic 수정
- adapter 기능 구현과 혼합 (task 3에서 이미 분리 완료)

## Verification

- `python3 -B -m pytest tests/test_calculator_schema_boundaries.py tests/test_calculator_input_adapter.py tests/test_calculator_result_adapter.py -q`
  - `15 passed`
- `python3 -B -m pytest -q`
  - `312 passed, 23 xfailed` (회귀 없음)
- 사전 검증으로 9개 region config 모두에서 `candidate_id, predicted_points,
  calculator_input, calculator_result, ranking, ranking_features`가 등장하지
  않음을 확인.

## Task Results

- task 4: OK
  - `BANNED_REGION_RUNTIME_KEYS`에 다음 6개 추가:
    `candidate_id, predicted_points, calculator_input, calculator_result,
    ranking, ranking_features`. 기존 `candidate / prediction / model_version /
    raw_result`는 유지.
  - `ADAPTER_ONLY_TERMS`에 다음 4개 추가:
    `predicted_points, calculator_input, calculator_result, ranking_features`.
    기존 envelope 타입과 `raw_result / model_version / prediction`은 유지.
  - adapter 모듈(`core/calculator_result_adapter.py`,
    `core/calculator_input_adapter.py`)는 이미 task 3에서 `ADAPTER_MODULES`로
    예외 처리됨.
  - 새 guard에서 기존 region config 9개 모두 정상 통과:
    `en14825_scop.json, eu.json, hong_kong.json, india_iseer.json,
    iso_t1_default_2point.json, korea.json, saso.json, usa.json,
    usa_hspf2.json`.

## Test Results

- `tests/test_calculator_schema_boundaries.py` → 3 passed (강화된 guard 통과)
- `tests/test_calculator_input_adapter.py` → 8 passed
- `tests/test_calculator_result_adapter.py` → 4 passed
- 전체 suite → 312 passed, 23 xfailed (회귀 없음)

## Changed Files

- `tests/test_calculator_schema_boundaries.py`

## Known Failures / Risks

- guard는 정적 검사(import/substring/JSON key)만 수행하므로, dynamic하게
  생성되는 key (예: f-string으로 만드는 key)는 검출되지 않는다. 현재 region
  config는 정적 JSON이므로 한계 없음.
- `candidate`는 substring match가 아니라 region config key casefold match.
  따라서 calculator core 코드의 `"candidate"` 변수명/주석은 영향받지 않는다.
- ADAPTER_ONLY_TERMS는 substring match이므로 calculator core가 우연히
  `"calculator_input"`을 포함한 문자열을 사용하지 않도록 주의 필요. 현재는
  모두 미사용.

## Next Suggested Action

- audit_4 4개 task가 모두 완료되었으므로 reference_files에 최종 완료 리포트
  생성.
- 차기 envelope slice (e.g. PredictedPointsEnvelope → CalculatorInputEnvelope
  변환 chain)는 ML caller가 실제로 들어올 때 추가.

## Scope Compliance

- 코드/region config/calculator/adapter 본체 수정 없음.
- 테스트 데이터만 확장.
- adapter-owned 용어가 calculator core로 새어 들어오지 않음을 정적으로
  보장.

## Commit / Push

- 본 보고서 작성 시점 source 커밋: `2a3b680`.
- 다음: report 커밋 후 push.
