# 291 Close Out Post-Focus-Preservation GUI Smoke

## Goal

Record the iMac GUI smoke results for the 288/289 focus-preservation fix and close out the undo/flicker arc.

## Scope

- docs/WORK_PLAN.md: update current next and next actions.
- project_log.md: record GUI smoke closeout decision.
- result_reports/active/291: this closeout report.

## Excluded Scope

- No code changes.
- No test changes.
- No active report lifecycle cleanup performed (pending separate follow-up).
- No controller switch expansion performed (blocker cleared, but execution pending).

## User GUI Smoke Result

Environment: iMac.

- calculator_tk 실행 OK
- Hong Kong CSPF profile OK
- 숫자 입력 시 ResultPanel flicker 없음
- invalid text 입력 OK
- 오류 summary 표시 OK
- Ctrl+Z undo가 원래 값으로 복원됨
- undo 후 같은 셀에 계속 입력 가능
- paste / clear / numeric undo 유지
- detail open/close 이상 없음
- 다른 profile 전환 후 이상 없음

## Decision

- Post-focus-preservation GUI smoke passed.
- Invalid text undo issue is resolved.
- ResultPanel flicker fix from 286/287 remains stable.
- Controller switch expansion blocker is cleared.

## Remaining Scope

- Controller switch expansion to remaining sections (HongKongHspfSection, IsoIseer2pointSection, SasoT3Section) is ready to proceed.
- Active report lifecycle cleanup is pending as a separate follow-up.

## Active Report Count

Current active report count: **30**.

## Lifecycle Maintenance Note

Active reports exceed the 10-report threshold. Summary/archive maintenance is pending and should be handled as a separate follow-up.

## Next

- Active report lifecycle cleanup follow-up.
- Controller switch expansion readiness.
