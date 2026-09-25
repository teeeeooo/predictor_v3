# 03. Spreadsheet-like Table UX Contract

## Role and scope

- This document is the **toolkit-agnostic table baseline adopted by
  predictor_v3**, with the surface bindings below. Other projects must
  explicitly adopt it; this repository does not govern their tables.
- It describes what the user sees and does, not how the toolkit
  implements it.
- Framework-specific rules live in:
  - `adapters/PYQT_TABLE_IMPLEMENTATION.md`
  - `adapters/TKINTER_TABLE_ADAPTER.md`
  - PySide6 Train/Predict use their current local surface owners and bindings;
    the legacy PyQt adapter is not their automatic implementation contract.
    A dedicated document may be added when needed; WPF is not the current toolkit.
- The historical reference at
  `_source/SPREADSHEET_TABLE_CONTRACT_legacy_pyqt.md` was a PyQt-only
  contract from a prior project. It is **source / history only**;
  this document is the active contract.

A "table-shaped" surface means a 2D grid the user can read across
columns and down rows. Single-column lists and form layouts are
**not** covered here.

Table-shaped is a trigger, not a pass condition. A compliant table surface
must also implement the interaction baseline in this document: selection,
copy/paste, clear, undo, navigation, edit/replace behavior, and read-only
cell roles where applicable. A grid of labels and entries that only looks
like a table remains non-compliant until those behaviors are present or the
gap is explicitly reported.

This document owns behavior after a table-shaped surface has been selected.
For the `predictor_v3` rule that shapes repeated input/result data into a
matrix table or summary result surface in the first place, see
`05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md`.

## Temporary surface bindings

