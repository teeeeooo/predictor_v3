# ISO/ISEER 2-point Batch UseCase Reuse

## Goal
- Remove duplicated ISO/India 2-point calculator orchestration from the batch handler.
- Reuse the Arc 12 ISO/ISEER application usecase while preserving batch output keys and states.

## Scope
- Updated `IsoIseer2PointBatchHandler.calculate_row()` to call `IsoIseer2PointUseCase`.
- Preserved pending, error, and OK behavior.
- Preserved batch output keys: `iso_cspf`, `iso_cstl`, `iso_csec`, `iseer`, `iseer_cstl`, `iseer_csec`.
- Added a source guard proving the batch profile handler no longer imports the core dispatcher or calls `calculate_cspf`.
- Regenerated `docs/code_map/CODEBASE_REFERENCE_MAP.md`.
- Updated `docs/WORK_PLAN.md` next action.

## Non-goals
- No batch table UX, copy/export, matrix spec, formula, config, fixture, golden expected, profile ID, or public result contract changes.
- No other calculator standards changed.

## Verification
- OK: `python3 -B -m pytest tests/test_ui_tk_iso_iseer_2point_batch_dialog.py tests/test_calculator_iso_iseer_2point_usecase.py -q`
- OK: `python3 -B -m py_compile apps/calculator/ui/batch_dialogs/profiles/iso_iseer_2point.py apps/calculator/application/iso_iseer_2point/*.py`
- OK: static source guard found no dispatcher/calculate_cspf references in batch handler.
- OK: `python3 -B -m py_compile app_calculator.py apps/calculator/**/*.py core/calculators/**/*.py`
- OK: `python3 -B -m pytest tests -k "iso_iseer or batch or calculator or cspf"`
- OK after regeneration: `python3 -B tools/code_checker/build_reference_map.py --check`
- OK with pre-existing soft warnings: `python3 -B tools/check_code_structure.py`
- OK: `git diff --check`
- OK: `git status --short`

## Task Results
- task 1: OK - shared evaluator was already available as `IsoIseer2PointUseCase`.
- task 2: OK - batch handler migrated to the usecase.
- task 3: OK - valid, pending, invalid, and source-guard tests updated.

## Changed Files
- `apps/calculator/ui/batch_dialogs/profiles/iso_iseer_2point.py`
- `tests/test_ui_tk_iso_iseer_2point_batch_dialog.py`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `docs/WORK_PLAN.md`
- `result_reports/active/613_iso-iseer-2point-batch-usecase-reuse.md`

## Reference Parity
- Existing reference checked: `IsoIseer2PointUseCase` from Slice 2.
- Reuse decision: reused existing application usecase instead of adding a second batch-local evaluator.
- Generic batch controller/table contract was left unchanged.

## Structure Warnings
- none on changed/new source files.
- Existing soft warnings remain in calculator core/UI hotspot files outside this
  slice's changed source ownership.

## Read Ledger
- `apps/calculator/ui/batch_dialogs/profiles/iso_iseer_2point.py`: lines 1-310, reason: explicit migration target and batch state/output contract.
- `apps/calculator/ui/batch/controller.py`: lines 1-130, reason: generic batch handler protocol/state contract.
- `apps/calculator/ui/batch/models.py`: lines 1-130, reason: `BatchRowState` contract.
- `tests/test_ui_tk_iso_iseer_2point_batch_dialog.py`: lines 1-130, reason: existing batch handler tests.
- `tests/test_ui_tk_batch_dialog_content_sizing.py`: lines 1-130, reason: batch shell safety-floor coverage unchanged.
- broad read: none
- repeated read: none

```yaml
change_gate:
  new_source: none
  hotspot_delta: wiring-only
  code_map_check: regenerated
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
  report_exemption: none
  read_ledger: included
```

## Known Failures / Risks
- Remaining standards still have direct UI calculation orchestration and are follow-up candidates.
- Batch output is mapped from the usecase's profile row shape; future row-shape changes should update this adapter intentionally.

## Next Suggested Action
- Arc 12 Slice 4 - Closeout / Next Extraction Decision.

## Commit / Push
- commit: completed in slice commit; final hash reported in terminal output
- push: deferred until all Arc 12 slices are complete per user request

## Project Memory Delta
- none
