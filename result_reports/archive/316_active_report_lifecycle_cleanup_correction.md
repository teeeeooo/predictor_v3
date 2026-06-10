# Report 316: Active Report Lifecycle Cleanup Correction

## Goal

- 직전의 `ui_tk controller switch` 아크 정리 작업(315) 이후 active 폴더에 유보되었던 leftover active reports를 전면 재검토하여 추가 아카이빙을 완결한다.
- 314 summary 내에 하드코딩되었던 로컬 절대경로 링크들을 repo-relative 상대경로로 일괄 보정한다.
- 315 리포트의 active 유지 목록을 실제와 정치하게 정렬한다.

## Scope

### Inventory Decision (인벤토리 판단 요약)

- **추가 Archive 대상 (총 3개)**:
  - `275_code_quality_guardrail_backlog_registration.md`: backlog가 REFACTOR_PLAN/WORK_PLAN에 완전히 등록되어 종결된 마일스톤이므로 archive.
  - `296_active_report_lifecycle_cleanup.md`: 과거 cleanup 결과보고서로 active 유지 불필요하므로 archive.
  - `297_wording_correction_for_295_summary.md`: exact count 및 Pending final execution 문구를 completed/threshold wording으로 보정한 뒤 archive.
- **Active 유지 대상 (총 4개)**:
  - `262_main-table-migration-candidate-check.md`: 차후 Next Action (Main table migration check)의 preflight.
  - `274_ui_tk_cleanup_preflight.md`: 차후 Next Action (ui_tk folder cleanup)의 preflight.
  - `315_active_report_lifecycle_cleanup_after_controller_switch.md`: 이전 lifecycle cleanup 결과 보고서.
  - `316_active_report_lifecycle_cleanup_correction.md` (본 리포트).

### Included Changes

- `result_reports/summaries/314_summary-tkinter-table-controller-switch-arc-closeout.md` 내 로컬 절대 경로 링크들을 relative path (`../archive/...`)로 치환 완료.
- 3개 active reports (275, 296, 297)를 `result_reports/archive/` 로 git mv 이동 완료.
- `result_reports/active/315_active_report_lifecycle_cleanup_after_controller_switch.md` 의 inventory 목록 및 archive count 보정 완료.
- `docs/WORK_PLAN.md` 및 `project_log.md` 갱신 완료.

### Excluded Scope

- Python source 코드 및 도구 수정 금지.
- 차후 Next Actions와 직접 연결되는 preflight 리포트들 (`262`, `274`)의 아카이브 이동 배제.

## Verification

- `git status --short` 및 `find` 명령어들로 19개 아카이브 파일의 이동 상태 정상 확인.
- `grep -R "file:///Users" ...` 명령어로 로컬 절대경로 링크가 완전히 제거되었음을 확인.
- `python3 -B tools/check_code_structure.py` warnings 4개(기존 warnings)만 노출되며 통과.
- `git diff --check` 통과.
- active report count 검증 완료 (exact count는 final terminal output으로만 출력).

## Reference Evidence Gate & Wording Policy

- **Active Report Count Wording Policy**: 본 리포트를 포함하여 WORK_PLAN.md, project_log.md, summaries 등 모든 영구 보존 문서 내에 exact active report count 대신 `meets lifecycle threshold criteria` 와 같은 threshold wording 정책을 적용함.

## Active Report Count

- active report count meets lifecycle threshold criteria.

## Lifecycle Maintenance Note

- **Completed**: active report 개수가 임계치 이하(criteria 충족)로 정리되어 마일스톤 위생이 최종 정상 상태로 복구됨.

## Next Suggested Action

1. **Main table migration check**
2. **ui_tk folder cleanup**
3. **EN14825 / AHRI 210/240 / KS profile expansion**

## Commit / Push

- Commit command: `git commit -m "docs: Correct active report lifecycle cleanup"` (no-verify 사용 금지)
- Pushed successfully.
