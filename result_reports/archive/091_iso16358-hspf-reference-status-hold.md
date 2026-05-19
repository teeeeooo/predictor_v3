# 091 ISO16358-2 HSPF Reference Diagnostic Status — Hold

## Goal
- 083 ISO16358-2 HSPF official exact diagnostic의 현재 분석 상태를 문서에
  정확히 반영한다.
- "official exact"라는 표현을 과신하지 않도록 보정한다.
- repo calculator / fixture / expected / xfail 수정 없이, 이 이슈를 hold
  상태로 분리한다.
- 부분 점검에서 확인된 사실 (reference script 해석 오류 가능성 포함)을
  기록한다.

## Scope
- 수정 파일은 docs/log/brief/이번 report에 한정한다.
- ISO16358-2 HSPF 계산식, fixture, expected, xfail, 테스트 코드는 수정하지
  않는다.
- EN14825, AHRI, UI, adapter, unit conversion, ML/inverse-search 작업과는
  섞지 않는다.

## Non-goals
- ISO16358-2 HSPF mismatch 11개 case의 최종 결론을 내리는 일.
- 083 report 본문을 직접 수정하는 일 (정정/hold 표시는 이 091 report에만
  남긴다).
- external reference script 자체를 수정/재실행하는 일.

## Task 1 Result

### Modified Files
- `docs/WORK_PLAN.md` — ISO16358-2 HSPF mismatch를 hold 상태로 명시하고,
  부분 점검에서 확인된 사실 (bin_hours / HSTL expected / fixture 동일성 /
  `_f` reference point 보존 / case 12·15·16의 external script 해석 오류
  가능성)을 추가했다. ISO mismatch는 immediate next action에서 제외한다.
- `project_brief.md` — 083 expected의 성격이 추가 검토 중이고 ISO16358-2
  HSPF mismatch가 hold 상태임을 짧게 반영했다.
- `project_log.md` — 2026-05-18 entry로 Tried / Result / Failed-Risk /
  Decision / Lesson을 append했다.
- `result_reports/active/091_iso16358-hspf-reference-status-hold.md` —
  이 report.

### 문서에 반영한 판단
- 083 ISO16358-2 HSPF 16-case diagnostic은 historical diagnostic snapshot
  으로 다룬다.
- 083 report 본문은 직접 수정하지 않고, expected의 "official exact" 성격
  보정과 hold 상태는 이 091 report에서 명시한다.
- ISO16358-2 default bin과 total bin hours (2866 h), HSTL expected
  4885.4 kWh, fixture 입력, repo fixture의 `2_full` / `2_half` → `2_full_f`
  / `2_half_f` 매핑, repo calculator의 frost reference point 보존 동작은
  부분 점검에서 정상으로 확인됐다.
- repo calculator는 measured `2_full` / `2_half`를 frost reference point인
  `2_full_f` / `2_half_f`로 보존하고, non-frost `2_full` / `2_half`는 -7~7
  line 계산값으로 유지하는데, 이 방식이 현재 규격 원문 해석상 맞는 것으로
  판단된다.
- external reference script는 measured `2_full`을 `2_full`과 `2_full_f` 양쪽에
  동일하게 넣고 `2_half`도 동일하게 처리한 것으로 확인됐다. 따라서 case
  12 / 15 / 16의 큰 mismatch는 repo calculator bug라기보다 external reference
  script의 해석 오류 가능성이 크다.
- single external reference script 결과를 "official exact" authority로
  굳히지 않는다.

### Hold 상태로 둔 항목
- ISO16358-2 HSPF official exact 16-case mismatch 분석 (나머지 case 포함).
- 083 expected 값의 최종 authority 판정.
- mismatch case에 대한 repo 계산식 변경 여부 결정.
- mismatch case xfail 목록 정리 여부.

### 수정하지 않은 파일과 이유
- `core/calculator_iso16358.py` — ISO16358-2 HSPF 계산식 변경은 명시적
  standard decision이 있을 때만 진행한다. 부분 점검 결과 frost reference
  point 보존 동작은 규격 해석상 맞는 방향으로 판단되어, 현재로서는 수정
  근거가 없다.
- `tests/fixtures/iso16358_hspf_official_exact_cases.json` — fixture
  expected 변경은 hold 대상이다. 사용자 외부 분석 결과 전 임의 수정 금지.
- `tests/test_iso16358_hspf_official_exact_golden.py` — xfail 목록 / 비교
  허용 오차 / case 구성 변경은 hold 대상.
- `result_reports/active/083_iso16358-2-hspf-official-exact-golden-verification.md`
  — 사용자 지시에 따라 원본 report는 보존하고, 정정/hold 표시만 091에 남긴다.

### 다음 repo 작업 순서
1. ISO16358-2 HSPF mismatch는 사용자 외부 분석 결과 대기 (hold).
2. repo 다음 작업은 `docs/WORK_PLAN.md` Near-term execution order의
   EN14825 horizontal table-input slice (Slice C → Slice D), invalid-cell
   visual delegate slice, Tab/Enter navigation 보강 순서로 진행한다.
3. unit adapter 확장과 ML / inverse-search 복귀는 그 뒤 별도 작업으로 다룬다.

## Verification
| command | result |
| --- | --- |
| `python3 -B -m pytest tests/test_iso16358_hspf_official_exact_golden.py -q` | `6 passed, 11 xfailed in 0.06s` |
| `python3 -B -m pytest tests/test_calculator_schema_boundaries.py -q` | `3 passed in 0.05s` |

## Changed Files
- `docs/WORK_PLAN.md`
- `project_brief.md`
- `project_log.md`
- `result_reports/active/091_iso16358-hspf-reference-status-hold.md`

## Known Failures / Risks
- ISO16358-2 HSPF official exact 16-case 중 11개는 strict xfail 상태 그대로
  유지된다. 본 작업은 hold 선언이며 mismatch 자체를 해결하지 않는다.
- 083 report 본문은 그대로 두기 때문에, 향후 081/082 류 summary 작성 시
  083과 091을 함께 묶어 reference 해석 보정을 반영할 필요가 있다.

## Next Suggested Action
- 사용자 외부 분석 결과 도착 시 repo 후속 작업 (계산식 / fixture / xfail /
  expected 변경 여부)을 재평가한다.
- 그 사이 repo 다음 slice는 EN14825 horizontal table-input slice로 시작한다.

## Scope Compliance
- ISO16358-2 HSPF 계산식, fixture, expected, xfail, 테스트 파일은 수정하지
  않았다.
- 083 report 본문은 수정하지 않았다.
- AGENTS_FULL.md, EN14825/AHRI/UI/adapter/ML 작업은 건드리지 않았다.

## Commit / Push
- source change: 본 작업은 문서 + 신규 report만 수정한다. 코드/테스트/
  fixture 변경 없음.
- docs commit과 report commit은 가능하면 분리한다 (`docs:` prefix와
  `report:` prefix).
- push 결과는 최종 터미널 보고에 남긴다.
