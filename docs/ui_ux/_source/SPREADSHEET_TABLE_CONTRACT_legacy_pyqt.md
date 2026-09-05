# Spreadsheet-like Table UI Contract

This document is the **single active owner** for PyQt table UI behavior
in this repository. Every table-shaped surface — Train/Predict tables,
Calculator UI tabs (AHRI, EN14825, ISO16358, KS C 9306, AS/NZS), and
any future helper / preview / diagnostic table — must satisfy this
contract.

> The original V2 trial-and-error material in
> `docs/archive/skills_v2_patterns.md` is **source / history only**. It
> is not the active contract. When archive guidance and this document
> disagree, this document wins.

## 1. Purpose

- Establish a single spreadsheet-like UX bar across the whole app so
  the agent and reviewers can apply the same rules everywhere.
- Lock the implementation pattern (`QTableView` + `QAbstractTableModel`
  + `QStyledItemDelegate`) so that future tables do not regress to
  `QTableWidget` / `setCellWidget` shortcuts.
- Centralize the copy / paste / clear / undo / navigation / validation
  rules so individual design docs (calculator, train UI, future
  surfaces) only have to describe their own shape on top of this
  baseline.

### 1.1 Excel-like UX is the project baseline

This project's table UX baseline is **Excel-like behavior**. The
working assumption is that every user already operates a spreadsheet
(Excel / Google Sheets / Numbers) every day and brings that muscle
memory to every table-shaped surface in this app.

- The default expectation for any table in `ui/**` is "behaves like a
  small Excel sheet". When a user clicks, types, copies, pastes, hits
  Enter, hits Tab, or hits Delete, the response must match what Excel
  would do.
- Implementations must not break that muscle memory — non-Excel
  behaviors (e.g. Enter moving right, Tab moving down, Delete doing
  nothing, no Ctrl+C export) are contract violations even when the
  underlying calculator still works.
- Any existing table whose behavior diverges from this Excel-like
  baseline is treated as a **contract alignment target**, not as an
  accepted exception. Divergences are tracked and converted in
  follow-up slices.

The Required UX baseline below (§3) is the minimum Excel-like surface
every table must implement.

## 2. Scope

- Applies to every legacy Qt binding table-shaped widget in `ui/**`, including
  helpers, fixtures, and test harnesses.
- Applies to read-only tables (display-only result grids) for the
  layout, selection, and copy rules; edit-related rules are no-ops
  there.
- Does **not** apply to non-table widgets (QFormLayout-based forms,
  QListWidget, etc.).
- Does **not** add new rules to the calculator engine, region config,
  ML feature schema, or calculator result schema. Adapter and core
  layers stay separate.

## 3. Required UX baseline

Every table behaves like a small spreadsheet from the user's point of
view. The following is the minimum **Excel-like** behavior every
table must implement; individual tables may add features as long as
they do not break the baseline.

### 3.1 Excel-like keyboard baseline (must-have)

| Shortcut | Behavior |
| --- | --- |
| `Ctrl+C` | Copy the selected range as TSV (tab between columns, `\n` between rows) to the OS clipboard. |
| `Ctrl+V` | Paste a TSV payload from the clipboard onto the current selection, anchored at the top-left cell. |
| `Delete` / `Backspace` | Clear the contents of every editable cell in the current selection. |
| `Ctrl+Z` | Undo the most recent cell edit / paste / clear group. |
| `Tab` | Move the active cell **one column to the right**. |
| `Shift+Tab` | Move the active cell **one column to the left**. |
| `Enter` / `Return` | Move the active cell **one row down**. |
| `Shift+Enter` / `Shift+Return` | Move the active cell **one row up**. |

Navigation wrap / clamp behavior is specified in §10. Copy / paste
contract details are in §7, Delete behavior in §8, undo in §9.

### 3.2 Other Excel-like expectations

- Cell selection: single cell, contiguous range, and Ctrl-click
  multi-select work the same way they do in Excel / Google Sheets.
- Copy with `Ctrl+C` puts a TSV (tab-separated, `\n`-terminated)
  representation of the selected range on the clipboard.
- Paste with `Ctrl+V` from Excel / Sheets / a TSV string fills the
  currently selected range from the top-left corner outward,
  multi-cell paste supported.
- `Delete` and `Backspace` clear the contents of every selected cell
  (subject to the column being editable).
- `Ctrl+Z` undoes the most recent cell edit / paste / clear sequence
  for that table. Redo support (`Ctrl+Y` / `Ctrl+Shift+Z`) is
  recommended but optional.
- `Tab` moves the active cell one column right (wrapping to the next
  row at the end); `Shift+Tab` reverses it. `Enter` moves the active
  cell one row down (wrapping to the next column at the end);
  `Shift+Enter` reverses it.

