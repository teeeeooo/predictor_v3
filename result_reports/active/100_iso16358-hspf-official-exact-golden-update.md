# 100 ISO16358-2 HSPF official exact golden update

## Goal
099 `_iso_hspf_extended_minus7_default()` fix 이후, ISO16358-2 HSPF official exact 16-case fixture expected를 원문 audit 기준 final value로 갱신하고, `XFAIL_CASE_IDS`를 정리해 strict XPASS 실패를 해소한다.

## Scope / Non-goals
- Scope: `tests/fixtures/iso16358_hspf_official_exact_cases.json` expected 값, `tests/test_iso16358_hspf_official_exact_golden.py::XFAIL_CASE_IDS`, `project_log.md`, `docs/WORK_PLAN.md`, `project_brief.md`.
- Non-goals: 계산 로직 수정, measured input fixture / bin_hours / case description 수정, Formula 식 수정, branch/case naming 변경, ISO table UI, AHRI/EN/UI, adapter/unit conversion, ML, result_reports lifecycle maintenance.

## 배경 요약
기존 fixture expected는 사용자 외부 reference script 출력 기준이었다. 099 직전까지는 11개 case가 strict xfail로 보존되어 있었고, 원문 audit 결과 두 가지 사실이 확인되었다.
- repo 구현의 frost endpoint 정책 / -7 multi-measured 적용 / Formula 50 적용 / saturated 처리는 원문 준수.
- 그러나 `-7_ext` default factor (0.734 / 0.877) 는 2°C **non-frost** → -7°C derivation이므로 2°C frost 측정값 (`2_ext`) 에 직접 곱하면 안 됨. 099에서 2-step (×1.12/×1.06 → ×0.734/×0.877) 으로 정정.

이로 인해 case 3/4/9/10/11이 099만으로 자연 pass했다. 잔여 mismatch 6건 (8/12/13/14/15/16) 은 기존 expected가 stale (구 reference-script가 `2_full`/`2_half` measured를 frost/non-frost 양쪽에 동일 주입하던 해석) 이었음. 본 작업에서 final golden을 원문 audit + 099 기준 actual값으로 정렬.

## task 1 결과
- 수정 파일: `tests/fixtures/iso16358_hspf_official_exact_cases.json`
- 갱신 case: 8, 12, 13, 14, 15, 16 (HSEC / HSPF). HSTL은 16 case 모두 4885.4 kWh로 유지.
- 갱신값:

| case | HSEC (이전 → 신) | HSPF (이전 → 신) |
|------|------------------|------------------|
| 8    | 1077.2 → 1078.5  | 4.535 → 4.530    |
| 12   | 1079.0 → 1108.6  | 4.528 → 4.407    |
| 13   | 1079.0 → 1077.2  | 4.528 → 4.535    |
| 14   | 1079.0 → 1077.2  | 4.528 → 4.535    |
| 15   | 1079.0 → 1112.8  | 4.528 → 4.390    |
| 16   | 1066.3 → 1111.2  | 4.582 → 4.396    |

- case 13/14 expected 동일성 ( duplicate description / expected ) 은 유지.
- measured input, bin_hours, description, config, point_pool 모두 미변경.
- 기준값 출처: 원문 audit 통과한 repo 구현 + 099 -7_ext fix 적용 후 actual.

## task 2 결과
- 수정 파일: `tests/test_iso16358_hspf_official_exact_golden.py`
- `XFAIL_CASE_IDS = frozenset({3, 4, 8, 9, 10, 11, 12, 13, 14, 15, 16})` → `XFAIL_CASE_IDS: frozenset[int] = frozenset()`.
- 기존 strict xfail 마킹은 그대로 두되 set이 비어 있어 어떤 case에도 적용되지 않음. XPASS strict 실패 0.
- tolerance / rounding (`HSTL_decimals=1`, `HSEC_decimals=1`, `HSPF_decimals=3`) 는 그대로 유지. 실패를 다시 xfail로 숨기지 않음.

## task 3 결과
- `tests/test_iso16358_hspf_official_exact_golden.py` → 17 passed (16 case + duplicate 보장 test).
- `tests/test_iso16358_hspf_extended_default.py` → 3 passed.
- `tests/test_iso16358_hspf_frost_trace.py` → 8 passed.
- `tests/test_iso16358_hspf_boundary_cop_alignment.py` → 6 passed, 1 skipped.
- `tests/test_iso16358_hspf_formula_micro.py` → all pass.
- `tests/test_iso16358_hspf_validation.py` → all pass.
- `tests/test_calculator_schema_boundaries.py` → pass.
- Full suite: **425 passed, 4 skipped, 23 xfailed** (XPASS strict 실패 0). 16-case official exact golden pass 확정.

## task 4 결과
- `project_log.md`: "2026-05-19 — ISO16358-2 HSPF -7_ext fix + golden update" 항목 추가 (Tried/Result/Failed-Risk/Decision/Lesson). 2026-05-18 hold log는 historical로 그대로 두고 그 위에 신규 phase 로그 append (merge 가능 여부 검토 후 hold 종료 phase는 분리 기록이 명확하다고 판단).
- `docs/WORK_PLAN.md`: 16/16 pass 상태와 빈 `XFAIL_CASE_IDS` 반영. 다음 순서를 (1) ISO table Excel-like behavior patch (2) ISO result/read-only table copy TSV (3) unit adapter 확장 (4) ML / inverse-search 복귀 준비 로 갱신. 100 항목 요약 추가.
- `project_brief.md`: ISO16358-2 HSPF mismatch hold 문장 제거하고 16/16 pass + `XFAIL_CASE_IDS` 비움을 짧게 반영.
- result report lifecycle maintenance는 이번 작업 범위에서 제외 (별도 정리 작업으로 분리).

## task 5 결과
- report 경로: `result_reports/active/100_iso16358-hspf-official-exact-golden-update.md` (본 파일).
- lifecycle maintenance 제외 이유: 본 작업은 fixture expected 정렬 + xfail 정리 + 관련 문서 갱신에 한정. active/archive/summaries 이동까지 섞으면 commit scope가 커지고 회귀 위험이 증가한다. 별도 lifecycle 작업으로 분리.

## Verification
- `python3 -B -m py_compile core/calculator_iso16358.py tests/test_iso16358_hspf_official_exact_golden.py` → OK
- `python3 -B -m pytest tests/test_iso16358_hspf_official_exact_golden.py -q` → 17 passed
- `python3 -B -m pytest tests/test_iso16358_hspf_extended_default.py -q` → 3 passed
- `python3 -B -m pytest tests/test_iso16358_hspf_frost_trace.py -q` → 8 passed
- `python3 -B -m pytest tests/test_iso16358_hspf_boundary_cop_alignment.py -q` → 6 passed, 1 skipped
- `python3 -B -m pytest tests/test_iso16358_hspf_formula_micro.py -q` → pass
- `python3 -B -m pytest tests/test_iso16358_hspf_validation.py -q` → pass
- `python3 -B -m pytest tests/test_calculator_schema_boundaries.py -q` → pass
- `python3 -B -m pytest -q` → 425 passed, 4 skipped, 23 xfailed

## Known Risks
- 본 fixture는 원문 audit + 099 fix 이후 actual을 final golden으로 굳혔다. 향후 ISO16358-2 HSPF 계산 path를 수정하면 16-case golden이 재차 흔들릴 수 있으므로, 그런 수정이 들어올 때는 원문 audit 갱신 또는 expected 재정렬을 함께 다뤄야 한다.
- result report lifecycle maintenance pending (active 폴더에 100까지 누적). 별도 정리 작업으로 분리.
