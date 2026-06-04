# 212 — BatchCaseTable Keep/Replace Preflight

## Goal

Decide whether the current `BatchCaseTable` should be kept and patched, absorbed into the existing `MetricInputTable` / `ExcelLikeTableController` pattern, or replaced with a reusable Tk batch table adapter before implementing Hong Kong CSPF batch table UX correction.

## Current State

- Branch: `main`, clean and up to date before report work.
- `WORK_PLAN.md` next action is `BatchCaseTable keep/replace preflight`.
- Reports 209-211 moved table UX rules back to owner docs and consolidated design-record indexing.
- Report 208 corrected batch entry to a `Multi 입력` dialog and removed the `CSPF Batch` metric tab, but retained `BatchCaseTable`.

This preflight does not modify code/tests/UI. It only records the implementation decision and next slice.

## BatchCaseTable Structure

Current `BatchCaseTable`:

- Builds a `tk.Frame` grid directly.
- Creates header cells as `tk.Label`.
- Creates input cells as `tk.Entry`.
- Creates result/status cells as `tk.Label`.
- Owns a `BatchTableModel`.
- Binds only `Ctrl/Cmd+V` paste on input entries.
- Rebuilds all row widgets on paste/add/remove.
- Has no separate interaction controller.
- Has no selection model, active cell model, undo stack, copy path, Delete/Backspace clear, Tab/Enter navigation contract, or replace-on-type state machine.

### Contract Check

| Requirement | Current state | Judgment |
| --- | --- | --- |
| One row per case | Supported by `BatchTableModel` rows | Keep |
| Input/result/status roles | Represented in `BatchColumnRole` | Keep, but revise status policy |
| Result/status read-only | Labels are non-editable | Partial; copy/selection behavior missing |
| TSV paste | Input-only paste exists | Partial; no selection model/atomic UX contract |
| TSV copy | Missing | NG |
| Delete/Backspace clear | Missing | NG |
| Ctrl/Cmd+Z undo | Missing | NG |
| Tab/Enter navigation | Native/default only, not contract-owned | NG |
| Click then type replace | Missing | NG |
| Rectangular selection | Missing | NG |
| Invalid row policy | Handler writes long error text into Status | Needs policy change |
| Auto-calc on edit | Missing; explicit Run Batch only | Needs correction for next slice |
| Dynamic row add/remove | Present | Keep concept, review UX |

## Existing Table Owner Analysis

### `MetricInputTable`

Reusable pieces:

- Bordered table frame with header, row header, editable, and static cell roles.
- Surface metadata consumed by `ExcelLikeTableController`.
- Batch value updates and change callback.
- Existing visual tokens and responsive layout.

Limits for batch:

- Shape is row header + fixed data columns, optimized for compact matrix inputs.
- Editable cells are the only dynamic value path.
- Static cells display `-`, not computed result text.
- Dynamic row count is not a current responsibility.
- It does not model mixed input/result columns per case row.

### `ExcelLikeTableController`

Reusable pieces:

- Rectangular selection.
- TSV copy/paste.
- Delete/Backspace clear.
- Undo.
- Tab/Enter and arrow navigation.
- Replace-on-type.
- Selection/edit state machine.

Limits for batch:

- It assumes editable positions from `table.field_key_for_address()`.
- Read-only/static cells are not part of selectable/copyable result surfaces in the current calculator binding.
- It is tied to table metadata shape exposed by `MetricInputTable`.

### `TableGrid` / `TableGridModel`

Reusable pieces:

- Toolkit-neutral row/column addressed text model.
- Numeric parsing/invalid state.
- Simple row/column grid idea.

Limits for batch:

- `TableGrid` is input-only and visually lighter than current tokenized table surfaces.
- No roles for result/read-only/status.
- No Excel-like controller.
- No dynamic row add/remove in the current model.

## Options

| Option | Summary | Pros | Risks / Costs | Judgment |
| --- | --- | --- | --- | --- |
| A. Patch current `BatchCaseTable` | Add selection/copy/delete/undo/navigation directly into current class. | Smallest file count; keeps current UI shell. | Turns `BatchCaseTable` into a mixed renderer/controller/model wrapper; duplicates `ExcelLikeTableController`; high regression risk. | Not recommended. |
| B. Absorb into `MetricInputTable` + `ExcelLikeTableController` | Force batch into existing matrix table. | Reuses strongest existing interaction controller. | Requires stretching `MetricInputTable` into dynamic row, result-column, and read-only selectable roles; likely damages compact matrix owner. | Not recommended for first correction. |
| C. Extend `TableGrid` | Make `TableGrid` batch-compatible. | Builds on row/column model; may become reusable. | Current `TableGrid` is input-only and not token/contract complete; would still need a controller and role model. | Backup only if D becomes too broad. |
| D. New reusable Tk batch table adapter | Replace `BatchCaseTable` surface with a batch-oriented table adapter and controller, while keeping batch spec/handler/model concepts. | Fits row-per-case shape; can implement Excel-like contract cleanly; supports future CSPF/HSPF/EN/AHRI/KS batch; avoids overloading `MetricInputTable`. | More new code than A; must keep adapter small and behavior-tested. | Recommended. |

