# 407 EN14825 SEER batch headless foundation

## Goal

Implement the first EN14825 batch slice as a headless tested-only SEER matrix
specification and row handler without adding dialog or section UI.

## Scope

- Added `apps/calculator/ui/en14825/seer_batch.py`.
- Added `EN14825_SEER_BATCH_SPEC` using the existing two-row
  `BatchMatrixSpec` foundation.
- Added typed common inputs and an adapter-injected
  `En14825SeerBatchHandler`.
- Added focused headless tests in
  `tests/test_apps_calculator_ui_en14825_batch.py`.
- Updated WORK_PLAN and regenerated the codebase reference map.

## Public Contract

- `EN14825_SEER_BATCH_SPEC`
- `En14825SeerBatchCommonInputs`
- `En14825SeerBatchHandler`
- `En14825SeerBatchResult`

The new module is imported directly from the EN14825 feature package path. The
package-level `__init__.py` export surface was not expanded.

## Matrix Contract

- Two physical rows per logical case: Capacity and Power.
- `Pdesignc` is editable only on the Capacity row.
- A/B/C/D each expose tested capacity and tested power inputs.
- Result cells are first-row-only and read-only.
- Result keys are `seer` and `qc_kwh`; status, total kWh, declared values, and
  comparison percentage are excluded.

## Handler Behavior

- Fully blank required input returns `BatchRowState.PENDING`.
- Partial, nonnumeric, adapter-failed, incomplete, or missing-result input
  returns `BatchRowState.ERROR` with blank result cells.
- Complete input builds tested-only `SeerPointInput` objects and calls the
  existing `SeerAdapter.calculate(...)` path.
- Output formatting follows the single-case surface: SEER to two decimals and
  QC to one decimal.
- Common values are typed and supplied to the handler; UI parsing/ownership is
  deferred to the dialog slice.

## Non-goals

- No section, dialog, Toplevel, copy/export, or snapshot wiring.
- No SCOP batch implementation.
- No core, config, calculator API, result schema, golden, or single-case
  behavior changes.
- No package-wide batch foundation refactor.

## Tests

- Matrix shape, input/result keys, physical row mapping, and cell roles.
- Tested-only adapter payload and common input forwarding.
- PENDING/ERROR/OK state behavior and blank results on failure.
- Output formatting.
- Real `SeerAdapter` plus unified config integration without adding golden
  expected values.

## code_map_check

- Targeted pre-edit check covered EN14825 adapter ownership, batch matrix
  symbols, handler/result patterns, and feature-package references.
- Regenerated `docs/code_map/CODEBASE_REFERENCE_MAP.md` because a new source
  module and symbols were added.

## Verification

- `python3 -B -m py_compile apps/calculator/ui/en14825/seer_batch.py tests/test_apps_calculator_ui_en14825_batch.py`
  OK.
- `python3 -B -m pytest tests/test_apps_calculator_ui_en14825_batch.py` OK:
  8 passed.
- `python3 -B tools/check_code_structure.py` completed with existing EN14825
  SEER/SCOP section LOC soft warnings only; the new module remains below source
  soft limits.
- `python3 -B tools/code_checker/build_reference_map.py --check` reports FRESH.
- `git diff --check` OK.
- `git status --short` reviewed before commit.

## Project Memory Delta

- none.

## Next Action

EN14825 SCOP batch headless spec/handler foundation.
