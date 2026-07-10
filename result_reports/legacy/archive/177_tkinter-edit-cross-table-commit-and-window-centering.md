# 177 Tkinter Edit Cross-table Commit and Window Centering

## Goal

Fix two macOS manual smoke findings after task 176: edit-mode values must commit when another table/card cell is clicked, and the Tkinter calculator window must open inside the visible screen near center.

## Scope

- `ui_tk/excel_like_table_controller.py`
- `ui_tk/calculator_app.py`
- `tests/test_ui_tk_excel_like_table_controller.py`
- `tests/test_ui_tk_calculator_foundation.py`
- `docs/guides/lightweight_calculator_tk_manual_smoke.md`
- `docs/WORK_PLAN.md`

## Non-goals

- No `MetricInputTable` interaction responsibility was added.
- No paste atomic validation, auto-calc debounce, result surface, visual token, theme, core/profile/dispatcher/calculator/golden/fixture, packaging, or PyQt retirement work was performed.
- `app_calculator_tk.py` remains a thin entrypoint.
- `project_log.md` and `result_reports/memory/project_memory_seed.md` were not modified.
- No lifecycle summary/archive maintenance was performed.

## Verification

- `python3 -B tools/check_code_structure.py`
  Result: passed, `code structure guard: OK (no findings)`.
- `python3 -B -m py_compile ui_tk/excel_like_table_controller.py ui_tk/calculator_app.py tests/test_ui_tk_excel_like_table_controller.py tests/test_ui_tk_iso_table_autocalc.py`
  Result: passed.
- `python3 -B -m pytest tests/test_ui_tk_excel_like_table_controller.py tests/test_ui_tk_iso_table_autocalc.py -q -rxXs`
  Result: passed, `37 passed in 1.48s`.
- `python3 -B -m pytest tests/test_ui_tk_calculator_foundation.py -q -rxXs`
  Result: passed, `5 passed in 0.40s`.
- `python3 -B -m pytest -q -rxXs`
  Result: passed, `665 passed, 32 skipped, 19 xfailed in 3.24s`.
- `git diff --check`
  Result: passed.

## Task Results

### task 1

- 수정 파일: `ui_tk/excel_like_table_controller.py`, `tests/test_ui_tk_excel_like_table_controller.py`
- 수정 내용: Esc cancel path and external/cross-controller clear path were separated. Esc still restores the edit snapshot and keeps the cell selected. External clear and cross-controller selection clear now commit the edit before clearing selection. Focus-out uses the same commit-and-clear path.
- 검증 결과: added regression coverage for edit mode followed by another table click preserving the edited value; existing edit entry, first-key replace, focus-out commit, Esc restore, and cross-table selection clear tests pass.

### task 2

- 수정 파일: `ui_tk/calculator_app.py`, `tests/test_ui_tk_calculator_foundation.py`
- 수정 내용: added `centered_geometry()` and `center_window()` in the Tk shell. The app now calls `update_idletasks()`, calculates requested/root size against screen size, clamps x/y to non-negative values, and applies geometry from `CalculatorTkApp`; `app_calculator_tk.py` was not changed.
- 검증 결과: pure geometry helper and injected-root build test cover centered placement and non-negative root coordinates.

### task 3

- 수정 파일: `docs/guides/lightweight_calculator_tk_manual_smoke.md`, `docs/WORK_PLAN.md`, `result_reports/active/177_tkinter-edit-cross-table-commit-and-window-centering.md`
- 수정 내용: manual smoke guide now includes initial window placement, edit-mode cross-table/card commit, Esc cancel, and focus-out commit checks. `docs/WORK_PLAN.md` records task 177 completion and keeps the next recommended action as macOS Tkinter manual UX smoke.
- 검증 결과: docs included in `git diff --check`; forbidden project log, memory seed, and lifecycle files were not modified.

## Test Results

- Focused controller/autocalc tests: `37 passed`.
- Tk shell/foundation tests: `5 passed`.
- Full suite: `665 passed, 32 skipped, 19 xfailed`.
- Existing skips/xfails are unrelated known PyQt environment and legacy diagnostic items.

## Changed Files

- `ui_tk/excel_like_table_controller.py`
- `ui_tk/calculator_app.py`
- `tests/test_ui_tk_excel_like_table_controller.py`
- `tests/test_ui_tk_calculator_foundation.py`
- `docs/guides/lightweight_calculator_tk_manual_smoke.md`
- `docs/WORK_PLAN.md`
- `result_reports/active/177_tkinter-edit-cross-table-commit-and-window-centering.md`

## Known Failures / Risks

- Manual smoke still needs to be rerun on macOS to confirm the actual window-manager placement and cross-table click behavior in the live app.
- Geometry centering is based on Tk requested/root size and screen size; multi-monitor placement remains delegated to Tk's reported screen metrics.

## Next Suggested Action

- macOS Tkinter manual UX smoke.

## Scope Compliance

- `project_log.md` was not modified.
- `result_reports/memory/project_memory_seed.md` was not modified.
- No lifecycle summary/archive maintenance was performed.
- No core/profile/dispatcher/calculator/golden/fixture files were modified.
- `app_calculator_tk.py` was not modified.

## Commit / Push

- Source/test/docs commit: `be12939` (`fix: commit tkinter edits on external selection`).
- Report commit: this commit (`report: tkinter edit commit and window centering`).
- Push: completed to `origin/work/ui-ux-ssot-adoption` through this report commit.

## Project Memory Delta

- type: fact
  topic: Tkinter edit external commit and window centering
  content: predictor_v3 Tkinter external table/card clicks commit active `ExcelLikeTableController` edit-mode values before clearing selection, while Esc remains the cancel-and-restore path; the Tk calculator shell centers the initial window using requested/root size and screen size with non-negative coordinates.
  keywords:
    - predictor_v3
    - Tkinter
    - ExcelLikeTableController
    - edit mode
    - window centering
  assertionStatus: verified
  source: result_reports/active/177_tkinter-edit-cross-table-commit-and-window-centering.md; focused and full pytest verification
