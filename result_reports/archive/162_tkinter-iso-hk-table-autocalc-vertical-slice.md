# 162. Tkinter ISO Hong Kong Table + Auto-calc Vertical Slice

## Goal

Change the running Tkinter ISO Hong Kong CSPF/HSPF screen from the
`NumericEntryRow` plus calculate-button MVP to table/grid input with
automatic calculation, while preserving existing calculation paths and
expected outputs.

## Scope

- Connect the task-161 `TableGrid` foundation to Hong Kong CSPF and HSPF.
- Add a small reusable Tkinter `after`-based auto-calc debounce helper.
- Display current CSPF/HSPF results without accumulating auto-calc history.
- Add vertical-slice tests and minimally align the final UX contract, manual
  smoke guide, and work plan.

## Non-goals

- No EN/AHRI/KS or region expansion.
- No core calculator, profile resolver, dispatcher, fixture, expected,
  skip, or xfail changes.
- No PyQt UI, Predict/Train, PyQt retirement, packaging, visual-token
  styling, or existing color changes.
- No TSV copy/paste, undo/redo, or full spreadsheet selection model.
- No `ACTIVE_DOCUMENTS.md`, `project_log.md`,
  `result_reports/memory/project_memory_seed.md`, or result-report lifecycle
  maintenance changes.

## Project Memory Recall Gate

Only the requested keywords were searched with `rg -n` in
`result_reports/memory/project_memory_seed.md`; the memory seed was not read
in full and was not modified.

Relevant evidence:

- Tkinter calculator work proceeds separately from the retained PyQt
  Predict/Train candidates, and PyQt calculator-only retirement remains a
  gated later decision.
- Auto-calc was previously selected as the final calculator action model.
- The existing calculator-only Tkinter direction must preserve the Hong Kong
  smoke results while moving toward final table-based UX.

The active final UX contract and task-161 report were used as the direct
owners for the new integration; memory remains supporting evidence only.

## Design Gate Summary

- The task-supplied boundary is sufficient for this vertical slice: connect
  only the existing Hong Kong CSPF/HSPF sections to the reusable grid.
- `ui_tk/auto_calc.py` owns callback scheduling only; section classes retain
  input assembly and existing resolver/dispatcher/calculator calls.
- `Iso16358Tab` owns composition of the latest metric result text so repeated
  auto-calc cannot append unbounded history.
- Visual-token styling, additional standards/regions, packaging, and source
  retirement remain deferred.

## Task Results

### Task 1 - Scope And Existing Structure

- Confirmed `IsoCspfSection` and `IsoHspfSection` previously created
  `NumericEntryRow` fields and explicit calculation buttons.
- Confirmed `TableGrid` supplies schema-backed text/numeric table access and
  changed-value callbacks, while `ResultPanel` already supplies `set_text()`.
- Limited the UI change to the current ISO 16358 / Hong Kong CSPF+HSPF
  surface.

### Task 2 - Auto-calc Helper

- Added `ui_tk/auto_calc.py` with `DebouncedAutoCalc`.
- Public operations are `schedule()`, `cancel()`, `flush_now()`, and
  `dispose()`, with a default 200 ms Tkinter `after` delay.
- The helper imports neither calculator core nor `TableGrid`; it only
  orchestrates callbacks and cancels pending work during disposal.

### Task 3 - Latest-result Composition

- Updated `ui_tk/tabs/iso16358_tab.py` to keep the latest text by metric and
  render it through `ResultPanel.set_text()`.
- Re-rendering a region clears old sections and result state before the new
  sections schedule their initial calculations.
- Existing `ResultPanel.append()`, `copy()`, and `clear()` APIs remain
  available; auto-calc sections no longer use append.

### Task 4 - CSPF Table And Auto-calc

- `IsoCspfSection` now uses one declared-capacity `TableGrid` and one
  `35_full`/`35_half` measurement grid.
- Preserved defaults `3500`, `3600`, `900`, `1700`, and `380`; the calculated
  default result remains `CSPF = 4.939`.
- Removed the CSPF calculation button and added public `recalculate_now()` as
  the deterministic test/manual hook.
- Missing or invalid numeric input reports
  `[CSPF 입력 오류] 숫자 입력을 확인하세요.` without invoking calculation.

### Task 5 - HSPF Table And Auto-calc

- `IsoHspfSection` now uses one rated-capacity `TableGrid` and one
  `7_full`/`7_half` measurement grid.
- Preserved defaults `6300`, `6300`, `1500`, `3200`, and `800`; the
  calculated default result remains `HSPF = 3.643`.
