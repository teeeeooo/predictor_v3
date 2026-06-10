# Active Report 352: Report 351 Wording and Validation Note Correction

## 목표 (Goal)

* `result_reports/active/351_mixed_iso_table_test_split_or_retirement.md`의 과도한 확정 표현을 evidence-based wording으로 보정한다.
* full pytest 미실행 사유와 후속 슬라이스에서 full pytest가 필요하다는 validation note를 351 report에 추가한다.
* production source, tests, apps, ui, WORK_PLAN, project_log, memory seed는 수정하지 않는다.

## 351 Report Wording Correction

아래 표현을 보정하였다:

| 위치 | 이전 표현 | 보정 후 표현 |
|------|-----------|-------------|
| 이유 섹션 (line 33) | 완벽하게 커버되고 있습니다 | 충분히 보호되는 것으로 판단됩니다 |
| blocker 해제 섹션 (line 47) | 완전히 제거되었습니다 | 제거되었습니다 |
| blocker 해제 섹션 (line 48) | 핵심 blocker가 완전히 해제되었습니다 | 주요 blocker가 해제됨 |
| next action 섹션 (line 71) | Blocker가 완전히 해제되었으므로 | 주요 blocker가 해제된 것으로 판단되므로 |

선택한 Option A (Retire whole mixed test), test retirement 판단 자체, deleted test 목록, retained shared utility coverage 내용은 변경하지 않았다.

## Validation Note Correction

351 report의 `## 검증 결과 (Verification)` 섹션에 아래 note를 추가하였다:

> **Validation note**: Full pytest was not run in this slice; validation was limited to focused shared utility and PyQt environment guard tests. Full pytest should be run in the subsequent PyQt calculator-only source retirement execution slice.

기존 focused test 결과(test_spreadsheet_table_model.py, test_spreadsheet_table_view.py, test_ui_theme_tokens.py, test_pyqt_environment_guard.py)는 그대로 유지하였다. 새로운 테스트 결과를 허위로 추가하지 않았다.

## 변경하지 않은 범위 (Unchanged Scope)

* production Python source 미수정
* tests/ 미수정
* apps/ 미수정
* ui/ 미수정
* docs/WORK_PLAN.md 미수정
* project_log.md 미수정
* result_reports/memory/project_memory_seed.md 미수정
* result_reports/summaries/ 미수정
* result_reports/archive/ 미수정
* docs/architecture/ 미수정
* docs/ui_ux/ 미수정
* AGENT_TASK_ROUTER.md 미수정
* docs/agent_workflows/ 미수정

## 검증 결과 (Verification)

* `git status --short`: 351 report 및 본 352 report 외 diff 없음 확인.
* `grep -n "완벽\|완전히\|completely"` on 351 report: 잔여 과도 표현 없음 확인.
* `grep -n "full pytest\|충분히 보호\|주요 blocker"` on 351 report: 보정 표현 및 validation note 존재 확인.
* `python3 -B tools/check_code_structure.py`: OK (no findings).
* `git diff --check`: whitespace 에러 없음.

## next action (Next Action)

* PyQt calculator-only source retirement execution slice에서 full pytest를 포함한 검증과 함께 레거시 소스 은퇴를 실행한다.
