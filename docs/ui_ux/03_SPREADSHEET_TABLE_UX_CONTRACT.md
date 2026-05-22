# 03. Spreadsheet-like Table UX Contract

## Role and scope

- This document is the **toolkit-agnostic UX contract** for every
  spreadsheet-like (multi-row, multi-column, editable) table surface
  in any project in this organization.
- It describes what the user sees and does, not how the toolkit
  implements it.
- Framework-specific rules live in:
  - `adapters/PYQT_TABLE_IMPLEMENTATION.md`
  - `adapters/TKINTER_TABLE_ADAPTER.md`
- The historical reference at
  `_source/SPREADSHEET_TABLE_CONTRACT_legacy_pyqt.md` was a PyQt-only
  contract from a prior project. It is **source / history only**;
  this document is the active contract.

A "table-shaped" surface means a 2D grid the user can read across
columns and down rows. Single-column lists and form layouts are
**not** covered here.

## 1. Baseline: behaves like a small Excel sheet

Users come to every table with spreadsheet muscle memory (Excel,
Google Sheets, Numbers). The table must respond the way a
spreadsheet would for the actions below. Behaviors that diverge from
this baseline are contract violations, not exceptions.

## 2. Selection

- **Single click** on a cell selects exactly that cell and makes it
  the active cell.
- **Click and drag** selects a contiguous rectangular range.
- **Shift + click** extends the current selection to a contiguous
  range anchored at the previously active cell.
- **Ctrl + click** toggles individual cells in or out of the
  selection (non-contiguous selection).
- The active cell is visually distinct from the rest of the
  selection.
- A click on a header selects the row or column where supported.

## 3. Editing entry

- With a cell selected, **typing immediately replaces** the existing
  value and enters edit mode. The first keystroke is the first
  character of the new value.
- **Double click**, **F2**, or an explicit "edit" affordance enters
  edit mode without clearing the existing value, placing the cursor
  inside the current value. Whether to support this in addition to
  type-to-replace is a per-project choice; type-to-replace is
  required.
- **Esc** during editing cancels the edit and restores the prior
  value.
- **Enter** during editing commits the value and moves the active
  cell (see §6).
- The editor for a cell is determined by the column. Numeric, text,
  and drop-down cells each use the appropriate editor.

## 4. Copy and paste

- **Ctrl + C** copies the selected range to the OS clipboard as
  **TSV** (tab between columns, `\n` between rows). A trailing `\n`
  after the last row is allowed.
- A copy of an N×M selection always emits an N×M TSV grid. Copy of
  a non-rectangular selection is forbidden; the table either expands
  to the bounding rectangle or rejects the copy.
- **Ctrl + V** pastes TSV from the clipboard onto the current
  selection, anchored at the **top-left** cell of the selection.
- Paste larger than the selection: the paste starts at the top-left
  of the selection and writes outward; cells past the table
  boundaries are silently dropped.
- Paste smaller than the selection: a **single-cell** source is
  repeated to fill the selection (Excel behavior); a multi-cell
  source is **not** auto-repeated.
- Paste of a non-TSV payload is rejected without modifying any cell.
- Pasted values go through the same per-column validator as inline
  edits. Invalid pasted cells are marked but do not abort the paste;
  other valid cells still land.

## 5. Clear (Delete / Backspace)

- **Delete** and **Backspace** clear the contents of every editable
  cell in the current selection.
- Read-only / auto / disabled cells in the selection are skipped.
- Clearing produces a single undo group covering all affected cells.
- After clearing, the active cell remains selected; the selection is
  not collapsed unless the user explicitly clicks elsewhere.

## 6. Navigation

- **Tab** moves the active cell one column to the right. At the end
  of a row, it wraps to the first editable cell of the next row.
- **Shift + Tab** moves one column to the left, with reverse
  wrap-around.
- **Enter** / **Return** moves the active cell one row down. At the
  bottom of a column, it wraps to the first row of the next column.
- **Shift + Enter** / **Shift + Return** moves one row up with
  reverse wrap-around.
- **Arrow keys** move one cell at a time in the corresponding
  direction; they do not wrap by default.
- **Esc** clears any in-progress edit and removes focus from the
  cell editor, returning focus to the cell.
- Focus leaves the table only on **Esc** at the cell level or
  explicit Tab-out via a keyboard shortcut handled at the window
  level.

## 7. Undo

- **Ctrl + Z** undoes the most recent edit, paste, or clear as a
  single group.
- Each user action (one edit, one paste, one clear) is a single undo
  group, no matter how many cells it touched.
- Redo (**Ctrl + Y** / **Ctrl + Shift + Z**) is recommended but
  optional.
- The undo stack is local to the table. Cross-table undo is out of
  scope.
- The undo stack is cleared when the underlying data context changes
  (loading a new file, switching profiles).

## 8. Cell states

Every table makes the following states visually distinguishable:

- **Editable**: default appearance.
- **Read-only / auto**: distinct background and a foreground that
  signals "not user-edited". Read-only cells do not accept edits,
  paste writes, or delete clears.
- **Disabled / inactive**: foreground dimmed; the cell is skipped
  by every editing path (edit, paste, delete, undo target).
- **Invalid value**: the cell holds a value that fails its
  validator. Marked with an indicator (border or background) but
  still editable.
- **Empty**: the cell holds no value. This is a distinct state from
  "invalid value" and must not be conflated.

Specifically:

- "Empty" is not the same as "zero" and not the same as "invalid".
- A disabled cell is excluded from edit, paste, delete, and from
  contributing to copy unless the project explicitly includes
  disabled cells in copy.
- A read-only cell is included in copy as its rendered value but
  excluded from paste and clear.

## 9. Numeric validation display

- Numeric columns declare their validator (range, integer / float,
  required positivity).
- Validators belong to the column, not to the painter. Painters only
  render an indicator.
- An invalid value is stored as-is and marked. The user can keep
  editing other cells; the table does not block further input.
- Code paths that consume the table's values (calculation, export)
  use a single helper that fails fast on required-invalid cells.
  The table does not silently coerce invalid values.

## 10. Keyboard workflow is required

- Every table-shaped UI must support a keyboard-only workflow:
  selection, editing, copy, paste, clear, undo, and navigation.
- Mouse-only tables are a contract violation. Users must be able to
  fill a table from a paste, navigate by Tab / Enter, and clear with
  Delete without touching the mouse.
- Shortcuts that conflict with the OS or with the host window's
  shortcuts must be explicitly noted in the project.

## 11. What this document does not cover

- Specific widget classes (`QTableView`, `tk.Entry`, etc.) — see the
  adapter documents.
- Per-project column shape, units, or column order — see the
  project's design doc.
- Cross-table interactions (linked tables, drag-and-drop between
  tables) — those are project-specific extensions on top of this
  baseline.

## 12. Related documents

- `00_UI_UX_SYSTEM.md` — common UX principles.
- `01_TOOLKIT_SELECTION_POLICY.md` — toolkit choice policy.
- `02_DESIGN_TOKENS_AND_LAYOUT.md` — tokens and layout.
- `adapters/PYQT_TABLE_IMPLEMENTATION.md` — PyQt5 implementation
  rules.
- `adapters/TKINTER_TABLE_ADAPTER.md` — Tkinter adapter rules for
  existing apps.
- `_source/SPREADSHEET_TABLE_CONTRACT_legacy_pyqt.md` — historical
  PyQt-only source. Reference only.