Tables that deviate from this baseline (e.g. Enter moving sideways,
Delete being a no-op, no Ctrl+C handler) are contract alignment
targets and must be brought into compliance in a follow-up slice.
They are not grandfathered exceptions.
- Read-only / auto-computed cells are visually distinguishable from
  user-editable cells. Background-color conventions defined in
  `docs/architecture/project_architecture.md` §3.3 (white / gray /
  green) remain the project default.
- Numeric cells that fail validation are visually marked (e.g. red
  border or pale-red background) without blocking further editing.

## 4. Required implementation pattern

These are non-negotiable. They strengthen, not replace, the AGENTS.md
UI guardrail.

- View: `QTableView`. **`QTableWidget` is forbidden** for any new
  table, helper, fixture, or test harness.
- Model: subclass `QAbstractTableModel`. Do not subclass
  `QStandardItemModel` for app tables.
- Editor / dropdown / custom paint: `QStyledItemDelegate`. **Direct
  `setCellWidget()` is forbidden** for any new code.
- Selection: use the view's built-in `QItemSelectionModel`. Do not
  re-implement selection state in the model.
- Headers: column units / labels live on the header (or the table
  title). Per-cell unit choosers are forbidden — see the
  calculator-specific design doc for the calculator surfaces.

## 5. Editor lifecycle (1-click dropdown)

- 1-click open: inside the delegate's `createEditor` (or
  `editorEvent`), schedule the popup with
  `QTimer.singleShot(0, editor.showPopup)`. The editor opens on a
  single click instead of requiring a double-click.
- `time.sleep` for UI event timing is forbidden. Always use
  `QTimer.singleShot` or another Qt-event-loop-aware primitive.
- Mouse press inside an editor must not bubble up as a generic cell
  click that re-triggers selection or pastes. Swallow the event in
  `editorEvent` when handling the dropdown open.
- Handler names must stay stable. Do not rename a delegate's change
  handler between versions (`_apply_mapping()` vs
  `on_dropdown_changed()`) — those drifts surface as late
  `AttributeError`s in paste / autofill paths.

## 6. Path isolation: edit vs paste vs cascade

Three event sources reach the model and they must not be conflated.

- Cell edit path: `setData` (from the delegate's `setModelData` or
  inline edit). One cell at a time. Triggers validation, autofill, and
  cascade hooks for that cell only.
- Paste path: a dedicated `on_paste_complete(rows, cols, values)` (or
  equivalent) handler. Operates on a rectangle of cells in one call.
  Triggers validation and autofill **once per affected row** rather
  than once per cell.
- Cascade / autofill path: a dedicated handler that fires only when a
  master dropdown value changes. Does not run on paste row-by-row
  unless the master cell itself was pasted.

Why this matters: V2 mixed paste into the cell-change path and ended
up either silently discarding pasted values or triggering autofill
cascades per pasted cell, which caused infinite cycles. The three
paths stay separate even if they share helpers.

## 7. Copy / paste contract

- Clipboard format: **TSV** (tab between columns, `\n` between rows).
  Trailing `\n` after the last row is allowed and ignored on paste.
- Copy of N×M selection always emits an N×M TSV grid; copy of a
  non-rectangular selection is forbidden — the view either expands the
  selection to the bounding rectangle or rejects the copy.
- Paste from clipboard parses TSV. If the clipboard payload does not
  parse as TSV, the paste is rejected without modifying any cell.
- Pasted values are coerced through the same validator used by the
  cell edit path. Invalid cells in the pasted grid are marked but do
  not abort the paste — other valid cells still land.
- Paste size larger than the selection: paste starts at the top-left
  of the selection and writes outward; out-of-bounds rows / columns
  are silently dropped. This must be the same behavior in every table.
- Paste size smaller than the selection: paste is repeated to fill the
  selection rectangle only if the source is a single value (Excel /
  Sheets behavior). Multi-cell source pastes are not auto-repeated.

## 8. Clear behavior (Delete / Backspace)

- `Delete` and `Backspace` clear every editable cell in the current
  selection. Read-only / auto cells are skipped.
- Clearing emits a single undo group covering all affected cells.
- Clearing a master dropdown clears its dependent auto cells using
  the cascade path — the cascade path owns the dependent reset.

## 9. Undo / redo

- Each table maintains an internal undo stack of cell mutations. A
  single user action (one edit, one paste, one clear) produces a
  single undo group.
- `Ctrl+Z` reverses the most recent undo group, `Ctrl+Y` /
  `Ctrl+Shift+Z` redoes it.
