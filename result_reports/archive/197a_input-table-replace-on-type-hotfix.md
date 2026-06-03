# 197-a Input Table Replace-On-Type Hotfix

## Goal

- Close out the 196-a graph min/max scale label manual smoke.
- Fix MetricInputTable single-click typing so the first printable key replaces the selected cell value instead of appending to it.
- Keep geometry issues as a separate follow-up.

## Scope

- Updated `ui_tk/excel_like_table_controller.py` only in the generic printable key binding path.
- Updated focused Excel-like controller tests in `tests/test_ui_tk_excel_like_table_controller.py`.
- Updated `docs/WORK_PLAN.md` and `result_reports/active/196a_graph-min-max-scale-label-hotfix.md`.

## Non-goals

- No geometry/window placement fix.
- No graph, CSV export, detail panel, ResultPanel, core, profile/config, golden, fixture, PyQt, or Hong Kong HSPF changes.
- No paste, copy, range selection, navigation, or table copy rewrite.

## Cause

- The controller already separated selection mode from edit mode with `_replace_pending`.
- Printable key handling returned `"break"` after replacing the active selected value, but the generic `KeyPress` binding was registered with `add="+"`.
- In real Tk Entry key events, that additive binding could still allow native insertion behavior to append the typed key to the old value path.

## Change

- Registered the controller's generic `KeyPress` handler as the widget-level handler instead of an additive handler.
- Kept specific bindings for copy, paste, undo, delete/backspace, F2, escape, navigation, and arrows unchanged.
- Preserved double-click/F2 edit mode by returning native Entry behavior when `_mode == "edit"`.

## Tests

- Updated focused controller coverage for `200` -> single-click -> type `100` -> `100`.
- Added real Tk key-event coverage for the replace-on-type path when a display is available.
- Existing coverage continues to cover paste/copy/delete/undo/navigation/drag and edit-mode behavior.

## Manual Check Result

- User manual smoke confirmed the 196-a graph min/max scale label on Windows dual-monitor setup.
- Simple window movement between monitors did not reproduce clipping.

## Windows Manual Check Failed

- User manual check found the 197-a input replace-on-type fix did not hold on Windows.
- Single-click typing still prepends/appends to the existing value instead of replacing it.
- Example failure path: `200` -> single-click -> type `100` -> `100200`-style result.
- Follow-up owner: `197-a2 input table replace-on-type Windows follow-up`.

## Follow-up Geometry Issues

- After moving the app to monitor 2, opening detail view can recenter on monitor 1.
- On first launch, the main window can appear below screen center enough to be clipped.
- These are recorded as next-work candidates only; this hotfix does not change geometry code.

## Verification

- Process check before final verification.
- `python3 -B tools/check_code_structure.py`
- `python3 -B -m py_compile` for changed source/tests and focused related test files.
- Quick smoke: replace-on-type test plus full app smoke test.
- Final focused pytest set: Excel-like controller, ISO table autocalc, calculator foundation, and profile resolver tests.
- `git diff --check`

## Known Risks

- Tk GUI tests skip in headless Codespaces when no display is available; the 197-a input typing behavior failed Windows manual verification.
- Geometry issues remain intentionally unfixed.

## Project Memory Delta

- none
