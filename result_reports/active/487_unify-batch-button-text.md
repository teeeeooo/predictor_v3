# 487 Unify Batch Button Text

## Goal

Remove stale section-local detail visibility state left after
`DetailPanelVisibility`, and make all existing batch-open buttons use the same
user-facing label.

## Changed Files

- `apps/calculator/ui/layout_constants.py`
- `apps/calculator/ui/ahri/hspf2_batch_access.py`
- `apps/calculator/ui/sections/en14825_seer_section.py`
- `apps/calculator/ui/sections/en14825_scop_section.py`
- `apps/calculator/ui/sections/ahri_seer2_section.py`
- `apps/calculator/ui/sections/ahri_hspf2_section.py`
- `apps/calculator/ui/sections/hong_kong_cspf_section.py`
- `apps/calculator/ui/sections/hong_kong_hspf_section.py`
- `apps/calculator/ui/sections/iso_iseer_2point_section.py`
- `apps/calculator/ui/sections/iso_saso_t3_section.py`
- `tests/test_ui_tk_iso_table_autocalc.py`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `result_reports/active/487_unify-batch-button-text.md`

## Changes

- Added `BATCH_INPUT_BUTTON_TEXT = "일괄 입력"` in the existing UI layout/token
  owner.
- Replaced existing batch-open button labels with the shared constant:
  EN14825 SEER/SCOP, AHRI SEER2/HSPF2, Hong Kong CSPF, ISO/ISEER 2-point, and
  SASO T3.
- Removed stale `_detail_visible = False` assignments; `DetailPanelVisibility`
  is now the visible state owner.
- Updated the focused Hong Kong layout test to assert the shared batch button
  text.

## Verification

- `python3 -B -m pytest tests/test_ui_tk_detail_visibility.py tests/test_ui_tk_ahri_hspf2_batch.py tests/test_ui_tk_ahri_seer2_batch.py tests/test_ui_tk_en14825_seer_batch_dialog.py tests/test_ui_tk_en14825_scop_batch_dialog.py tests/test_ui_tk_iso_iseer_2point_batch_dialog.py tests/test_ui_tk_saso_t3_batch_dialog.py tests/test_ui_tk_iso_table_autocalc.py` — passed, 91 tests.
- `python3 -B tools/code_checker/build_reference_map.py` — regenerated.
- `python3 -B tools/check_code_structure.py` — hard checks passed; existing soft
  warnings remain.
- `git diff --check` — passed.
- Final cached gate is run at slice closeout.

## Excluded Scope

- No dialog titles, `surface_role`, batch dialog behavior, detail payload,
  schema, core calculation, public API, fixture, or golden behavior changed.
- Hong Kong HSPF batch button creation is intentionally left to Slice 2.

## Reuse / Commonization Decision

The repeated batch-open label is a small UI text token, so it belongs in the
existing UI layout/token owner rather than a new i18n system or helper. Detail
visibility state is not duplicated in sections because `DetailPanelVisibility`
already owns it.

## Structure Warning Triage

- EN14825 SEER/SCOP section size warnings are existing hotspots. This slice
  removes stale state and swaps label tokens only.
- `apps/calculator/ui/batch/controller.py` keeps the prior class-count soft
  warning; this slice does not touch it.

## Change Gate

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

Read Ledger:

- `rg` search for `_detail_visible`, batch button texts, and `Multi 입력`;
  reason: confirm stale state and text drift.
- affected section constructor/button ranges only; reason: keep cleanup scoped.
- focused batch/detail tests; reason: preserve construction and lifecycle
  behavior.
- broad read: none.
- repeated read: none.

## Next Action

Hong Kong HSPF batch implementation using `BatchMatrixCalculationController`
and `BatchDialogHandle`.
