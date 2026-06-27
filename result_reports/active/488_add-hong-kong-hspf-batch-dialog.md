# 488 Add Hong Kong HSPF Batch Dialog

## Goal

Add a Hong Kong HSPF batch dialog using the existing two-row matrix batch
surface, `BatchMatrixCalculationController`, and `BatchDialogHandle`.

## Changed Files

- `apps/calculator/ui/batch/matrix_models.py`
- `apps/calculator/ui/batch_dialogs/profiles/hong_kong_hspf.py`
- `apps/calculator/ui/sections/hong_kong_hspf_section.py`
- `tests/test_ui_tk_hong_kong_hspf_batch.py`
- `docs/WORK_PLAN.md`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `result_reports/active/488_add-hong-kong-hspf-batch-dialog.md`

## Changes

- Added `HONG_KONG_HSPF_MATRIX_SPEC` with two physical rows per logical case:
  Capacity / Power across `7 Full` and `7 Half`.
- Added Hong Kong HSPF batch handler, section, adapter, and dialog wrapper.
- Handler reuses the existing `build_hspf_input`,
  `resolve_profile_id(region_label, "HSPF")`, and `calculate_hspf()` flow.
- Batch results expose the same minimum summary family as the main HSPF result:
  `HSPF`, `HSTL`, and `HSEC`.
- Added an `일괄 입력` button and `BatchDialogHandle` wiring to
  `HongKongHspfSection`, including snapshot restoration, duplicate dialog
  focus, close callback, and parent destroy disposal.
- Added focused tests for matrix spec, handler valid/blank/invalid cases,
  matrix controller behavior, and dialog snapshot reopen behavior.
- Updated `WORK_PLAN.md` to reflect this slice as complete pending final
  validation/push.

## Verification

- `python3 -B -m pytest tests/test_ui_tk_hong_kong_hspf_batch.py -q` — passed,
  5 tests.
- `python3 -B -m pytest tests/test_ui_tk_hong_kong_hspf_batch.py tests/test_ui_tk_hong_kong_cspf_matrix_migration.py tests/test_ui_tk_iso_iseer_2point_batch_dialog.py tests/test_ui_tk_saso_t3_batch_dialog.py tests/test_ui_tk_iso_table_autocalc.py -q` — passed, 82 tests.
- `python3 -B tools/check_code_structure.py` — hard checks passed; existing
  soft warnings remain.
- `python3 -B tools/code_checker/build_reference_map.py` — regenerated.
- `git diff --check` — passed.
- Final cached gate is run at slice closeout.

## Excluded Scope

- No HSPF calculation formula, core logic, schema, public API, fixture, golden,
  CSPF batch behavior, dialog shell, lifecycle primitive, or broad batch
  abstraction changed.
- CSPF and HSPF handlers remain profile-local; no mega-handler was introduced.

## Reuse / Commonization Decision

The slice reuses the existing shared matrix controller and dialog handle because
the Hong Kong HSPF surface matches the established BatchMatrixSpec pattern.
The HSPF input/result mapping remains profile-local in
`batch_dialogs/profiles/hong_kong_hspf.py` because it calls the HSPF-specific
core path and result summary contract. The matrix spec belongs beside the
existing Hong Kong CSPF matrix spec in `batch/matrix_models.py`.

## Structure Warning Triage

- `apps/calculator/ui/batch_dialogs/profiles/hong_kong_hspf.py` follows the
  existing profile adapter pattern and keeps handler, section, adapter, and
  dialog together like sibling batch profile files.
- `apps/calculator/ui/batch/controller.py` keeps the prior class-count soft
  warning; this slice reuses it without modification.
- EN14825 section soft warnings remain unrelated.

## Change Gate

```yaml
change_gate:
  new_source: small
  hotspot_delta: accepted-for-slice
  code_map_check: regenerated
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
  report_exemption: none
  read_ledger: included
```

Read Ledger:

- Hong Kong CSPF batch profile, matrix spec, and matrix controller ranges;
  reason: mirror the established two-row batch pattern.
- Hong Kong HSPF section input/result ranges; reason: connect the same
  `build_hspf_input` and result summary contract.
- focused Hong Kong CSPF/ISO/SASO matrix tests; reason: preserve sibling matrix
  behavior while adding HSPF.
- broad read: none.
- repeated read: none.

## Next Action

Hong Kong HSPF batch visual smoke, then select the next approved calculator
detail/manual-smoke or empty-state slice.
