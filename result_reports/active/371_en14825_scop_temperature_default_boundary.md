# 371. EN14825 SCOP Temperature Default Boundary Correction

This report summarizes the correction of the default temperature boundary mapping between the SCOP adapter layer and the core calculator engine.

## Goal
Ensure that the default TOL and Tbiv temperature fallback values resolved at the adapter layer match the values passed to the core calculator, preventing discrepancy when user overrides are omitted.

## Cause
Previously, `ScopAdapter` used `CLIMATE_DEFAULTS` to evaluate the validation constraint (`TOL <= Tbiv`) in the adapter but passed the original inputs (`tbiv_temp_c` and `tol_temp_c` which are `None` when omitted) to `calculate_scop()`. This allowed the core calculator to resolve temperature fallbacks from config-level limits (`tbiv_max_c`, `tol_max_c`), causing a mismatch between the validation baseline and actual core execution defaults.

## Scope
* Implemented `resolve_temperature_overrides()` helper method in `ScopAdapter`.
* Updated `calculate()` in `ScopAdapter` to pass resolved effective temperature values (`eff_tbiv`, `eff_tol`) to both validation checks and both core calculator invocation paths (Declared and Tested).
* Updated unit test suite `tests/test_apps_calculator_ui_en14825_scop.py` with 5 focused test cases.

## Non-goals
* No changes to core calculator logic or region config definitions.
* No GUI section implementation in this slice.

## Changed Files
* `apps/calculator/ui/en14825/scop_adapter.py` (modified)
* `tests/test_apps_calculator_ui_en14825_scop.py` (modified)
* `result_reports/active/370_en14825_scop_foundation.md` (modified)
* `result_reports/active/371_en14825_scop_temperature_default_boundary.md` (created)

## Adapter Boundary Correction
* Exposes `resolve_temperature_overrides(climate, tbiv_temp_c, tol_temp_c)` which resolves omitted inputs using UI/adapter-level `CLIMATE_DEFAULTS` (Average: -10°C / -11°C, Warmer: 2°C / -11°C, Colder: -15°C / -22°C).
* Guarantees both declared and tested runs call core calculate method with explicit, identical parameters.

## Test Results
16 unit tests successfully pass in `tests/test_apps_calculator_ui_en14825_scop.py`:
* Verified average climate defaults pass -10.0°C / -11.0°C.
* Verified warmer climate defaults pass 2.0°C / -11.0°C.
* Verified colder climate defaults pass -15.0°C / -22.0°C.
* Verified partial overrides fall back correctly (e.g. Tbiv override preserves default TOL).
* Verified `TOL > Tbiv` error blocks core invocation and returns `invalid_temp_override` status code.

All SEER tests continue to pass without regression.

## MVC/SoC Judgment
The adapter retains its responsibility as the contract translation boundary, mapping and sanitizing all inputs before delegating computation.

## Known Risks / Gaps
None. Effective temperature mapping is robustly covered by focused tests.

## Next Suggested Action
Proceed to **Slice 2: section UI integration** (`en14825_scop_section.py`) to build the stacked climate cards and bind dynamic events.

## Project Memory Delta
- none