For this policy-only consolidation, existing product behavior is temporarily
fixed as described in [the root baseline](README.md#temporary-behavior-baseline).
The following observed bindings take precedence over conflicting generic clauses
in this document during consolidation. They do not certify overall UX parity or
permanently settle future interaction design.

| Surface | Temporarily retained behavior | Owner and evidence |
| --- | --- | --- |
| Train Data Mapping | One contiguous rectangular selection; no Ctrl-click disjoint ranges. Paste exceeding available rows or columns is rejected as a whole, without changing draft, selection, or undo history. | [Table view](../../apps/train/ui/data_mapping/table_view.py), [overflow/selection regression](../../tests/apps/train/ui/data_mapping/test_audit_selection_overflow.py). |
| Predict Input | Paste creates required overflow rows through the application bulk transaction; it does not silently discard those values. | [Approved input authoring](../designs/2026-07-14-future-predict-ui-ux-overhaul-boundary.md#3-approved-input-authoring), [UI adapter](../../apps/predict/ui/bulk_paste_adapter.py), [application owner](../../apps/predict/application/bulk_paste.py). |
| Calculator `MetricInputTable` + `TkTableController` (including Hong Kong inputs) | Paste writes raw text into editable cells; invalid numeric text is not rejected atomically at the paste layer. Read-only cells are excluded. Validation/calculation remains with the surface/domain owner. | [Controller](../../apps/calculator/ui/table/controller.py), [surface](../../apps/calculator/ui/metric_input_table.py), [paste regression](../../tests/test_ui_tk_metric_input_table_controller_parity.py), [Hong Kong caller regression](../../tests/test_ui_tk_hong_kong_cspf_controller_switch.py). |

Source review also shows that the common Tk controller retains a single
rectangle (no Ctrl-toggle set), keeps selection on selection-mode Esc, and
provides explicit F2 edit entry without a separate same-cell/double-click
edit-entry binding. These differ from the generic clauses below and remain
unresolved interaction gaps under the temporary freeze, not parity passes.
This is a bounded source observation, not a full per-surface runtime audit.

Other existing table behavior is unchanged by policy cleanup. Record unresolved
contract differences rather than changing implementations to make this document
appear consistent. Later explicitly scoped behavior work can revise the relevant
binding with its owner and focused validation.

## Completion gate

This document, including its surface bindings, owns table UX completion for
the adopted predictor_v3 surfaces. Toolkit adapters describe implementation;
they do not silently introduce alternate product rules.

Concrete implementations and external examples may be used as evidence for
the desired interaction feel. They do not replace this toolkit-neutral
contract, and they do not become owner docs. An adopted interaction target
applies across toolkits subject to the documented surface bindings.

Before a new table-shaped UI or table adapter is treated as complete:

- Reuse the existing reference table implementation for the toolkit when the
  shape fits.
- If the reference implementation cannot be reused, preserve the reason and
  controller-level parity test plan in task validation/evidence.
- Preserve the table parity checklist below as pass/fail validation evidence.
- If a toolkit-specific adapter does not yet exist, use this document
  directly as the acceptance contract and preserve the adapter gap in task
  evidence.
- These evidence requirements do not create a separate Result Record or memory-write requirement. Preserve durable rationale only when the active memory/decision policy says it is worth keeping.
- Windows or platform smoke is a final platform check. If a core interaction
  bug is first discovered there, record it as a validation gap and add an
  automated helper/controller-level guard in the next correction slice.

Toolkit-neutral parity checklist:

- multi-cell rectangular selection
- copy as TSV
- paste from TSV
- single-column multi-row paste
- Delete/Backspace clear
- grouped undo for rectangular paste/clear/edit operations
- Tab/Enter navigation and shifted variants
- arrow-key navigation in selection mode
- click/type replace-on-type
- read-only result cell copy
- read-only result mutation prevention
- row identity uses row headers by default, not calculation input columns
- layout sizing acceptance: a table/dialog must not unnecessarily enlarge
  the parent/main window, and the default viewport must show the core
  rows/columns without excessive blank space

## Surface architecture requirements

- A table is a reusable surface with row/column metadata and cell-role
  metadata; interaction code attaches to that surface rather than rebuilding
  cells ad hoc.
- Table and associated result surfaces use their parent layout responsively:
  related tables expand together and preserve alignment when the available
  content area changes.
- Toolkit adapters may choose character/font-based initial sizing and local
  density rules, but must not solve alignment by fixing a table to one pixel
  width that prevents resize behavior.
- Selection, clipboard, clear, undo, and navigation may be implemented by a
  separate interaction controller, provided the final table still satisfies
  the baseline behavior below.
- Reusable table components are not product screens. A new adapter or
  toolkit port must prove the table inside the existing section order and
  user workflow, not only in a standalone grid demo.
- Demo rows, mock cascading options, and component smoke controls belong in
  test/demo surfaces only. They must not be visible in the default
  calculator, Predictor, or Trainer workflow.

## 1. Baseline: behaves like a small Excel sheet

Users come to every table with spreadsheet muscle memory (Excel,
Google Sheets, Numbers). The table must respond the way a
spreadsheet would for the actions below. Undocumented divergence is a contract gap;
the explicit temporary surface bindings above retain their current behavior.

## 2. Selection

- **Single click** on a cell selects exactly that cell and makes it
  the active cell in selection mode.
- **Click and drag** selects a contiguous rectangular range.
- **Shift + click** extends the current selection to a contiguous
  range anchored at the previously active cell.
- **Ctrl + click** toggles individual cells in or out of the
  selection (non-contiguous selection).
- The active cell is visually distinct from the rest of the
  selection.
- A click on a header selects the row or column where supported.

## 3. Selection and edit state machine

Every editable table implements these two interaction modes:

- **Selection mode**: one cell or range is active, with no text caret inside
  the cell. Commands act on cells or the selection. A printable key starts a
  whole-cell replacement: the old cell value is replaced and that key is the
  first character of the new value.
- **Edit mode**: one cell has an active text-editing position and a visible
  caret. The value present when edit mode begins is retained until the user
  edits it. Printable keys insert or append at the caret rather than
  replacing the whole cell.

For an editable cell, the required transitions are:

| Current state | User event | Required behavior | Next state |
| --- | --- | --- | --- |
| No selection | Cell click | Select the clicked cell as active; do not show a caret. | Selection mode |
| Selection mode | Printable key | Replace the whole active-cell value; the key becomes the first new character. | Edit mode |
| Selection mode | Same active-cell click | Retain the current value and place a caret for partial editing. | Edit mode |
| Selection mode | Double click on active cell | Retain the current value and place a caret for partial editing. | Edit mode |
| Selection mode | `F2` | Retain the current value and place a caret for partial editing. | Edit mode |
| Selection mode | Arrow key | Move the active cell in that direction without editing a value. | Selection mode |
| Selection mode | `Tab` / `Enter` (and shifted variants) | Move the active cell according to §6 without editing a value. | Selection mode |
| Selection mode | `Delete` / `Backspace` | Clear editable cells in the selection as one undoable cell operation. | Selection mode |
| Selection mode | `Esc` | Clear the active selection and its selection visual. | No selection |
| Edit mode | Printable key | Insert or append at the caret, preserving text not replaced by the edit. | Edit mode |
| Edit mode | Arrow key | Move the caret within the editable value; do not move the active cell. | Edit mode |
| Edit mode | `Delete` / `Backspace` | Delete text relative to the caret; do not clear the selection as a cell operation. | Edit mode |
| Edit mode | `Enter` / `Tab` (and shifted variants) | Commit the edited value, then move the active cell according to §6. | Selection mode |
| Edit mode | `Esc` | Cancel uncommitted editing, restore the value from before edit mode, and keep the cell selected. | Selection mode |
| Edit mode | Focus leaves the table | Commit the edited value before table focus is released. | No longer editing; external focus applies |

Same-cell second click, double click, and `F2` are required edit-entry
paths, not optional enhancements. They enter edit mode without clearing the
existing value. A project may add explicit edit affordances, but they do not
replace these baseline paths.

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
  repeated to fill the selection (Excel behavior). A one-row source
  whose column count matches the selected range width is repeated down
  each selected row. Other multi-cell sources are **not** auto-repeated.
- Selected-range fill paste applies across toolkits: if the clipboard is
  `1 x N` and the selection is `M x N`, the clipboard row fills each selected
  row. Read-only/result cells inside the selection are skipped as mutation
  targets.
- Paste of a non-TSV payload is rejected without modifying any cell.
- Pasted values go through the same per-column validator as inline
  edits. Invalid pasted cells are marked but do not abort the paste;
  other valid cells still land.

## 5. Clear (Delete / Backspace)

- In **selection mode**, **Delete** and **Backspace** clear the contents of
  every editable cell in the current selection.
- In **edit mode**, **Delete** and **Backspace** edit text relative to the
  caret and do not invoke selection clear.
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
- In **selection mode**, **Arrow keys** move one cell at a time in the
  corresponding direction; they do not wrap by default.
- In **edit mode**, **Arrow keys** move the caret inside the value rather than
  moving to another cell.
- In **edit mode**, **Esc** cancels the in-progress edit and returns to a
  selected cell. In **selection mode**, **Esc** removes the selection.
- When focus leaves the table during edit mode, the pending value is committed
  before external focus takes over.

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

- Specific widget classes or event-binding mechanisms — see the adapter
  documents.
- Per-project column shape, units, or column order — see the
  project's design doc.
- Cross-table interactions (linked tables, drag-and-drop between
  tables) — those are project-specific extensions on top of this
  baseline.
- Permission to change the surrounding product workflow. Toolkit adapters
  implement this contract inside an approved screen flow; they do not decide
  whether the screen is immediate-calc, button-run, single-case, or batch.

## 12. Related documents

- `00_UI_UX_SYSTEM.md` — common UX principles.
- `01_TOOLKIT_SELECTION_POLICY.md` — toolkit choice policy.
- `02_DESIGN_TOKENS_AND_LAYOUT.md` — tokens and layout.
- `05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md` — `predictor_v3`
  matrix/result surface-shaping rules; separate from this behavior contract.
- `adapters/PYQT_TABLE_IMPLEMENTATION.md` — legacy Qt binding implementation
  rules.
- `adapters/TKINTER_TABLE_ADAPTER.md` — Tkinter adapter rules for
  existing apps.
- `_source/SPREADSHEET_TABLE_CONTRACT_legacy_pyqt.md` — historical
  PyQt-only source. Reference only.