- Removed the HSPF calculation button and added public `recalculate_now()`.
- Missing or invalid numeric input reports
  `[HSPF 입력 오류] 숫자 입력을 확인하세요.` without invoking calculation.

### Task 6 - Tests

- Added `tests/test_ui_tk_iso_table_autocalc.py` for debounce behavior,
  PyQt-free import, grid/button surface, initial CSPF/HSPF results,
  non-accumulating latest results, changed-input recompute, invalid-input
  handling, and idempotent grid updates.
- During integration tests, an explicit-root defect in the task-161 adapter
  was exposed and corrected: each `StringVar` in `ui_tk/table_grid.py` is
  now created with `master=self`. This makes widget creation stable when
  tests construct isolated Tk roots.
- Existing table-grid, profile-resolver, and Tkinter foundation tests remain
  green; no expected, fixture, skip, or xfail marker was changed.

### Task 7 - Documentation And Work Plan

- Updated the final UX contract to mark the Hong Kong table/auto-calc slice
  complete and keep manual smoke as the next validation slice.
- Updated the manual smoke guide from calculate-button instructions to
  table/default auto-calc and latest-result behavior.
- Added task 162 to `docs/WORK_PLAN.md`; next recommended actions are:
  1. macOS manual UX smoke.
  2. Windows PyInstaller size measurement when a Windows host is available.
  3. Visual token/style adapter adoption, if needed.
  4. Tkinter standard/region expansion, if needed.
- PyQt calculator-only retirement remains held pending Windows packaging size
  measurement or a later explicit usability decision.

### Task 8 - Report And Memory Delta

- This full report records the vertical-slice behavior, verification, scope
  boundary, and one durable memory delta below.
- Result-report lifecycle maintenance is excluded because the prompt
  expressly prohibits active/archive/summaries moves. The metadata-only
  check found 8 active reports before this report was added; no lifecycle
  files were changed.

### Task 9 - Verification

- `python3 -B tools/check_code_structure.py`: PASS (`no findings`).
- `python3 -B -m py_compile ui_tk/auto_calc.py ui_tk/tabs/iso16358_tab.py ui_tk/sections/iso_cspf_section.py ui_tk/sections/iso_hspf_section.py tests/test_ui_tk_iso_table_autocalc.py`: PASS.
- Requested targeted test set: PASS (`40 passed`).
- `python3 -B -m pytest -q -rxXs`: PASS
  (`628 passed, 32 skipped, 19 xfailed`).
- Relative to the supplied `622 passed, 32 skipped, 19 xfailed` baseline,
  six vertical-slice tests were added; remaining xfail count is unchanged and
  no native abort occurred.

## Changed Files

- `ui_tk/auto_calc.py`
- `ui_tk/table_grid.py`
- `ui_tk/tabs/iso16358_tab.py`
- `ui_tk/sections/iso_cspf_section.py`
- `ui_tk/sections/iso_hspf_section.py`
- `tests/test_ui_tk_iso_table_autocalc.py`
- `docs/designs/2026-05-23-tkinter-calculator-final-ux-contract.md`
- `docs/guides/lightweight_calculator_tk_manual_smoke.md`
- `docs/WORK_PLAN.md`
- `result_reports/active/162_tkinter-iso-hk-table-autocalc-vertical-slice.md`

## Known Risks / Deferred Work

- The automated vertical slice is green, but the macOS manual UX smoke has
  not yet been executed.
- Tkinter table editing intentionally does not yet implement TSV clipboard,
  undo/redo, full Excel-like selection, or visual-token styling.
- Windows packaging size evidence is still unavailable, so PyQt source
  retirement is not authorized.

## Scope Compliance

- Core/profile/dispatcher execution paths and existing Hong Kong expected
  values were preserved.
- No prohibited PyQt, Predict/Train, visual-token wiring, color, packaging,
  test-marker, active-doc registry, project-log, or memory-seed changes were
  made.

## Commit / Push

- Source/docs/tests commit: `491340a` (`feat: wire Tkinter ISO tables with auto-calc`).
- Report commit: this report is committed separately after source verification.
- Push: `origin/work/ui-ux-ssot-adoption` after the report commit.

## Project Memory Delta

- type: decision
  topic: tkinter-iso-hk-table-autocalc-vertical-slice
  content: "Tkinter ISO Hong Kong CSPF/HSPF sections now use table/grid input and auto-calc, replacing the Entry row plus calculate-button MVP for this vertical slice while PyQt calculator retirement remains gated."
  keywords:
    - Tkinter
    - Hong Kong
    - CSPF
    - HSPF
    - auto-calc
  assertionStatus: observed
  source: result_reports/active/162_tkinter-iso-hk-table-autocalc-vertical-slice.md
