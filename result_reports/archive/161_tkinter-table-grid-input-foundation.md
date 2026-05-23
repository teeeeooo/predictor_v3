# 161. Tkinter Table/Grid Input Foundation

## Goal

Add reusable Tkinter table/grid input foundations for the final calculator UX
while leaving the current ISO sections, calculator execution, auto-calc, and
visual styling unchanged.

## Scope

- Confirm final UX/table/visual contract boundaries and current Tkinter MVP
  structure.
- Add a pure table/grid data model and a separate Tkinter `Entry`-grid
  adapter.
- Add focused pure-model and minimal Tk widget-adapter tests.
- Link the modules from the final UX contract and advance `docs/WORK_PLAN.md`.

## Non-goals

- No replacement or wiring of `IsoCspfSection`, `IsoHspfSection`, or
  `NumericEntryRow`.
- No calculator/core/profile/dispatcher call, auto-calc debounce, result
  panel change, visual-token wiring, or existing color/style change.
- No PyQt source retirement, Predict/Train work, new standards/regions,
  fixture/expected/skip/xfail edits, or packaging execution.
- No `ACTIVE_DOCUMENTS.md`, `project_log.md`,
  `result_reports/memory/project_memory_seed.md`, or result-report lifecycle
  maintenance changes.

## Project Memory Recall Gate

Only the user-specified keywords were searched with `rg -n` against
`result_reports/memory/project_memory_seed.md`; the seed was not read in
full and remains evidence below the prompt, rules, and active owner docs.

Relevant entries confirmed:

- Tkinter calculator direction proceeds separately from retained PyQt
  Predict/Train candidates; PyQt calculator-only retirement remains held.
- The table contract owns spreadsheet-like table UX behavior.
- Auto-calc alignment exists as a later direction rather than an entitlement
  to add recompute wiring in this slice.

Report 157 and the active final UX contract provide the direct table/grid
foundation decision. Report 160 confirms `ui_common/visual_tokens.py` exists
but current widgets are not yet migrated to it. The memory seed is not
modified.

## Design Gate Summary

### Confirmed Decisions

- A reusable Tkinter table input is divided into a pure model
  (`ui_tk/table_grid_model.py`) and a toolkit adapter
  (`ui_tk/table_grid.py`).
- The new component exists beside the current `NumericEntryRow` MVP; ISO
  section replacement is a later vertical-slice task.
- This slice implements schema, text storage, numeric validation state,
  snapshots, a changed-value callback hook, and basic Enter focus travel.

### Boundary And Deferred Work

- Pure model: no Tkinter, PyQt, calculator, profile, or external-library
  dependencies.
- Tk adapter: widget construction and callback propagation only; no core
  calculation, debounce, or styles.
- Deferred: integration with ISO sections, auto-calc, result/status surfaces,
  visual-token styling, TSV copy/paste, undo/redo, and full Excel-like
  selection/navigation.

## Task Results

### Task 1 - Contract And Existing Structure

- Confirmed final UX requires a table/grid with numeric validation and a
  `values_changed` callback, while current MVP still uses `NumericEntryRow`
  plus calculation buttons.
- Confirmed the common table contract distinguishes missing from invalid and
  permits invalid text to remain editable; the foundation therefore stores
  entered text and reports state instead of coercing or calculating.
- Confirmed `ui_tk/input_widgets.py`, existing ISO sections, and result panel
  continue to own the current MVP path without modification.
- Confirmed the visual-token foundation is available but must not be wired
  into widgets in this task.

### Task 2 - Pure Model

- Added `ui_tk/table_grid_model.py`.
- Public interface:
  `GridColumn`, `GridRow`, `GridCellState`, `TableGridModel`, and
  `parse_numeric_cell(value: str) -> float`.
- `TableGridModel` provides schema-ordered storage, `get_cell`, `set_cell`,
  `set_cells`, `cell_state`, `invalid_cells`, `as_text_table`, and
  `as_numeric_table`.
- Missing cells are reported as `GridCellState.MISSING`; non-empty values
  that cannot be parsed as finite numeric input are
  `GridCellState.INVALID`; both block `as_numeric_table()` with a clear
  exception.
- Numeric parsing supports trimming whitespace and removing commas only;
  there is no formula or profile-specific behavior.

### Task 3 - Tkinter Adapter

- Added `ui_tk/table_grid.py` with `TableGrid`, implemented as
  `ttk.Frame` containing row/header labels and editable `ttk.Entry` cells.
- Public adapter methods:
  `get_text_table`, `get_numeric_table`, `set_cell`, `focus_cell`,
  `invalid_cells`, `clear_validation_state`, and
  `set_values_changed_callback`.
- `StringVar` changes update the pure model; the callback fires only when
  the stored text actually changes. It performs no debounce or calculation.
- Enter moves focus through cells in row-major order as a minimal keyboard
  foundation; full spreadsheet navigation, copy/paste, selection, and undo
  remain deferred.
- Validation styling is intentionally not applied: validation is exposed by
  state/API only so that 160 visual tokens are not wired into current
  widgets in this slice.

