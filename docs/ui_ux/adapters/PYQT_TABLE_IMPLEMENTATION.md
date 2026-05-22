# PyQt Table Implementation Adapter

## Role and scope

- This document is the **PyQt5-specific implementation contract** for
  spreadsheet-like table surfaces.
- It assumes the toolkit-agnostic baseline in
  `../03_SPREADSHEET_TABLE_UX_CONTRACT.md` and the common UX
  principles in `../00_UI_UX_SYSTEM.md`.
- It does **not** describe Tkinter behavior. For Tkinter, see
  `TKINTER_TABLE_ADAPTER.md`.
- The historical PyQt source at
  `../_source/SPREADSHEET_TABLE_CONTRACT_legacy_pyqt.md` is the
  reference this adapter was derived from. That source file is
  history; this adapter is the active PyQt rule set.

This adapter applies to every PyQt5 table-shaped widget in a project
that has selected PyQt5 under `../01_TOOLKIT_SELECTION_POLICY.md`,
including helpers, fixtures, and test harnesses.

## 1. Required widget pattern

- **View**: `QTableView`. `QTableWidget` is **forbidden** for any
  new table, helper, fixture, or test harness.
- **Model**: subclass `QAbstractTableModel`. Do not subclass
  `QStandardItemModel` for app tables.
- **Editor / dropdown / custom paint**: `QStyledItemDelegate`.
  Direct `setCellWidget()` is **forbidden** for any new code.
- **Selection**: use the view's built-in `QItemSelectionModel`. Do
  not re-implement selection state in the model.
- **Headers**: column units and labels live on the header (or table
  title). Do not put per-cell unit choosers inside the body of the
  table.

`QTableWidget` and `setCellWidget()` short-cuts produce per-cell
widgets that defeat scrolling, paste-rectangle handling, and
delegate-based validation. They are not acceptable trade-offs.

## 2. Editor lifecycle (1-click open)

- A dropdown cell opens on a **single click**, not on double-click.
  Inside the delegate's `createEditor` (or `editorEvent`), schedule
  the popup with `QTimer.singleShot(0, editor.showPopup)`.
- `time.sleep` for UI event timing is **forbidden**. Always use
  `QTimer.singleShot` or another Qt-event-loop-aware primitive.
- A mouse press inside an open editor must not bubble up as a
  generic cell click that re-triggers selection or paste. Swallow the
  event in `editorEvent` when handling the dropdown open.
- Delegate change handler names stay stable across versions. Renames
  like `_apply_mapping` ↔ `on_dropdown_changed` surface as late
  `AttributeError`s in paste / autofill paths.

## 3. Persistent editors and `setCellWidget`

- Do **not** rely on persistent editors to make a column "always
  look like a combo box". Use a delegate that paints the right
  visual and opens an editor on interaction.
- Do **not** call `setCellWidget()` to embed widgets inside cells.
  It breaks model-driven copy / paste, undo, and validation.

## 4. Path isolation: edit vs paste vs cascade

Three event sources reach the model and they must not be conflated.

- **Cell edit path**: `setData` (from the delegate's `setModelData`
  or inline edit). One cell at a time. Triggers validation,
  autofill, and cascade hooks for that cell only.
- **Paste path**: a dedicated `on_paste_complete(rows, cols,
  values)` (or equivalent) handler. Operates on a rectangle of cells
  in one call. Triggers validation and autofill **once per affected
  row**, not once per cell.
- **Cascade / autofill path**: a dedicated handler that fires only
  when a master dropdown value changes. Does not run on paste
  row-by-row unless the master cell itself was pasted.

Why this matters: mixing paste into the cell-change path either
silently discards pasted values or triggers autofill cascades per
pasted cell and produces feedback cycles. Keep the three paths
distinguishable in the diff even when they share helpers.

## 5. Copy / paste (Qt-side)

- Clipboard format is **TSV**. Trailing `\n` after the last row is
  allowed and ignored on paste.
- Copy of a non-rectangular selection: either expand to the bounding
  rectangle or reject the copy. Never emit jagged TSV.
- Paste parses TSV. Non-TSV clipboard payload is rejected without
  mutating any cell.
- Pasted values go through the same validator used by the cell edit
  path. Invalid pasted cells are marked but do not abort the paste.
- Paste larger than selection: write outward from top-left; drop
  out-of-bounds cells silently.
- Paste smaller than selection: repeat a single-cell source to fill
  the selection; do not auto-repeat a multi-cell source.

## 6. Model data, display data, and edit data

