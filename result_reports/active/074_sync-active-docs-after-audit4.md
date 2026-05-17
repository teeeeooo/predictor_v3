# 074 Sync active docs after audit 4

## Goal

audit_5 task 1: audit_4 completion 시점과 실제 active 문서 상태가 어긋난 부분을
동기화한다. `project_log.md`에 audit_4 completion entry를 추가하고,
`docs/WORK_PLAN.md`의 next-action을 다음 envelope step으로 갱신하고,
`project_brief.md`에 EN SCOP UI 연결과 envelope adapter slice 완료 상태를
반영한다.

## Scope

- `project_log.md` (audit_4 completion entry append)
- `docs/WORK_PLAN.md` (current milestone focus + near-term execution order)
- `project_brief.md` (Calculator UI / ML adapter 경계 문장)

## Non-goals

- 코드/테스트 수정 (이번 task는 docs-only)
- adapter schema 변경 (audit_5 task 2의 범위)
- UI 수정 (audit_5 task 4/6의 범위)
- `docs/REFACTOR_PLAN.md` 수정 — 후보/분리 전략에 실제 변경 없음

## Verification

- `git diff --stat` → 3 files changed, +44/-4. report-only docs로 코드 영향
  없음.
- 변경 후 `python3 -B -m pytest -q` 재실행 불필요 (docs only). 직전
  audit_4 검증 결과 (`312 passed, 23 xfailed`)가 그대로 유효.

## Task Results

- task 1: OK
  - `project_log.md` 앞쪽에 `2026-05-17 — Audit 4 next actions completion
    (069 ~ 073)` block 추가. Result/Decision/Verification 3 섹션으로 정리하고
    source/report commit 해시를 명시.
  - `docs/WORK_PLAN.md`:
    - Current milestone focus에 EN14825 SCOP UI wiring, AHRI SEER2 envelope
      first slice, schema boundary guard 강화 상태를 추가.
    - Near-term execution order의 3번을 design doc 정렬 → PredictedPoints →
      ranking smoke → ML caller 순으로 갱신. EN14825 SEER profile/UI follow-up을
      4번으로 추가. 기존 5번/Z-phase는 유지.
  - `project_brief.md`의 Calculator UI / ML adapter 문장을 envelope adapter
    slice + schema guard 적용 상태로 갱신.

## Test Results

- 본 작업은 docs-only이므로 새 테스트 실행 결과 없음.

## Changed Files

- `project_log.md`
- `docs/WORK_PLAN.md`
- `project_brief.md`

## Known Failures / Risks

- audit_5 task 2 (schema 정합성 고정)와 task 3 (PredictedPointsEnvelope)가
  완료된 뒤 본 next-action 목록을 다시 한 번 갱신해야 한다. 현재 문서는 그
  단계가 끝나기 전 시점에서 작성됨.
- `docs/REFACTOR_PLAN.md`는 본 작업에서 건드리지 않았다. 분리 전략에 변경이
  없기 때문이며, 만약 envelope shape이 design doc과 정렬되면서 가드 정책이
  바뀌면 다음 task에서 함께 검토한다.

## Next Suggested Action

- audit_5 task 2: CalculatorInputEnvelope schema 정합성을 design doc과 정렬.

## Scope Compliance

- 코드/테스트 미수정.
- adapter schema/region config 미수정.
- audit_5 task 1의 “수정 대상”인 3개 문서만 변경.

## Commit / Push

- Source commit: `3acc966` (docs: sync active docs to audit_4 completion
  state).
- Report commit: 본 보고서를 별도 커밋으로 추가 예정.
- push는 본 작업 scope 밖.
