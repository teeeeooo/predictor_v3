# 130 Tkinter ISO Section Pure Helper Cleanup

## Goal

Extract the pure input-dict construction and result text formatting logic from the Tkinter ISO CSPF/HSPF section classes without changing UI layout, defaults, calculator routing, or smoke results.

## Scope

- `ui_tk/sections/iso_cspf_section.py`
- `ui_tk/sections/iso_hspf_section.py`
- `ui_tk/sections/iso16358_helpers.py`
- `tests/test_ui_tk_iso16358_helpers.py`
- `docs/WORK_PLAN.md`

## Non-Goals

- Add a region, metric, standard, UI feature, or calculator behavior.
- Change UI layout, labels, button text, default values, result panel behavior, profile resolver behavior, dispatcher/core calls, expected values, fixtures, xfail markers, PyQt code, or PyQt tests.
- Perform result report lifecycle maintenance.

## Task 1 Result

Section responsibility classification:

| Responsibility | Before | After |
| --- | --- | --- |
| Tkinter widget creation/layout | Section classes | Section classes |
| Entry value reads | Section classes via `NumericEntryRow.get_value()` | Section classes |
| Calculator input dict construction | Section classes | `ui_tk.sections.iso16358_helpers` |
| Profile id resolution | Section classes via `resolve_profile_id(region_label, metric)` | Section classes |
| Calculator creation/call | Section classes via `create_calculator_for_profile(profile_id=...)` | Section classes |
| Result text formatting | Section classes | `ui_tk.sections.iso16358_helpers` |
| Result callback invocation | Section classes | Section classes |

Moved to pure helper:

- CSPF measured input + declared capacity construction.
- HSPF measured input construction.
- CSPF result text formatting.
- HSPF result text formatting.

Left in section classes:

- Widget creation and layout.
- Existing default UI values.
- Entry reads.
- Resolver and dispatcher/core call orchestration.
- Exception handling and result callback calls.

## Task 2 Result

Added helper module:

- `ui_tk/sections/iso16358_helpers.py`

Public helpers:

- `build_cspf_input(...)`
- `build_hspf_input(...)`
- `format_cspf_result(result) -> str`
- `format_hspf_result(result) -> str`

The helper module imports only stdlib typing utilities and does not import Tkinter, PyQt, the resolver, dispatcher, calculator core, or result panel.

The input dict contracts are unchanged:

- CSPF:
  - `35_full.capacity`
  - `35_full.power`
  - `35_half.capacity`
  - `35_half.power`
  - declared capacity returned separately for `calculate_cspf(..., declared_capacity=...)`.
- HSPF:
  - `rated_heating_capacity`
  - `7_full.capacity`
  - `7_full.power`
  - `7_half.capacity`
  - `7_half.power`

The result text still includes:

- `[CSPF]`
- `CSPF = ...`
- `CSTL = ...`
- `CSEC = ...`
- `[HSPF]`
- `HSPF = ...`
- `HSTL_Wh = ...`
- `HSEC_Wh = ...`

## Task 3 Result

Updated section classes:

- `IsoCspfSection._read_inputs()` now reads entries and calls `build_cspf_input(...)`.
- `IsoCspfSection._on_calculate()` now calls `format_cspf_result(result)` before invoking the result callback.
- `IsoHspfSection._read_inputs()` now reads entries and calls `build_hspf_input(...)`.
- `IsoHspfSection._on_calculate()` now calls `format_hspf_result(result)` before invoking the result callback.

Unchanged behavior:

- UI layout.
- Entry labels.
- Default values.
- Button text.
- Exception flow.
- Result callback behavior.
- `resolve_profile_id(region_label, "CSPF"/"HSPF")`.
- `create_calculator_for_profile(profile_id=...)`.
- Calculator method calls.

## Task 4 Result

Added pure helper tests:

- `tests/test_ui_tk_iso16358_helpers.py`

Coverage:

- Importing `ui_tk.sections.iso16358_helpers` does not import `tkinter` or `PyQt5`.
- `build_cspf_input(...)` creates the existing CSPF measured dict and declared capacity.
- `build_hspf_input(...)` creates the existing HSPF measured dict.
- `format_cspf_result(...)` includes the existing `[CSPF]`, `CSPF`, `CSTL`, and `CSEC` output lines.
- `format_cspf_result(...)` keeps the legacy `cstl` / `csec` fallback when `_wh` keys are absent.
- `format_hspf_result(...)` includes the existing `[HSPF]`, `HSPF`, `HSTL_Wh`, and `HSEC_Wh` output lines.

Existing Tkinter smoke remained intact:

- `tests/test_ui_tk_profile_resolver.py tests/test_ui_tk_calculator_foundation.py` -> `15 passed`.
- Hong Kong CSPF smoke remains `4.939`.
- Hong Kong HSPF smoke remains `3.643`.
- `ui_tk.calculator_app` import still avoids PyQt5.

## Task 5 Result

`docs/WORK_PLAN.md` was updated narrowly:

- Recorded the Tkinter ISO section pure helper cleanup.
- Recorded the new helper module and retained section-class responsibilities.
- Recorded full-suite result after the cleanup.

Next recommended actions:

1. Python 3.12/3.11 venv PyQt support validation.
2. Windows PyInstaller size measurement when a Windows host is available.
3. PyQt test support matrix documentation.
4. Tkinter next metric/standard extension design, if needed.

Lifecycle maintenance was not performed because this task creates a single active report and does not summarize/archive active reports.

## Task 6 Result

Verification:

- `python3 -B tools/check_code_structure.py` -> `code structure guard: OK (no findings)`.
- `python3 -B -m py_compile ui_tk/sections/iso16358_helpers.py ui_tk/sections/iso_cspf_section.py ui_tk/sections/iso_hspf_section.py tests/test_ui_tk_iso16358_helpers.py` -> pass.
- `python3 -B -m pytest tests/test_ui_tk_iso16358_helpers.py -q` -> `6 passed`.
- `python3 -B -m pytest tests/test_ui_tk_profile_resolver.py tests/test_ui_tk_calculator_foundation.py -q` -> `15 passed`.
- `python3 -B -m pytest -q -rxXs` -> `585 passed, 59 skipped, 19 xfailed`.

Remaining xfail count:

- 19 xfailed.

Native abort status:

- No native abort occurred. The known-bad macOS PyQt widget tests were skipped by the existing 129 environment guard.

## Changed Files

- `ui_tk/sections/iso16358_helpers.py`
- `ui_tk/sections/iso_cspf_section.py`
- `ui_tk/sections/iso_hspf_section.py`
- `tests/test_ui_tk_iso16358_helpers.py`
- `docs/WORK_PLAN.md`
- `result_reports/active/130_tkinter-iso-section-pure-helper-cleanup.md`

## Residual Risk

- This is a structural cleanup only; it does not add new Tkinter metrics, standards, or region coverage.
- Future Tkinter expansion should continue to keep widget orchestration separate from pure input/format helpers.
