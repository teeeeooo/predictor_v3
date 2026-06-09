# 284 Controller Switch Pilot Implementation

## Goal

Perform the first production pilot of the main table/controller migration by
switching `HongKongCspfSection`'s table controllers from
`ExcelLikeTableController` to `TkTableController`.

## Scope

- `ui_tk/sections/hong_kong_cspf_section.py`
  - Change import from `ExcelLikeTableController` to `TkTableController`
  - Switch `rated_controller` and `input_controller` instantiation
- `tests/test_ui_tk_hong_kong_cspf_controller_switch.py`
  - 5 focused pilot tests
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
  - Regenerated (timestamp-only change)

## Excluded Scope

- No other section files modified (HongKongHspf, IsoIseer, SasoT3 remain
  using `ExcelLikeTableController`).
- No `metric_input_table.py`, `excel_like_table_controller.py`,
  `table/controller.py`, `table/interaction_core.py`, `table/surface.py`
  modifications.
- No calculator/core changes.
- No full controller switch.

## Pilot Target

`HongKongCspfSection` contains:
- `rated_table`: 1x1 `MetricInputTable` (declared capacity)
- `input_table`: 2x2 `MetricInputTable` (full/half capacity/power)

Both tables previously used `ExcelLikeTableController`. After this slice both
use `TkTableController`.

## Controller Switch Summary

| Line | Before | After |
|------|--------|-------|
| Import | `from ui_tk.excel_like_table_controller import ExcelLikeTableController` | `from ui_tk.table.controller import TkTableController` |
| rated_controller | `ExcelLikeTableController(self.rated_table)` | `TkTableController(self.rated_table)` |
| input_controller | `ExcelLikeTableController(self.input_table)` | `TkTableController(self.input_table)` |

Table construction, default values, callback wiring, result calculation,
detail panel, and batch dialog behavior are unchanged.

## Added Tests

`tests/test_ui_tk_hong_kong_cspf_controller_switch.py` (5 tests):

| Class | Tests | What they verify |
|-------|-------|-----------------|
| `TestControllerSwitch` | 2 | `rated_controller` and `input_controller` are instances of `TkTableController` |
| `TestPasteBehavior` | 2 | Paste updates editable cell; paste does not reject invalid text |
| `TestRecalculate` | 1 | `recalculate_now()` with valid values produces a result (not error) through new controller |

## Xvfb Validation Result

| Suite | Passed | Skipped | Failed |
|-------|--------|---------|--------|
| Pilot tests | 5 | 0 | 0 |
| Parity tests | 15 | 0 | 0 |

Total: **20 passed, 0 skipped, 0 failures** in Xvfb environment.

## Code Map Regeneration Result

`python3 -B tools/code_checker/build_reference_map.py` was executed.
`CODEBASE_REFERENCE_MAP.md` changed by **timestamp only** (no structural or
import-edge changes of note). This is expected for a single-import change in
one section file.

## Validation

| Check | Command | Result |
|-------|---------|--------|
| Pilot tests | `xvfb-run -a pytest tests/test_ui_tk_hong_kong_cspf_controller_switch.py -rs -vv` | 5 passed, 0 skipped, 0 failures |
| Parity tests | `xvfb-run -a pytest tests/test_ui_tk_metric_input_table_controller_parity.py -rs -vv` | 15 passed, 0 skipped, 0 failures |
| Compile target section | `py_compile ui_tk/sections/hong_kong_cspf_section.py` | OK |
| Compile pilot test | `py_compile tests/test_ui_tk_hong_kong_cspf_controller_switch.py` | OK |
| Structure guard | `python3 -B tools/check_code_structure.py` | No new violations |
| Code map regen | `python3 -B tools/code_checker/build_reference_map.py` | Timestamp-only change |
| Git diff check | `git diff --check` | Clean |

## Manual Windows Smoke Required (Not Yet Performed)

Before marking this pilot complete, the following must be verified on Windows:

1. `python -m pytest tests/test_ui_tk_hong_kong_cspf_controller_switch.py -rs -vv`
2. `python -m pytest tests/test_ui_tk_metric_input_table_controller_parity.py -rs -vv`
3. Run `calculator_tk`
4. Select Hong Kong CSPF profile
5. Click rated/input table cells
6. Single-key replace-on-type
7. Excel 2x2 copy → paste into input table
8. Invalid text paste → paste accepted, calculation blocks/invalid display
9. Ctrl+Z undo
10. Delete/Backspace clear
11. F2 edit / Escape restore
12. CSPF detail open/close, window refit
13. Switch to HSPF/other profile, check for UI breakage/ghosting/focus issues

## Next

- **Post-implementation Windows smoke** for `HongKongCspfSection` controller
  switch pilot.
- If Windows smoke passes: expand switch to remaining sections
  (`HongKongHspfSection`, `IsoIseer2pointSection`, `SasoT3Section`).
- If Windows smoke reveals issues: targeted fix before expansion.

## Risks

- `ExcelLikeTableController` still used in 3 other sections; inconsistent
  controller foundation across sections until full switch.
- `TkTableController` and `ExcelLikeTableController` may have subtle
  behavioral differences in edge cases not covered by focused tests.
- Windows Tcl/Tk install issue (2 skipped in 283) may affect interactive
  smoke if the user's local environment hasn't been fixed.
