# Active Report 347: Active Report Lifecycle Cleanup after Apps Calculator Relocation

## 목표 (Goal)

본 보고서의 목적은 `result_reports/active/`에 등록된 335번부터 345번까지의 완료된 active report들을 종합 및 archive하여, active report 개수를 lifecycle threshold 이하로 안정화하는 것이다.

## Inventory 결과

- **대상 active report**:
  - `335_active_report_lifecycle_cleanup_before_batch_foundation_audit.md`
  - `336_active_report_lifecycle_remaining_wording_correction.md`
  - `337_batch_foundation_foldering_audit.md`
  - `338_batch_foundation_foldering_slice_1_models.md`
  - `339_338_report_reference_link_typo_correction.md`
  - `340_batch_foundation_foldering_slice_2_views_controllers.md`
  - `341_align_post_batch_foldering_next_action.md`
  - `342_calculator_first_apps_package_architecture_audit.md`
  - `343_charter_architecture_policy_alignment.md`
  - `344_apps_calculator_skeleton_entrypoint_handover.md`
  - `345_relocate_ui_tk_to_apps_calculator_ui.md`
- **분류**:
  - **Archive Candidate**: 335 ~ 345 (모두 완료되어 summaries/346으로 커버됨)
  - **Remaining Active**: 본 보고서 (347) 단 1개만 active로 유지

## Summary 생성 결과

- **생성된 summary**: `result_reports/summaries/346_summary-batch-foundation-apps-calculator-relocation-closeout.md`
- **내용 요약**:
  - Batch foundation foldering arc 정리 (ui_tk/batch/ 이주 완료)
  - Apps package architecture alignment 및 policy synchronization 정리
  - Calculator entrypoint handover 및 UI relocation 정리 (apps/calculator/ui/ 이주 완료)

## Archived Reports 목록

- `result_reports/archive/335_active_report_lifecycle_cleanup_before_batch_foundation_audit.md`
- `result_reports/archive/336_active_report_lifecycle_remaining_wording_correction.md`
- `result_reports/archive/337_batch_foundation_foldering_audit.md`
- `result_reports/archive/338_batch_foundation_foldering_slice_1_models.md`
- `result_reports/archive/339_338_report_reference_link_typo_correction.md`
- `result_reports/archive/340_batch_foundation_foldering_slice_2_views_controllers.md`
- `result_reports/archive/341_align_post_batch_foldering_next_action.md`
- `result_reports/archive/342_calculator_first_apps_package_architecture_audit.md`
- `result_reports/archive/343_charter_architecture_policy_alignment.md`
- `result_reports/archive/344_apps_calculator_skeleton_entrypoint_handover.md`
- `result_reports/archive/345_relocate_ui_tk_to_apps_calculator_ui.md`

## Remaining Active Reports 목록

- `result_reports/active/347_active_report_lifecycle_cleanup_after_apps_calculator_relocation.md`

## WORK_PLAN 업데이트 내용

- `docs/WORK_PLAN.md`에 lifecycle cleanup 완료 사항을 반영하였고, 이주 및 정리 arc의 개별 체크포인트를 `[Summary 346](result_reports/summaries/346_summary-batch-foundation-apps-calculator-relocation-closeout.md)`으로 치환하였습니다.
- 차기 최우선 과제로 "Calculator PyQt reference retirement preflight"를 1순위에 등록하였습니다.

## Project Log / Memory Seed Unchanged

- 본 작업은 단순 문서 정리 및 active report lifecycle 정리 성격이므로, `project_log.md` 및 `result_reports/memory/project_memory_seed.md`는 수정하지 않고 보존하였습니다.

## 제외 범위 (Non-goals)

- Python 프로덕션 소스 코드 및 테스트 코드는 절대 수정하지 않았습니다.
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`, `PROJECT_CHARTER.md`, `docs/architecture/` 등 핵심 아키텍처 및 맵 문서는 본 작업에서 제외되었습니다.

## 검증 결과 (Verification Results)

- `python3 -B tools/check_code_structure.py` 검사 수행 완료
- `git diff --check` 검사 수행 완료
- active report lifecycle count 상태 확인 완료

## Next Action (차기 계획)

1. **Calculator PyQt reference retirement preflight**:
   - `apps/calculator`로의 Tkinter 이주가 완성됨에 따라 legacy PyQt 기반 계산기 UI 코드(`ui/calc_window.py` 등)의 안전한 은퇴 가능 여부를 preflight 진단합니다.

## Lifecycle Wording

- active report count is below lifecycle threshold
