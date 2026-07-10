# 176 Tkinter Excel-like Edit Mode Implementation

## Goal

Implement the Tkinter `ExcelLikeTableController` selection/edit state machine from `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md`, including same-cell second click, double click, and F2 edit-entry paths.

## Scope

- `ui_tk/excel_like_table_controller.py`
- `tests/test_ui_tk_excel_like_table_controller.py`
- `docs/guides/lightweight_calculator_tk_manual_smoke.md`
- `docs/WORK_PLAN.md`

## Non-goals

- No `MetricInputTable` interaction responsibility was added.
- No core/profile/dispatcher/calculator/golden/fixture files were changed.
- No paste atomic validation redesign, auto-calc debounce/result-surface change, visual token change, Forest-ttk-theme work, lifecycle summary/archive work, `project_log.md` update, or `result_reports/memory/project_memory_seed.md` update was performed.

## Verification

- `python3 -B tools/check_code_structure.py`
  Result: passed, `code structure guard: OK (no findings)`.
- `python3 -B -m py_compile ui_tk/excel_like_table_controller.py tests/test_ui_tk_excel_like_table_controller.py tests/test_ui_tk_iso_table_autocalc.py`
  Result: passed.
- `python3 -B -m pytest tests/test_ui_tk_excel_like_table_controller.py tests/test_ui_tk_iso_table_autocalc.py -q -rxXs`
  Result: passed, `36 passed in 1.64s`.
- `python3 -B -m pytest -q -rxXs`
  Result: passed, `663 passed, 32 skipped, 19 xfailed in 3.19s`.
- `git diff --check`
  Result: passed.

## Task Results

### task 1

- 수정 파일: `ui_tk/excel_like_table_controller.py`, `tests/test_ui_tk_excel_like_table_controller.py`
- 수정 내용: controller-local selection/edit mode state and edit snapshot were added. First click leaves the cell in selection mode with hidden caret. Same selected cell second click, double click, and F2 enter edit mode with the existing value preserved and caret visible.
- 검증 결과: covered by controller regression tests and full verification commands.

### task 2

- 수정 파일: `ui_tk/excel_like_table_controller.py`, `tests/test_ui_tk_excel_like_table_controller.py`
- 수정 내용: selection mode keeps cell-level printable replace, Arrow navigation, Delete/Backspace clear, Tab/Enter/KP_Enter navigation, and Esc selection clear. Edit mode lets printable/Arrow/Delete/Backspace fall through to native text editing, commits on Enter/Tab/KP_Enter before navigation, restores the edit snapshot on Esc, and commits before external focus clear. Edit commit records one undo snapshot.
- 검증 결과: controller tests cover mode-specific key behavior, grouped edit undo, focus-out commit, cross-table selection clear, and paste atomic reject.

### task 3

- 수정 파일: `tests/test_ui_tk_excel_like_table_controller.py`
- 수정 내용: regression tests were added for same-cell second click, double click, F2 edit entry, edit caret visibility, append/insert behavior, edit-mode Arrow/Delete/Backspace fall-through, selection-mode Delete/Backspace clear, edit commit/navigation, Esc restore, and focus-out commit. Existing Tab/Enter/arrow first-key replace and cross-table clear tests remain.
- 검증 결과: `tests/test_ui_tk_excel_like_table_controller.py` passed as part of the focused `36 passed` run and the full suite.

### task 4

- 수정 파일: `docs/guides/lightweight_calculator_tk_manual_smoke.md`, `docs/WORK_PLAN.md`, `result_reports/active/176_tkinter-excel-like-edit-mode-implementation.md`
- 수정 내용: manual smoke edit-mode checks now describe implemented verification steps. `docs/WORK_PLAN.md` records task 176 completion and leaves the next recommended action as `macOS Tkinter manual UX smoke`.
- 검증 결과: docs diff checked by `git diff --check`; forbidden project log, memory seed, lifecycle summary/archive files were not modified.

## Test Results

- Focused controller/autocalc tests: `36 passed`.
- Full suite: `663 passed, 32 skipped, 19 xfailed`.
- Existing skips/xfails are unrelated known PyQt environment and legacy diagnostic items.

## Changed Files

- `ui_tk/excel_like_table_controller.py`
- `tests/test_ui_tk_excel_like_table_controller.py`
- `docs/guides/lightweight_calculator_tk_manual_smoke.md`
- `docs/WORK_PLAN.md`
- `result_reports/active/176_tkinter-excel-like-edit-mode-implementation.md`

## Known Failures / Risks

- No automated screenshot/pixel or full app launch test was added by design.
- Same-cell second click and double click place the caret at the value end; click-position caret placement remains a possible future refinement.

## Next Suggested Action

- macOS Tkinter manual UX smoke.

## Scope Compliance

- `project_log.md` was not modified.
- `result_reports/memory/project_memory_seed.md` was not modified.
- No lifecycle summary/archive maintenance was performed.
- No core/profile/dispatcher/calculator/golden/fixture files were modified.

## Commit / Push

- Source/test/docs commit: `1dbf5ea` (`fix: implement tkinter table edit mode`).
- Report commit: this commit (`report: tkinter excel-like edit mode implementation`).
- Push: pending.

## Project Memory Delta

- type: fact
  topic: Tkinter Excel-like edit mode
  content: predictor_v3 Tkinter `ExcelLikeTableController` implements selection/edit mode separation with same-cell second click, double click, and F2 entering caret-visible partial edit while preserving the existing value; edit commit records one undo snapshot from the edit-start value.
  keywords:
    - predictor_v3
    - Tkinter
    - ExcelLikeTableController
    - edit mode
    - spreadsheet table
  assertionStatus: verified
  source: result_reports/active/176_tkinter-excel-like-edit-mode-implementation.md; `python3 -B -m pytest tests/test_ui_tk_excel_like_table_controller.py tests/test_ui_tk_iso_table_autocalc.py -q -rxXs`
