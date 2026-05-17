# 079 RankingCandidateEnvelope minimum smoke

## Goal

audit_5 task 5: ML 복귀 전, `CalculatorResultEnvelope`을 ranking layer가
소비할 수 있는 최소 형태의 `RankingCandidateEnvelope`을 설계/구현한다.
첫 slice는 단일 metric value를 score로 그대로 쓰는 단순 변환에 한정한다.

## Scope

- `core/calculator_ranking_adapter.py` (신규)
- `tests/test_calculator_ranking_adapter.py` (신규)
- `tests/test_calculator_schema_boundaries.py` (adapter modules set 확장)

## Non-goals

- 실제 inverse-search 구현
- multi-objective ranking 알고리즘 구현
- ML model / predictor 수정
- calculator result schema 변경

## Verification

- `python3 -B -m py_compile core/calculator_ranking_adapter.py
  tests/test_calculator_ranking_adapter.py` → passed
- `python3 -B -m pytest tests/test_calculator_ranking_adapter.py
  tests/test_calculator_prediction_adapter.py
  tests/test_calculator_input_adapter.py
  tests/test_calculator_result_adapter.py
  tests/test_calculator_schema_boundaries.py -q` → `61 passed`
- `python3 -B -m pytest -q` → `364 passed, 23 xfailed`

## Task Results

- task 5: OK
  - 새 함수 `build_ranking_candidate_envelope(candidate_id,
    result_envelope, score=None, ranking_features=None)`:
    - 입력은 `CalculatorResultEnvelope` mapping. raw calculator dict를
      직접 받지 않도록 의도된 설계.
    - 출력 shape (audit_5 task 5 field list):
      `{candidate_id, calculator_profile_id, metric, value, units, score,
      ranking_features}`.
    - `score`는 caller가 명시하지 않으면 `result_envelope["value"]`로
      채워 단일 metric ranking을 즉시 지원.
    - `ranking_features`는 dict로 얕은 복사. caller가 나중에 원본을 mutate
      해도 envelope에는 새 키가 흘러들지 않는다 (test로 보장).
    - `raw_result`, `diagnostics`는 환경 밖으로 노출하지 않음 — ranker는
      envelope의 fields만 소비해야 한다는 design contract 강제.
    - fail-fast: 빈 / non-string `candidate_id`, non-mapping
      `result_envelope`, `result_envelope`에 필수 키 누락,
      non-mapping `ranking_features`.
  - 설계 문서의 추가 필드 (`predicted_points_ref`,
    `calculator_result_ref`)는 첫 slice에서 의도적으로 제외. 실제 ranking
    layer가 registry를 요구하는 시점에 추가한다.
  - `tests/test_calculator_schema_boundaries.py`의 `ADAPTER_MODULES` set
    에 새 모듈 추가 — adapter-owned vocabulary 사용 허가.

## Test Results

- `tests/test_calculator_ranking_adapter.py` → 12 passed (신규)
- 인접 boundary / envelope 테스트 → 회귀 없음
- 전체 suite → 364 passed, 23 xfailed

## Changed Files

- `core/calculator_ranking_adapter.py` (new)
- `tests/test_calculator_ranking_adapter.py` (new)
- `tests/test_calculator_schema_boundaries.py` (`ADAPTER_MODULES` 갱신)

## Known Failures / Risks

- 첫 slice는 단일 metric scoring (score = value)만 지원. 향후 multi-metric
  weighted scoring, 비용/소음 등 ranking_features 기반 합산 모델이
  필요하면 별도 함수/slice로 확장해야 한다.
- `predicted_points_ref`, `calculator_result_ref` 같은 design 문서의
  추가 식별자는 registry가 필요할 때 추가. 현재는 envelope이 self-contained
  로 충분히 동작.
- caller가 `score`를 직접 지정해도 검증 로직은 단순 `float()`만 수행한다.
  음수 score / NaN 등의 정책은 ranking layer 본구현 단계에서 결정해야
  한다.

## Next Suggested Action

- 최종 audit_5 completion 리포트를 `reference_files/`에 작성.
- 후속 작업 후보: PredictedPoints → CalculatorInput → CalculatorResult →
  RankingCandidate 4단계 envelope chain end-to-end smoke (현재는 인접
  쌍 smoke만 있음).

## Scope Compliance

- 실제 inverse-search 구현 없음.
- multi-objective ranking 알고리즘 없음.
- ML model / predictor 미수정.
- calculator result schema 미변경.
- adapter-owned 용어가 calculator core로 새어 들어오지 않음 (`ADAPTER_MODULES`
  guard 통과).

## Commit / Push

- Source commit: `dd283dc`.
- Report commit: 별도로 추가 예정.
