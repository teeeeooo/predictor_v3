# 060 AHRI UI Profile Selector

## Goal

Make the AHRI calculator UI selector use the calculator profile registry instead of showing JSON filenames while ignoring the selected value.

## Scope

- `ui/calc_window.py`
- `tests/test_app_calculator_ui_smoke.py`

## Non-goals

- No EN14825 profile registration.
- No AHRI formula changes.
- No result envelope or ML adapter implementation.

## Changed Files

- `ui/calc_window.py`
- `tests/test_app_calculator_ui_smoke.py`
- `result_reports/active/060_ahri-ui-profile-selector.md`

## Verification

- `python3 -B -m py_compile app_calculator.py ui/calc_window.py core/calculator_profiles.py core/calculator_dispatcher.py`
  - passed
- `QT_QPA_PLATFORM=offscreen python3 -B -m pytest tests/test_app_calculator_ui_smoke.py tests/test_calculator_profiles.py tests/test_calculator_dispatcher.py -q`
  - `32 passed`

## Task Results

- `scan_configs()` now delegates AHRI population to enabled profiles from `list_calculator_profiles()`.
- AHRI combo labels are profile labels, and `profile_id` is stored in combo item data.
- `on_region_changed_ahri()` now resolves the selected `profile_id` through `create_calculator_for_profile()`.
- EN tab JSON scanning is intentionally retained until an EN profile is registered in a separate task.
- UI signal blocking in the AHRI population path uses `try/finally` and explicitly refreshes the selected calculator after population.

## Known Risks

- Only the currently enabled AHRI SEER2 profile is exposed in the AHRI cooling selector. HSPF2 remains loaded separately through `_load_hspf2_calc()`.
- The earlier UI interaction gap remains: no calculate button/result label path was added in this selector cleanup.

## Commit / Push

- Source commit: `0f94441` (`fix: drive AHRI UI selector from calculator profiles`).
- Report commit: this commit (`report: record AHRI UI profile selector cleanup`).
- Push: deferred until final objective push.
