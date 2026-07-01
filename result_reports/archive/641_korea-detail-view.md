# KOREA Detail View

## Goal

Implement Slice 5 of the KOREA calculator notebook sub-arc: CSPF/HSPF detail
view wiring using official calculation detail rows only.

## Scope

- Added `BinDetailPanel` and `DetailPanelVisibility` wiring to KOREA CSPF and
  HSPF sections.
- CSPF detail uses the cooling/default bin detail schema.
- HSPF detail uses `HEATING_HSPF_BIN_DETAIL_SCHEMA`.
- Added focused contract tests proving KOREA detail rows come from official
  usecase `detail_rows` and do not include midpoint guide keys.

## Non-goals

- No core result dict key additions.
- No formula/config/profile/golden changes.
- No midpoint guide values in detail view.
- No batch framework changes.

## Reference Parity

- Checked the EN14825/AHRI detail design record and existing Hong Kong detail
  wiring.
- Reuse outcome: reused `BinDetailPanel`, `DetailPanelVisibility`, existing
  cooling/heating detail schemas, and lifecycle callbacks. KOREA section-local
  source labels/filenames stay local.

## Verification

- `python3 -B -m pytest -q tests/test_calculator_korea_detail_contract.py tests/test_calculator_korea_cspf_usecase.py tests/test_calculator_korea_hspf_usecase.py`:
  OK, 10 passed.
- `python3 -B -m pytest -q tests/test_apps_calculator_ui_korea_tab.py`: weaker
  verified; 2 skipped because Tk could not open in the headless environment.
- `python3 -B -m compileall -q apps/calculator tests`: OK.
- `python3 -B -m pytest -q tests/test_ui_tk_bin_detail_schema.py tests/test_ui_tk_detail_visibility.py tests/test_ui_tk_result_panel_stable_update.py`:
  OK with headless skips, 9 passed and 30 skipped.
- `python3 -B tools/code_checker/build_reference_map.py`: regenerated
  `docs/code_map/CODEBASE_REFERENCE_MAP.md`.
- `python3 -B tools/check_code_structure.py`: OK with 9 pre-existing soft
  warnings outside the changed source files.
- `git diff --check`: OK.

## Structure Warnings

- No changed/new source file emitted a structure-guard warning.
- `korea_cspf_section.py` and `korea_hspf_section.py` now exceed the 250 LOC
  soft planning threshold after single UI, batch, and detail wiring.
- Warning triage: accepted for this slice because current responsibilities are
  still section-local widget composition and event forwarding; perform a split
  audit before adding more KOREA section responsibilities.

## change_gate

- owner_boundary: KOREA sections own detail toggle/panel composition and use
  official `detail_rows` from application usecases.
- reuse_commonization: `reused-existing-owner`; existing detail panel,
  visibility helper, schema, and lifecycle callback owners were reused.
- code_map_check: `regenerated`; `docs/code_map/CODEBASE_REFERENCE_MAP.md` is
  included in the diff.

## Known Risks

- Tk detail open/close smoke could not run in this headless environment.
- Section files should not receive additional unrelated responsibilities before
  a split audit.

## Commit / Push

- Commit: performed after report finalization; final hash is reported in the
  terminal response.
- Push: not run; push is reserved for final Slice 6 closeout.
