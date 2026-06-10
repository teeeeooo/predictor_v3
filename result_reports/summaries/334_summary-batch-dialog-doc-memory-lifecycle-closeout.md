# Summary 334: Batch Dialog, Table Controller Retirement, and Log/Memory Lifecycle Closeout

## Executive Summary

본 요약본은 legacy `ExcelLikeTableController` 제거 및 `TkTableController` 수렴, `BatchDialogShell` + `profiles/` 구조 기반의 배치 입력 확장(ISO 2-point, SASO T3), `project_log.md` 및 `project_memory_seed.md` 정기 유지보수 활동에 이르는 대규모 개발/문서화 주기(active reports 262~333)를 마감하는 최종 요약서이다.

## Summary Coverage (대상 범위)

본 요약본은 아래의 active reports(총 21개)를 커버하고 아카이빙한다:

- [262_main-table-migration-candidate-check.md](../archive/262_main-table-migration-candidate-check.md)
- [274_ui_tk_cleanup_preflight.md](../archive/274_ui_tk_cleanup_preflight.md)
- [315_active_report_lifecycle_cleanup_after_controller_switch.md](../archive/315_active_report_lifecycle_cleanup_after_controller_switch.md)
- [316_active_report_lifecycle_cleanup_correction.md](../archive/316_active_report_lifecycle_cleanup_correction.md)
- [317_main_table_migration_check_after_controller_switch.md](../archive/317_main_table_migration_check_after_controller_switch.md)
- [318_retire_excel_like_table_controller.md](../archive/318_retire_excel_like_table_controller.md)
- [319_ui_tk_batch_dialog_folder_boundary_audit.md](../archive/319_ui_tk_batch_dialog_folder_boundary_audit.md)
- [320_batch_dialog_shell_profiles_boundary_correction.md](../archive/320_batch_dialog_shell_profiles_boundary_correction.md)
- [321_batch_dialog_shell_profiles_skeleton_hk_cspf_relocation.md](../archive/321_batch_dialog_shell_profiles_skeleton_hk_cspf_relocation.md)
- [322_batch_dialog_relocation_smoke_closeout_private_access.md](../archive/322_batch_dialog_relocation_smoke_closeout_private_access.md)
- [323_remove_private_shell_access_from_batch_dialog_test.md](../archive/323_remove_private_shell_access_from_batch_dialog_test.md)
- [324_iso_iseer_2point_batch_dialog_implementation.md](../archive/324_iso_iseer_2point_batch_dialog_implementation.md)
- [325_iso_iseer_2point_batch_dialog_report_closeout_correction.md](../archive/325_iso_iseer_2point_batch_dialog_report_closeout_correction.md)
- [326_saso_t3_batch_dialog_implementation.md](../archive/326_saso_t3_batch_dialog_implementation.md)
- [327_saso_t3_batch_optional_validation_header_correction.md](../archive/327_saso_t3_batch_optional_validation_header_correction.md)
- [328_compact_project_log_batch_dialog_arc.md](../archive/328_compact_project_log_batch_dialog_arc.md)
- [329_project_log_lifecycle_strategy_audit.md](../archive/329_project_log_lifecycle_strategy_audit.md)
- [330_project_log_2026_06_archive_segment_cleanup.md](../archive/330_project_log_2026_06_archive_segment_cleanup.md)
- [331_memory_seed_maintenance_audit.md](../archive/331_memory_seed_maintenance_audit.md)
- [332_memory_seed_maintenance_execution.md](../archive/332_memory_seed_maintenance_execution.md)
- [333_memory_seed_source_reference_correction.md](../archive/333_memory_seed_source_reference_correction.md)

## Key Achievements (주요 완료 내용)

### 1. Main Table Controller Retirement & Convergence (262, 274, 317, 318)
- **ExcelLikeTableController Retirement**: 모든 main calculator section의 메인 테이블이 `TkTableController`로 스위치 완료됨에 따라 사용되지 않는 legacy `ExcelLikeTableController` 코드를 안전하게 삭제 완료.
- **Test Gap Resolution**: legacy controller를 호출하던 unit test 단언문을 `TkTableController` 기준으로 전면 교정하고, interactive behaviors (paste, undo, navigation, selection) Focused test를 추가 보강하여 test gap 해소.
- **MetricInputTable Compatibility**: `TkTableSurface` 어댑터 인터페이스 안정성을 확인하고 visual invalid marking 및 positivity check의 calculator 위임 구조 종결.

### 2. Batch Dialog Composition Architecture & Profile Expansion (319~327)
- **Shell + Profiles Separation**: Toplevel GUI lifecycle, hidden-first geometry settle, close callback, snapshot handoff 책임을 공통 `BatchDialogShell` (in `shell.py`)로 격리하고, 프로필별 특화 spec/calculators는 `profiles/` 아래 thin adapter 객체로 위상 분리.
- **Profile Relocation & Implementation**:
  - 기존 Hong Kong CSPF batch dialog를 `batch_dialogs/profiles/hong_kong_cspf.py`로 안정적으로 이주.
  - ISO / India ISEER 2-point batch dialog 및 SASO T3 batch dialog 신규 구현 및 integration 완료.
  - SASO T3의 필수 6개 필드 및 선택 35 Min 2개 필드 validation logic 교정 (partial validation error 강화) 및 4pt/3pt header ordering 직관성 보정.
- **Encapsulation & Shell Unit Testing**:
  - 통합 테스트 내 dialog private 멤버(`_shell`) 직접 접근을 제거하고 public delegation 메서드(`first_dialog.snapshot()`)로 교정.
  - `BatchDialogShell` 자체의 flow를 검증하는 mock 기반 unit test 추가.

### 3. Log & Memory Seed Maintenance Lifecycle (328~333)
- **Project Log Compacting**: `project_log.md` 내 중복 누적된 task-level heading들을 milestone 단위로 통합 및 compact화.
- **Historical Log Archiving**: `project_log.md`가 비대해짐에 따라 2026-06 이전 historical entries를 `docs/archive/project_log/2026-06/` 아래 read-only segment로 이주 및 분리.
- **Memory Seed Maintenance**: staging memory seed (`project_memory_seed.md`)의 stale/superseded entries 청소, assertionStatus 검토 및 trace source reference 정보 정정 완료.

## Memory Seed Sync Judgment
- 본 summary 정리로 인해 staging memory seed 에 반영이 필요한 추가적인 decisions, procedures 변경사항은 없으며, memory seed의 상태는 **no update** (수정 없음)으로 종결한다. (실제 memory seed 파일은 이번 태스크에서 수정하지 않음)

## Remaining Active Reports
- **None**: 완료된 21개 active reports가 모두 본 summary에 수렴되어 archive로 이주하므로, active 폴더 하위에 남은 보고서는 없습니다.

## Excluded Scope
- production calculator core logic / model predictor / config / tests logic 등 code behavior 변경 없음.
- `project_log.md` 및 `project_memory_seed.md`에 대한 직접적인 수정은 이전 lifecycle slice에서 이미 별도로 수행되었으므로 본 작업에서는 수행하지 않음.

## Next Action Suggestion
1. **Batch foundation foldering audit**: `ui_tk/` root에 잔존하는 batch table foundation 파일들의 적합한 foldering 구조 정립.

---
*Note: active report count meets lifecycle threshold after cleanup.*
