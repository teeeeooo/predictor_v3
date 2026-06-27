# 484 Add Batch Matrix Calculation Controller

## Goal

Move the repeated two-row matrix recalculation loop for Hong Kong CSPF,
ISO/India ISEER 2-point, and SASO T3 into a matrix-specific controller while
keeping case-table and matrix-table controllers separate.

## Changed Files

- `apps/calculator/ui/batch/controller.py`
- `apps/calculator/ui/batch_dialogs/profiles/hong_kong_cspf.py`
- `apps/calculator/ui/batch_dialogs/profiles/iso_iseer_2point.py`
- `apps/calculator/ui/batch_dialogs/profiles/saso_t3.py`
- `tests/test_ui_tk_hong_kong_cspf_matrix_migration.py`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `result_reports/active/484_add-batch-matrix-calculation-controller.md`

## Changes

- Added `BatchMatrixCalculationController` as a sibling to the existing
  `BatchCalculationController`.
- Reused `BatchCalculationSummary` for matrix valid/blank/error counts.
- Replaced three profile-local matrix controller classes with the common matrix
  controller.
- Preserved each profile's handler calculation logic, result values, status
  formatting, table shape, snapshot behavior, and auto-calc scheduling.
- Updated the Hong Kong headless matrix controller test to import the common
  controller.

## Verification

- `python3 -B -m pytest tests/test_ui_tk_hong_kong_cspf_matrix_migration.py tests/test_ui_tk_iso_iseer_2point_batch_dialog.py tests/test_ui_tk_saso_t3_batch_dialog.py` — passed, 23 tests.
- A broader matrix/main-controller superset was tried and produced two stale
  empty-state expectation failures in main ISO/SASO controller-switch undo
  tests expecting old default values `3600`/`5000`; those are outside the batch
  matrix controller path and were not used as slice acceptance.
- `python3 -B tools/code_checker/build_reference_map.py` — regenerated.
- `python3 -B tools/code_checker/build_reference_map.py --check` — fresh.
- `python3 -B tools/check_code_structure.py` — passed hard rules; existing EN
  hotspot warnings remain and `batch/controller.py` now emits a class-count
  soft warning.
- Final cached gate and diff check are run at slice closeout.

## Excluded Scope

- No case-table migration or conditional mega-controller was introduced.
- No handler commonization, schema/result/table shape, core calculation,
  fixture, golden, or public API changed.
- No unrelated UI layout, status text, or snapshot behavior changed.

## Reuse / Commonization Decision

Report 477 accepted a matrix-specific controller and rejected merging case and
matrix controller shapes. This slice reuses the existing batch controller owner
and `BatchCalculationSummary`, while retaining profile-local handlers. The
matrix loop was commonized because all three sibling matrix surfaces shared the
same cases/set_result/count policy.

## Structure Warning Triage

- `apps/calculator/ui/batch/controller.py` now defines six top-level classes,
  one over the soft limit.
- Accepted for this slice: the added class is a cohesive sibling controller in
  the existing controller owner, and splitting it into a new module would create
  more surface than this bounded commonization needs.
- Next action is not another batch controller expansion; revisit only if a new
  matrix/case controller responsibility is added.

## Change Gate

```yaml
change_gate:
  new_source: none
  hotspot_delta: none
  code_map_check: regenerated
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
  report_exemption: none
  read_ledger: included
```

Read Ledger:

- `result_reports/active/477_batch-matrix-controller-audit.md`: decision and
  implementation boundary, reason: preserve accepted matrix-only scope.
- `apps/calculator/ui/batch/controller.py`: existing controller and summary
  owner, reason: add sibling matrix controller without merging case-table path.
- three matrix batch profiles: local controller ranges, reason: replace repeated
  loop only.
- focused matrix tests: controller and dialog tests, reason: preserve result,
  blank, error, and shape contracts.
- broad read: none.
- repeated read: none.

## Next Action

Batch dialog handle implementation.
