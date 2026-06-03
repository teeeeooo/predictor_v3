# 197-a2 Input Table Replace-On-Type Windows Follow-up

## Goal

- Record that the 197-a replace-on-type fix failed Windows manual verification.
- Make single-click selection mode robust so first typing replaces the existing editable cell value instead of prepending/appending.
- Keep geometry issues as a separate follow-up.

## Scope

- Updated `ui_tk/excel_like_table_controller.py` within selection/caret handling only.
- Updated focused Excel-like controller tests in `tests/test_ui_tk_excel_like_table_controller.py`.
- Updated `docs/WORK_PLAN.md` and `result_reports/active/197a_input-table-replace-on-type-hotfix.md`.

## Non-goals

- No geometry/window placement fix.
- No paste, copy, range selection, undo, navigation policy, detail panel, graph, CSV export, ResultPanel, core, profile/config, golden, fixture, PyQt, or Hong Kong HSPF changes.

## Windows Manual Check Failed

- User verified 197-a on Windows and found single-click typing still prepended/appended instead of replacing.
- Example: `200` -> single-click -> type `100` should produce `100`, but produced a `100200`-style value.

## Cause Hypothesis

- 197-a changed the printable `KeyPress` binding, but Windows native Entry insertion can still occur if the intercept path is missed.
- Selection mode previously cleared Entry text selection and placed the cursor at index `0`.
- If native insertion runs in that state, the typed value can be inserted before the old value.

## Change

- Selection mode now selects the full Entry text with `selection_range(0, "end")`.
- The caret remains hidden via `insertontime=0`, with the insertion cursor at the selection end.
- Navigation and arrow movement now reuse the same selected-cell visual/text-selection state.
- `_type_replace()` remains the explicit first-printable-key replacement path.
- Double-click/F2 edit mode still clears selection and keeps normal internal editing behavior.

## Tests

- Added/updated focused controller checks that selection mode covers the whole existing Entry text.
- Kept direct handler coverage for `200` -> single-click -> type `100` -> `100`.
- Kept real Tk key-event coverage for display-enabled environments.
- Added edit-mode assertions that double-click/F2 do not force full-text selected-cell replacement.

## Verification

- Process check before final verification: no leftover pytest/python process beyond the check command itself.
- `python3 -B tools/check_code_structure.py`
  - Passed with existing soft-limit warning: `ui_tk/sections/bin_detail_panel.py` exceeds 400 LOC.
- `python3 -B -m py_compile` for changed source/tests and focused related test files.
  - Passed.
- Quick smoke: replace-on-type follow-up test plus full app smoke test.
  - Result: 3 skipped because Tk display is unavailable in Codespaces.
- Final focused pytest set: Excel-like controller, ISO table autocalc, calculator foundation, and profile resolver tests.
  - Result: 34 passed, 72 skipped because Tk display is unavailable in Codespaces.
- `git diff --check`
  - Passed.

## Manual Check Result

- Codespaces automated verification and Windows manual GUI verification were performed separately.
- User completed Windows local GUI smoke for 197-a2.
- Single-click typing in an editable input table cell now replaces the existing value instead of prepending/appending.
- 197-a2 is closed for the input table replace-on-type behavior.

## Follow-up Geometry Issues

- After moving the app to monitor 2, opening detail view can recenter on monitor 1.
- On first launch, the main window can appear below screen center enough to be clipped.
- These remain next-work candidates only; this hotfix does not change geometry code.

## Project Memory Delta

- none