- `Qt.DisplayRole`, `Qt.EditRole`, and `Qt.UserRole` are
  intentionally separate.
  - `DisplayRole` returns the **rendered** string (compact numeric
    formatter, units, etc.).
  - `EditRole` returns the **raw** value the editor expects (number,
    bool, plain string).
  - `UserRole` is for adapter-specific metadata (validation state,
    source row id, etc.).
- Painters use `DisplayRole`; delegates' editors use `EditRole`.
- Do not encode validation state into the `DisplayRole` string.
  Validation state belongs in a separate role consumed by the
  delegate's paint logic.

## 7. Validation coloring (model / delegate split)

- Validators live on the **delegate or model**. Painters do not
  decide what counts as invalid.
- The model stores the value as-is even when invalid; it exposes the
  validity through a dedicated role.
- The delegate's `paint` reads that role and renders the error
  indicator (border or background derived from
  `color.bg.cell.invalid` / `color.danger`).
- Read-only / auto / disabled state is also exposed through a role,
  not inferred at paint time.

## 8. Keyboard event handling

- Tab / Shift+Tab / Enter / Shift+Enter / Arrow / Esc / Delete /
  Backspace behavior matches
  `../03_SPREADSHEET_TABLE_UX_CONTRACT.md`.
- Implement table-level shortcuts (Ctrl+C, Ctrl+V, Ctrl+Z, Delete)
  on the view via key event handlers or `QShortcut` instances scoped
  to the view, not on the application-global level.
- Editors must not swallow Tab / Enter without also moving the
  active cell. The view's navigation must remain reachable from
  inside the editor when the editor commits.

## 9. `blockSignals` discipline

- Any code path that mutates the model and would otherwise re-enter
  `dataChanged` or change handlers must wrap the mutation in
  `try / finally`:

  ```python
  table.blockSignals(True)
  try:
      # batch mutations
  finally:
      table.blockSignals(False)
  ```

- `try / finally` is **required**, not optional. A bare
  `blockSignals(True)` / `blockSignals(False)` pair anywhere in the
  UI tree is a defect.
- Keep the signal-blocked window short. For long batches, release
  `blockSignals` and re-emit `dataChanged` once at the end.

## 10. Test setup

- Table widgets are testable headlessly via the offscreen Qt
  platform plugin: set the environment variable
  `QT_QPA_PLATFORM=offscreen` for the test process.
- Tests should drive selection, paste, delete, and undo through the
  same code paths the user hits — not by calling private helpers.
- Fixtures that create a table for a test must use the offscreen
  platform plugin so they run in CI without a display.

## 11. Table review checklist (before commit)

- [ ] View is `QTableView`; model subclasses `QAbstractTableModel`.
      No `QTableWidget`.
- [ ] No `setCellWidget()` was introduced.
- [ ] 1-click editor opens via `QTimer.singleShot(0,
      editor.showPopup)`. No `time.sleep` for UI timing.
- [ ] Edit, paste, and cascade paths are distinguishable in the
      diff; paste does not enter the cell-change handler.
- [ ] Copy emits TSV; paste accepts TSV and rejects non-TSV payloads.
- [ ] Delete / Backspace clears every editable cell in the selection
      and skips read-only / disabled cells.
- [ ] An undo group covers each user action; Ctrl+Z reverts it; the
      undo stack is reset on data-context change.
- [ ] Navigation: Tab / Shift+Tab / Enter / Shift+Enter behave as
      specified in the common contract.
- [ ] Invalid numeric cells are visually marked but do not block
      other edits.
- [ ] Every `blockSignals(True)` is paired with a
      `blockSignals(False)` in `try / finally`.
- [ ] DisplayRole vs EditRole are distinct; validation state lives
      in its own role.
- [ ] If the helper exposes a fixture for tests, the fixture uses
      `QT_QPA_PLATFORM=offscreen`.

## 12. Related documents

- `../00_UI_UX_SYSTEM.md` — common UX principles.
- `../01_TOOLKIT_SELECTION_POLICY.md` — when to choose PyQt5.
- `../02_DESIGN_TOKENS_AND_LAYOUT.md` — tokens and layout.
- `../03_SPREADSHEET_TABLE_UX_CONTRACT.md` — common table UX.
- `TKINTER_TABLE_ADAPTER.md` — Tkinter equivalent for existing apps.
- `../_source/SPREADSHEET_TABLE_CONTRACT_legacy_pyqt.md` —
  historical PyQt-only source that this adapter was derived from.
  Reference only; this adapter is the active rule set.
