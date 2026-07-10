# Report 336: Active Report Lifecycle Remaining Wording Correction

## Goal (목표)

- summary 334와 active report 335에 기술되었던 "남은 active report 없음" 관련 wording 불일치를 보정하여 실제 상태(cleanup/correction report가 active에 유지되는 상태)와 정확히 일치시킨다.

## Scope (범위)

### 1. Discrepancy (발견된 불일치)
- summary 334 및 report 335에 "남은 active report 없음" 또는 "None"으로 표기되어 있으나, 실제로는 335 cleanup report와 그 이후의 correction report(본 336 report 등)가 active에 유지되고 있어 정정 필요성이 제기됨.

### 2. Summary 334 Wording Correction
- `result_reports/summaries/334_summary-batch-dialog-doc-memory-lifecycle-closeout.md` 내 `Remaining Active Reports` 섹션 문구를 수정하여, 이전 active reports(262~333)는 아카이브되었으나 cleanup evidence 및 summary 334 이후 생성된 리포트들은 coverage 외의 영역으로 active에 남을 수 있음을 명시함.

### 3. Report 335 Wording Correction
- `result_reports/active/335_active_report_lifecycle_cleanup_before_batch_foundation_audit.md` 내 `Remaining Active Reports (유지 대상)` 섹션 문구를 수정하여, 335 cleanup report 자체가 active에 남아 evidence 및 next-action pointer 역할을 수행함을 명시함.

### 4. Unchanged Scope (변경하지 않은 범위)
- 이번 작업은 오직 wording/traceability micro correction이므로, 추가적인 archive 이동, `project_log.md`, `docs/WORK_PLAN.md`, `result_reports/memory/project_memory_seed.md` 파일은 전혀 수정하지 않음 (unchanged).
- codebase reference map, production Python source, tests, ui_tk, calculator/core 등 비즈니스 로직 수정 없음.

## Changed Files (변경 파일)

- `result_reports/summaries/334_summary-batch-dialog-doc-memory-lifecycle-closeout.md`
- `result_reports/active/335_active_report_lifecycle_cleanup_before_batch_foundation_audit.md`
- `result_reports/active/336_active_report_lifecycle_remaining_wording_correction.md` (본 리포트 생성)

## Verification (검증 결과)

- `python3 -B tools/check_code_structure.py` 통과 (OK)
- `git diff --check` 상의 whitespace 문제 없음 (OK)
- `git status --short` 확인 결과 허용된 3개 파일(334 summary, 335 active report, 336 correction report) 외의 diff 없음 확인 (OK)

## Known Risks (알려진 위험)
- 없음. 로직 및 테스트 코드 변경 없이 문서 문구 정정으로만 진행됨.

## Next suggested Action (차기 과제)
1. **Batch foundation foldering audit**