### Task 4 - Tests

- Added `tests/test_ui_tk_table_grid_model.py` covering pure import
  independence, schema setup, changed/idempotent updates, fail-fast
  addresses, numeric parsing, missing/invalid distinction, and snapshots.
- Added `tests/test_ui_tk_table_grid.py` covering no PyQt import, Tk widget
  construction, cell round-trip, callback idempotence, and invalid state.
- Widget tests create a withdrawn Tk root and skip on hosts where Tk cannot
  initialize; no screenshot/pixel or calculator tests are added.
- Existing Tkinter foundation tests remain unmodified and pass.

### Task 5 - Documentation And Work Plan

- Updated `docs/designs/2026-05-23-tkinter-calculator-final-ux-contract.md`
  to identify the two foundation modules, state that existing sections remain
  unwired, and set the next slice to the debounce/helper foundation.
- Updated `docs/WORK_PLAN.md` with the 161 completion boundary and the ordered
  next actions: debounce/helper foundation, ISO Hong Kong vertical slice,
  macOS manual UX smoke, then Windows PyInstaller measurement when available.
- PyQt calculator-only source retirement remains held until the Tkinter final
  UX vertical-slice gate is satisfied.

### Task 6 - Report And Memory Delta

- This full report records the foundation boundary, public API, deferred
  integration work, verification, and next action.
- One durable procedure item is included under Project Memory Delta.
- Lifecycle maintenance is excluded because the prompt explicitly prohibits
  it; the metadata-only check found 7 active reports before this report,
  below the routine 8-12 report trigger.

### Task 7 - Verification

- `python3 -B tools/check_code_structure.py`:
  `code structure guard: OK (no findings)`.
- `python3 -B -m py_compile ui_tk/table_grid_model.py ui_tk/table_grid.py tests/test_ui_tk_table_grid_model.py tests/test_ui_tk_table_grid.py`:
  passed.
- `python3 -B -m pytest tests/test_ui_tk_table_grid_model.py tests/test_ui_tk_table_grid.py -q -rxXs`:
  `19 passed in 0.43s`.
- `python3 -B -m pytest tests/test_ui_tk_profile_resolver.py tests/test_ui_tk_calculator_foundation.py -q`:
  `15 passed in 0.45s`.
- `python3 -B -m pytest -q -rxXs`:
  `622 passed, 32 skipped, 19 xfailed in 2.22s`.
- Relative to the 160 baseline `603 passed, 32 skipped, 19 xfailed`,
  passed count increases by 19 for the new tests, xfail count remains 19,
  and no native abort occurred.

## Changed Files

- `ui_tk/table_grid_model.py` - pure schema/value/validation model.
- `ui_tk/table_grid.py` - Tkinter Entry-grid adapter and callback hook.
- `tests/test_ui_tk_table_grid_model.py` - pure model contract tests.
- `tests/test_ui_tk_table_grid.py` - minimal Tk widget-adapter tests.
- `docs/designs/2026-05-23-tkinter-calculator-final-ux-contract.md` -
  foundation paths and slice boundary update.
- `docs/WORK_PLAN.md` - completion record and next execution order.
- `result_reports/active/161_tkinter-table-grid-input-foundation.md` - this
  report.

## Known Failures / Risks

- The grid foundation is intentionally not reachable from the current
  calculator UI until the later ISO vertical slice connects it.
- The adapter exposes validation state but does not yet paint invalid/missing
  cells; styling must be a separately scoped adoption decision.
- Full Excel-like table behavior required by the long-term contract remains
  incomplete until later interaction slices.

## Next Suggested Action

Implement the Tkinter auto-calc debounce/helper foundation as a reusable,
unwired helper that can later subscribe to `TableGrid` changes in the ISO
Hong Kong vertical slice.

## Scope Compliance

- No edits were made to existing ISO sections, `ui_tk/input_widgets.py`,
  result panel, `ui_common/visual_tokens.py`, existing PyQt modules, core,
  profile/dispatcher, existing tests, `ACTIVE_DOCUMENTS.md`,
  `project_log.md`, or `project_memory_seed.md`.
- No calculator invocation, token styling, auto-calc implementation, source
  retirement, xfail/skip modification, or lifecycle maintenance occurred.

## Commit / Push

- Source/docs/test commit: `8a82866` (`feat: add Tkinter table grid
  foundation`).
- Report is committed separately after finalization and pushed to
  `origin/work/ui-ux-ssot-adoption`.

## Project Memory Delta

```yaml
- type: procedure
  topic: tkinter-table-grid-foundation
  content: "Tkinter table/grid input foundation is split into ui_tk/table_grid_model.py for pure schema and validation state plus ui_tk/table_grid.py for the Entry-grid adapter and changed-value callback; existing calculator sections and auto-calc remain unwired until later slices."
  keywords:
    - Tkinter
    - table grid
    - calculator-only
    - auto-calc
    - UI/UX SSOT
  assertionStatus: observed
  source: result_reports/active/161_tkinter-table-grid-input-foundation.md
```
