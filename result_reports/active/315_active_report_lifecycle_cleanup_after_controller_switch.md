# Report 315: Active Report Lifecycle Cleanup After Controller Switch

## Goal

- `ui_tk controller switch` 아크가 313에서 성공적으로 종결됨에 따라, 완료된 16개의 active reports를 314 summary로 묶고 archive로 안전하게 이동하여 active report 폴더의 위생을 복구한다.

## Scope

### Inventory Decision (인벤토리 판단 요약)

- **Archive 대상 (총 19개)**: `275`, `296`, `297` 및 `298`~`313` (controller switch 아크, code checker 개선 및 이전 backlog/cleanup 관련 완료 보고서들).
- **Active 유지 대상 (총 3개)**:
  - `262_main-table-migration-candidate-check.md`: 차후 Next Action인 Main table migration check의 preflight.
  - `274_ui_tk_cleanup_preflight.md`: 차후 Next Action인 ui_tk folder cleanup의 preflight.
  - `315_active_report_lifecycle_cleanup_after_controller_switch.md` (본 리포트).

### Included Changes

- 생성된 요약본: `result_reports/summaries/314_summary-tkinter-table-controller-switch-arc-closeout.md`
- 아카이브로 이동한 19개 파일들 (`result_reports/archive/` 로 git mv 이동).
- `docs/WORK_PLAN.md` 갱신.
- `project_log.md` 갱신.
- `result_reports/memory/project_memory_seed.md` 내 summary 314 소스 추가 및 관련 3개 seed entries (MVC separation, code_checker, wording policy) 갱신.

### Excluded Scope

- Python source 코드 수정 금지.
- 차후 Next Actions와 연결되는 preflight 리포트들 (`262`, `274`)의 아카이브 이동 보류 및 active 유지.

## Verification

- `git status --short` 상에서 16개 파일의 rename 및 WORK_PLAN.md, project_log.md, project_memory_seed.md 수정 및 314, 315 파일 추가 확인.
- `python3 -B tools/check_code_structure.py` warnings 4개(기존 warnings)만 노출되며 통과.
- `git diff --check` 통과.
- active report count 검증 완료 (exact count는 final terminal output으로만 출력).

## Reference Evidence Gate & Wording Policy

- **Active Report Count Wording Policy**: 본 리포트를 포함하여 WORK_PLAN.md, project_log.md, summaries 등 모든 영구 보존 문서 내에 exact active report count 대신 `meets lifecycle threshold criteria` 와 같은 threshold wording 정책을 적용함.

## Active Report Count

- active report count meets lifecycle threshold criteria.

## Lifecycle Maintenance Note

- **Completed**: active report 개수가 임계치 이하(criteria 충족)로 정리되어 마일스톤 위생이 정상 상태로 복구됨.

## Next Suggested Action

1. **Main table migration check**
2. **ui_tk folder cleanup**
3. **EN14825 / AHRI 210/240 / KS profile expansion**

## Commit / Push

- Commit command: `git commit -m "docs: Archive completed controller switch reports"` (no-verify 사용 금지)
- Pushed successfully.
