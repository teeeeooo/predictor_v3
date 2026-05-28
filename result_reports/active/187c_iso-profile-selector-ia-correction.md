# 187-c ISO Profile Selector IA Correction

## Goal

Correct the Tkinter ISO tab selector hierarchy after manual smoke of 187-b.

## Scope

- Treat `Hong Kong` and `ISO / ISEER 2-point` as ISO tab profiles rather than peer calculation modes.
- Make `ISO / ISEER 2-point` the default selected profile.
- Hide the duplicate `지역: Hong Kong` selector when the Hong Kong profile is selected.
- Preserve Hong Kong CSPF/HSPF metric sub-tabs and all existing calculations.

## Non-goals

- No 2-point calculation logic changes.
- No SASO option or implementation.
- No multi/batch, detail/trace, graph, EN/AHRI implementation.
- No core/profile/config/golden/fixture/PyQt source changes.
- No `ResultPanel`, `ScrollableFrame`, or window geometry changes.

## Changed Files

- `ui_tk/profile_resolver.py`
- `ui_tk/tabs/iso16358_tab.py`
- `tests/test_ui_tk_profile_resolver.py`
- `tests/test_ui_tk_iso_table_autocalc.py`
- `docs/WORK_PLAN.md`
- `result_reports/active/187c_iso-profile-selector-ia-correction.md`

## Implementation

- `calculation_mode_labels()` now returns profile selector labels in default-first order:
  - `ISO / ISEER 2-point`
  - `Hong Kong`
- The ISO tab selector label is now `ISO 프로파일`.
- `Iso16358Tab` opens on `ISO / ISEER 2-point`.
- Hong Kong still renders CSPF/HSPF metric sub-tabs, but the internal single-region `지역` row is no longer packed into the visible UI.
- Existing 2-point section and calculation behavior are unchanged.

## Verification

- `python3 -B tools/check_code_structure.py` — passed.
- `python3 -B -m py_compile ui_tk/tabs/iso16358_tab.py ui_tk/profile_resolver.py tests/test_ui_tk_profile_resolver.py tests/test_ui_tk_iso_table_autocalc.py tests/test_ui_tk_calculator_foundation.py` — passed.
- `python3 -B -m pytest tests/test_ui_tk_iso_table_autocalc.py::test_iso_iseer_2point_mode_renders_default_summaries tests/test_ui_tk_calculator_foundation.py::test_calculator_tk_app_builds_widget_tree -q -rxXs` — `2 passed`.
- `python3 -B -m pytest tests/test_ui_tk_profile_resolver.py tests/test_ui_tk_iso_table_autocalc.py tests/test_ui_tk_calculator_foundation.py -q -rxXs` — `42 passed`.
- `git diff --check` — clean.
- No leftover pytest/python process.

Full pytest was not run by request.

## Manual Check Needed

- Confirm the app opens directly on `ISO / ISEER 2-point`.
- Confirm switching to `Hong Kong` shows only CSPF/HSPF metric sub-tabs, without the duplicate region selector.
- Confirm switching back to `ISO / ISEER 2-point` keeps 2-point summaries and input editing stable.

## Commit / Push

- source/test commit: `fa657b1f5b0593951d358a25aa90650f058e1d35`
- report/WORK_PLAN commit: pending
- push: pending

## Project Memory Delta

- none
