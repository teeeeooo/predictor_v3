# 486 Share Detail Panel Visibility Helper

## Goal

Move repeated section-local detail panel show/hide mechanics into a narrow
section-layer helper while preserving each section's data refresh ownership and
the existing visible-content lifecycle callback path.

## Changed Files

- `apps/calculator/ui/sections/detail_visibility.py`
- `apps/calculator/ui/sections/en14825_seer_section.py`
- `apps/calculator/ui/sections/en14825_scop_section.py`
- `apps/calculator/ui/sections/ahri_seer2_section.py`
- `apps/calculator/ui/sections/ahri_hspf2_section.py`
- `apps/calculator/ui/sections/hong_kong_cspf_section.py`
- `apps/calculator/ui/sections/hong_kong_hspf_section.py`
- `apps/calculator/ui/sections/iso_iseer_2point_section.py`
- `apps/calculator/ui/sections/iso_saso_t3_section.py`
- `tests/test_ui_tk_detail_visibility.py`
- `docs/WORK_PLAN.md`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `result_reports/active/486_share-detail-panel-visibility-helper.md`

## Changes

- Added `DetailPanelVisibility`, a section-layer view helper that owns:
  visible state, `grid`/`grid_remove`, button text, section-supplied grid
  options, optional refresh-before-show callback, and post-change callback.
- Replaced eight repeated `_toggle_detail()` bodies with helper delegation.
- Kept profile-specific detail source refresh in sections through optional
  `before_show` callbacks.
- Kept tab/lifecycle scheduling unchanged: the helper calls the existing
  section callback, which still terminates at the composed
  `ProfileVisibleContentLifecycleController` trigger.
- Added focused helper tests for show/hide button text, grid options, callback
  invocation, and refresh-before-grid ordering.
- Updated `WORK_PLAN.md` to show the approved helper implementation bundle as
  complete pending final validation/push.

## Verification

- `python3 -B -m pytest tests/test_ui_tk_detail_visibility.py tests/test_ui_tk_en14825_seer_detail.py tests/test_ui_tk_en14825_scop_detail.py tests/test_ui_tk_ahri_seer2_detail.py tests/test_ui_tk_ahri_hspf2_detail.py tests/test_ui_tk_hong_kong_hspf_detail.py tests/test_ui_tk_iso_table_autocalc.py tests/test_ui_tk_window_lifecycle_repair.py` — passed, 98 tests.
- `python3 -B -m pytest tests/test_ui_tk_en14825_profile_switch_fit.py -q` — passed, 4 tests.
- `python3 -B tools/code_checker/build_reference_map.py --check` — fresh; generated from the current dirty tree before staging.
- `python3 -B tools/check_code_structure.py` — hard checks passed; existing soft warnings remain.
- Final cached gate and diff check are run at slice closeout.

## Excluded Scope

- No `ProfileVisibleContentLifecycleController`, tab lifecycle, detail payload,
  schema, formatter, geometry cycle, core calculation, public API, fixture, or
  golden behavior changed.
- No base section class or tab-level detail widget manipulation was introduced.

## Reuse / Commonization Decision

Report 479 accepted a section-layer visibility helper and rejected moving
widget show/hide mechanics into the lifecycle controller or a base section
class. This slice implements only that accepted owner. Grid rows and refresh
policies remain section-supplied because they are profile-local layout/data
contracts, while the repeated toggle mechanics are now shared.

## Structure Warning Triage

- EN14825 SEER/SCOP sections remain existing hotspots, but this slice removes
  repeated toggle mechanics rather than adding a new responsibility.
- `apps/calculator/ui/batch/controller.py` keeps the prior class-count soft
  warning from Slice 3; this slice does not touch it.
- Accepted for this slice because the new helper is small and the section
  deltas are wiring-only.

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

- `result_reports/active/479_detail-toggle-lifecycle-boundary-audit.md`:
  accepted owner and guard boundaries, reason: preserve lifecycle/controller
  separation.
- eight `_toggle_detail` ranges in affected sections, reason: migrate only the
  repeated view mechanics.
- focused detail/lifecycle tests, reason: preserve detail source refresh,
  callback/refit trigger, and profile switch behavior.
- broad read: none.
- repeated read: none.

## Next Action

Final validate and push the five-slice calculator helper implementation bundle.