- Undo state is local to the table. Cross-table undo is not in scope.
- The undo stack must be cleared when the underlying data context
  changes (e.g. loading a new file or switching profiles).

## 10. Navigation

- `Tab` / `Shift+Tab`: move one column horizontally with wrap-around to
  the next / previous row.
- `Enter` / `Shift+Enter`: move one row vertically with wrap-around to
  the next / previous column.
- Arrow keys: standard cell-by-cell navigation.
- Wrap-around at the table boundary is allowed; jumping out of the
  table (focus loss) only happens on `Esc`.

## 11. Numeric validation and invalid-cell display

- Numeric columns declare their validator (range, integer / float,
  required positivity) on the delegate or model.
- Invalid values are stored as-is in the model and marked with a
  visual error indicator (border or background) until the user fixes
  them.
- Calculator action paths read the model through a validator helper
  that fails fast if any required-positive cell is invalid; the table
  does not block the user from editing other cells in the meantime.
- Validators are **owned by the delegate / model**, not by the
  cell-paint code. Painters only render the error indicator.

## 12. `blockSignals` discipline

- Any code path that mutates the model and would otherwise re-enter
  `dataChanged` / change handlers must wrap the mutation in:

  ```python
  table.blockSignals(True)
  try:
      # batch mutations
  finally:
      table.blockSignals(False)
  ```

- `try/finally` is **required**, not optional. A bare `blockSignals(True)`
  / `blockSignals(False)` pair anywhere in `ui/**` is a defect.
- The signal-blocked window must stay short. Long batch operations
  must release `blockSignals` and re-emit `dataChanged` at the end of
  the batch.

## 13. Table helper / test harness checklist

When you add or modify a table helper (custom model, delegate, paste
handler) or a test harness for a table, walk through this checklist
before commit.

- [ ] The new code uses `QTableView` + `QAbstractTableModel`, never
      `QTableWidget`.
- [ ] No `setCellWidget()` calls were introduced.
- [ ] Any 1-click editor opens via `QTimer.singleShot(0,
      editor.showPopup)`. No `time.sleep` was used to time UI events.
- [ ] The edit, paste, and cascade paths are distinguishable in the
      diff; paste does not enter the cell-change handler.
- [ ] Copy emits TSV; paste accepts TSV and rejects non-TSV payloads.
- [ ] Delete / Backspace clears every editable cell in the selection
      and skips read-only cells.
- [ ] An undo group covers each user action; `Ctrl+Z` reverts the
      action; the undo stack is reset on data-context change.
- [ ] Navigation: Tab / Shift+Tab / Enter / Shift+Enter behave as
      described in §10.
- [ ] Invalid numeric cells are visually marked but do not block
      other edits.
- [ ] Every `blockSignals(True)` is paired with a `blockSignals(False)`
      in `try/finally`.
- [ ] The helper does not import calculator core, region config, or
      ML feature schema directly.
- [ ] If the helper exposes a fixture for tests, the fixture uses the
      offscreen Qt platform plugin (`QT_QPA_PLATFORM=offscreen`).

## 14. Relationship to other documents

- `AGENTS.md` is the current always-on repository contract and routes UI work
  to the repository-local `ui-surface` Skill.
- `.agents/skills/ui-surface/SKILL.md` routes active table work to the current
  shared `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md`. This legacy PyQt
  source is historical evidence only when that older implementation context is
  specifically needed.
- `docs/architecture/project_architecture.md` §3.3: continues to be the
  owner of background-color conventions, calculator boundary, and
  cascade autofill state-machine rules. The spreadsheet-behavior
  details (copy / paste / undo / navigation / numeric validation /
  paste path isolation / 1-click editor) live here.
- `docs/designs/2026-05-17-calculator-horizontal-table-input-ui.md`:
  defines calculator-specific table shape (columns / rows / units) and
  the AHRI / EN14825 migration order; relies on this contract for
  behavior.
- `docs/archive/skills_v2_patterns.md`: source / history only. The
  active rules promoted from there are:
  - 1-click dropdown via `QTimer.singleShot` and `editorEvent`.
  - `time.sleep` for UI timing is forbidden.
  - Paste path must be separated from the cell-change path
    (`on_paste_complete` style).
  - Dropdown change handler names must stay stable; renaming surfaces
    as `AttributeError` in paste / autofill paths.
  - `blockSignals` must be wrapped in `try/finally`; cascade
    sequencing is data lookup → signal-blocked write → UI state.
  - Master-dropdown is the sole owner of auto-column lock/unlock
    state.
  - Project-wide `QTableWidget → QTableView + QAbstractTableModel`
    transition; new tables stay on the new pattern.