## Recommendation

Use **Option D**.

Create a reusable Tk batch table surface/controller that is batch-oriented but not Hong Kong-specific. Keep these pieces:

- `BatchColumnSpec`
- `BatchColumnRole`
- `BatchProfileSpec`
- `HongKongCspfBatchHandler`
- row-to-core calculation path

Revise or replace:

- `BatchCaseTable` as the current UI surface.
- `BatchCalculationController` if auto-calc replaces explicit Run Batch.
- Hong Kong CSPF batch spec status/result columns.

Option C is the fallback if the implementation can reuse `TableGridModel` cheaply without broad refactor. Option A should be avoided because it hides an interaction-controller rewrite inside a single widget class. Option B should be avoided because it risks damaging the stable single-case matrix input surface.

## Next Implementation Slice

### Candidate Files

Modify:

- `ui_tk/batch_models.py`
- `ui_tk/batch_case_table.py` or replace with `ui_tk/batch_table.py`
- `ui_tk/batch_controller.py`
- `ui_tk/sections/hong_kong_cspf_batch_section.py`
- `ui_tk/sections/hong_kong_cspf_batch_spec.py`
- focused Tkinter batch tests

Potential new file:

- `ui_tk/batch_table_controller.py` for Excel-like interaction behavior.

### Preserve

- `HongKongCspfBatchHandler` still calls the existing profile resolver, dispatcher, and core calculator.
- Batch model/spec remain toolkit-neutral.
- Batch remains a dialog opened from Hong Kong CSPF `Multi 입력`.
- Core calculator, region config, fixture/golden values stay unchanged.

### Proposed Behavior

- Default rows: 5 blank/starter rows, not 1 row.
- Status column: remove from the visible table for Hong Kong CSPF first slice.
- Result columns: `CSPF`, `CSEC`; read-only/selectable/copyable.
- Input columns: `Case`, `Declared`, `35 Full Cap`, `35 Full Power`, `35 Half Cap`, `35 Half Power`.
- Calculation trigger: debounced auto-calc on input edits/paste/clear.
- Blank row: result cells blank.
- Partial/invalid row: result cells blank; no repeated long error text in table cells.
- Valid row: result cells populated and must match single-case CSPF.
- Optional dialog-level status: compact summary such as `3 valid / 2 blank / 0 invalid`, not per-cell tracebacks.
- Add/remove row controls can remain, but row removal should keep at least one row.

### Excel-Like Behavior Scope

Next implementation should include:

- rectangular selection;
- Ctrl/Cmd+C TSV copy including read-only result cells;
- Ctrl/Cmd+V TSV paste into editable cells only;
- Delete/Backspace clear for editable selected cells;
- Ctrl/Cmd+Z undo;
- Tab/Shift+Tab/Enter/Shift+Enter navigation;
- click then type replace-on-type;
- read-only result cells selectable/copyable but skipped by edit/paste/delete/undo.

If any behavior cannot be automated safely in the slice, it must be recorded as a gap and covered by Windows manual smoke.

## Validation Plan For Next Implementation

Automatic tests should be behavior-focused, not class-name forced:

- Hong Kong CSPF batch spec has no visible `Status` column.
- Default model/table seeds 5 rows.
- Blank row leaves `CSPF` and `CSEC` blank.
- Invalid/partial row leaves result blank and does not abort other rows.
- Valid row populates `CSPF` and `CSEC`.
- Batch row result equals existing single-case CSPF core path.
- Paste parsing/apply helper clips to editable cells and does not mutate result cells.
- Copy helper includes selected read-only result cells.
- Delete/Backspace helper clears editable cells only.
- Undo restores a paste/clear/edit group.
- Result/read-only cells reject direct edits.

Manual Windows GUI smoke should cover:

- Excel TSV paste into multiple rows.
- Copy from input+result rectangle.
- Delete/Backspace clear.
- Tab/Enter movement.
- Click then type replace.
- Result columns are read-only.
- Row/grid lines are uniform.
- Input changes auto-calculate.
- Dialog open/close does not resize the main calculator window.

Do not run full project pytest for this slice unless requested. Use focused batch/model/UI tests and `tools/check_code_structure.py`.

## Excluded

- No code/test changes in this preflight.
- No UI implementation change.
- No core/region/golden/fixture changes.
- No HSPF/EN/AHRI/KS batch implementation.
- No docs/designs body edits.

## Next Action

Implement batch table UX correction using Option D: a reusable Tk batch table adapter/controller that satisfies the Excel-like contract while preserving the existing batch spec/handler/core calculation boundary.

## Verification

- `git diff --check`: passed.
- `python3 -B tools/check_code_structure.py`: passed with existing `ui_tk/sections/bin_detail_panel.py` soft LOC warning.
- `git status --short`: expected report and `WORK_PLAN.md` changes only.

Not run:

- `pytest`: preflight/report only; no code/test changes.
- GUI smoke: no UI code changes.
