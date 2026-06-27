# 485 Add Batch Dialog Handle

## Goal

Move repeated batch dialog reference, snapshot, open/focus, clear, and dispose
state into a small handle while leaving dialog construction and snapshot schema
with each section/profile owner.

## Changed Files

- `apps/calculator/ui/batch_dialogs/dialog_handle.py`
- `apps/calculator/ui/sections/en14825_seer_section.py`
- `apps/calculator/ui/sections/en14825_scop_section.py`
- `apps/calculator/ui/sections/ahri_seer2_section.py`
- `apps/calculator/ui/sections/hong_kong_cspf_section.py`
- `apps/calculator/ui/sections/iso_iseer_2point_section.py`
- `apps/calculator/ui/sections/iso_saso_t3_section.py`
- `apps/calculator/ui/ahri/hspf2_batch_access.py`
- `tests/test_ui_tk_batch_dialog_handle.py`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `result_reports/active/485_add-batch-dialog-handle.md`

## Changes

- Added `BatchDialogHandle` with `dialog`, `snapshot`,
  `open_or_focus(factory)`, `clear(snapshot)`, and `dispose()`.
- Standardized liveness on `dialog.window.winfo_exists()` with stale-window
  reopen behavior.
- Migrated six parent sections and AHRI HSPF2 batch access to the handle.
- Kept factory closures in each section so constructor differences remain
  profile-owned.
- Preserved existing private test surfaces through thin proxy properties for
  `_batch_dialog` and `_batch_snapshot`.
- Added focused handle tests for live focus, externally destroyed dialogs,
  non-`None` snapshot retention, and dispose close/clear behavior.

## Verification

- `python3 -B -m pytest tests/test_ui_tk_batch_dialog_handle.py tests/test_ui_tk_ahri_hspf2_batch.py tests/test_ui_tk_ahri_seer2_batch.py tests/test_apps_calculator_ui_en14825_batch.py tests/test_ui_tk_en14825_seer_batch_dialog.py tests/test_ui_tk_en14825_scop_batch_dialog.py tests/test_ui_tk_iso_iseer_2point_batch_dialog.py tests/test_ui_tk_saso_t3_batch_dialog.py tests/test_ui_tk_iso_table_autocalc.py` — passed, 108 tests.
- `python3 -B tools/code_checker/build_reference_map.py` — regenerated.
- `python3 -B tools/code_checker/build_reference_map.py --check` — fresh.
- `python3 -B tools/check_code_structure.py` — passed hard rules; existing EN
  hotspot warnings and the prior batch controller class-count soft warning
  remain.
- Final cached gate and diff check are run at slice closeout.

## Excluded Scope

- No button creation, layout row, dialog constructor, snapshot schema, tab
  lifecycle, lifecycle primitive, core calculation, public API, fixture, or
  golden behavior changed.
- No generic dialog manager was introduced.

## Reuse / Commonization Decision

Report 478 accepted a narrow state handle and rejected moving construction,
buttons, or layout into a generic manager. This slice implements only that
state handle and reuses profile factory closures for constructor differences.
Snapshot `None` retention remains explicit through the handle policy.

## Structure Warning Triage

- EN14825 SEER/SCOP sections remain existing hotspots and gained only proxy
  properties plus handle wiring to preserve private test compatibility.
- `apps/calculator/ui/batch/controller.py` still has the prior class-count soft
  warning from Slice 3; this slice does not modify it.
- Accepted for this slice because state mechanics moved out of sections and no
  new section responsibility was added.

## Change Gate

```yaml
change_gate:
  new_source: small
  hotspot_delta: wiring-only
  code_map_check: regenerated
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
  report_exemption: none
  read_ledger: included
```

Read Ledger:

- `result_reports/active/478_batch-dialog-handle-audit.md`: accepted boundary,
  reason: preserve handle-only implementation.
- repeated `_open_batch_dialog`, `_clear_batch_dialog`, and dispose ranges in
  six sections plus AHRI HSPF2 access, reason: migrate only dialog state.
- focused lifecycle/persistence tests, reason: preserve duplicate prevention,
  snapshot restoration, close ordering, and parent destroy behavior.
- broad read: none.
- repeated read: none.

## Next Action

Detail toggle section-layer helper implementation.
