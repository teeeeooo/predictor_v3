# 178 Tkinter Initial Window Size and Scroll

## Goal

Fix the Tkinter calculator startup display so the initial window stays inside the visible screen and lower CSPF/HSPF tables remain reachable when content is taller than the window.

## Scope

- `ui_tk/calculator_app.py`
- `ui_tk/tabs/iso16358_tab.py`
- `tests/test_ui_tk_calculator_foundation.py`
- `docs/guides/lightweight_calculator_tk_manual_smoke.md`
- `docs/WORK_PLAN.md`

## Non-goals

- `app_calculator_tk.py` was not modified and remains a thin entrypoint.
- `ExcelLikeTableController` and `MetricInputTable` were not modified.
- No visual theme/token, graph/detail, matplotlib, standard/region expansion, Windows packaging, PyQt retirement, core/profile/dispatcher/calculator/golden/fixture, `project_log.md`, `result_reports/memory/project_memory_seed.md`, or lifecycle summary/archive work was performed.

## Verification

- `python3 -B tools/check_code_structure.py`  
  Result: passed, `code structure guard: OK (no findings)`.
- `python3 -B -m py_compile ui_tk/calculator_app.py ui_tk/tabs/iso16358_tab.py`  
  Result: passed.
- `python3 -B -m pytest tests/test_ui_tk_calculator_foundation.py tests/test_ui_tk_excel_like_table_controller.py tests/test_ui_tk_iso_table_autocalc.py -q -rxXs`  
  Result: passed, `43 passed in 1.63s`.
- `git diff --check`  
  Result: passed.

## Task Results

### task 1

- 수정 파일: `ui_tk/calculator_app.py`, `tests/test_ui_tk_calculator_foundation.py`
- 수정 내용: initial geometry calculation now caps requested width/height to screen size with margins, keeps coordinates non-negative through the existing centering helper, and applies a reasonable `minsize`. Pure helper coverage was added for normal, oversized, and small requested-size cases.
- 검증 결과: `tests/test_ui_tk_calculator_foundation.py` passed within the focused test command.

### task 2

- 수정 파일: `ui_tk/tabs/iso16358_tab.py`, `tests/test_ui_tk_calculator_foundation.py`
- 수정 내용: ISO tab content is rendered inside a Canvas-backed vertical scroll container with a `ttk.Scrollbar`. Region selector and CSPF/HSPF section stack remain in the scrollable content frame. Mouse wheel and trackpad scroll bind while the pointer is over the tab. Content width is synchronized to the canvas width so existing responsive table-width behavior is preserved.
- 검증 결과: focused tests passed, including existing table interaction/autocalc tests and width-expansion tests.

### task 3

- 수정 파일: `docs/guides/lightweight_calculator_tk_manual_smoke.md`, `docs/WORK_PLAN.md`, `result_reports/active/178_tkinter-initial-window-size-and-scroll.md`
- 수정 내용: manual smoke guide now checks initial window fit, lower table accessibility via vertical scroll, mouse wheel/trackpad scroll, and table behavior after scrolling. WORK_PLAN records task 178 completion and keeps the next recommended action as macOS Tkinter manual UX smoke.
- 검증 결과: `git diff --check` passed; forbidden project log, memory seed, lifecycle, controller, and table files were not modified.

## Test Results

- Focused Tk shell/controller/autocalc suite: `43 passed`.
- Full pytest was not run because it was not part of the requested verification command list for task 178.

## Changed Files

- `ui_tk/calculator_app.py`
- `ui_tk/tabs/iso16358_tab.py`
- `tests/test_ui_tk_calculator_foundation.py`
- `docs/guides/lightweight_calculator_tk_manual_smoke.md`
- `docs/WORK_PLAN.md`
- `result_reports/active/178_tkinter-initial-window-size-and-scroll.md`

## Known Failures / Risks

- Live macOS manual smoke remains required to confirm actual window-manager placement and trackpad behavior.
- Mouse wheel binding is active while the pointer is over the scrollable ISO tab; table keyboard, clipboard, and edit behavior are covered by existing controller tests and were not changed.

## Next Suggested Action

- macOS Tkinter manual UX smoke.

## Scope Compliance

- `ExcelLikeTableController` was not modified.
- `MetricInputTable` was not modified.
- `app_calculator_tk.py` was not modified.
- `project_log.md` was not modified.
- `result_reports/memory/project_memory_seed.md` was not modified.
- No lifecycle summary/archive maintenance was performed.

## Commit / Push

- Source/test/docs commit: `39db1f6` (`fix: add tkinter initial scroll layout`).
- Report commit: this commit (`report: tkinter initial window size and scroll`).
- Push: completed to `origin/work/ui-ux-ssot-adoption` through this report commit.

## Project Memory Delta

- type: fact
  topic: Tkinter initial window size and ISO tab scroll
  content: predictor_v3 Tkinter calculator shell caps initial requested window size to the visible screen and ISO 16358 tab content is wrapped in a vertical scroll container so lower CSPF/HSPF tables remain reachable when content exceeds window height.
  keywords:
    - predictor_v3
    - Tkinter
    - initial window geometry
    - vertical scroll
    - ISO 16358 tab
  assertionStatus: verified
  source: result_reports/active/178_tkinter-initial-window-size-and-scroll.md; focused pytest verification
