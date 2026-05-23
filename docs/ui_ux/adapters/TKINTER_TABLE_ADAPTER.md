# Tkinter Table Adapter

## Role and scope

- This document is the **Tkinter-specific adapter** for table-shaped
  UI in existing Tkinter applications (e.g. SPOT).
- It assumes the toolkit-agnostic baseline in
  `../03_SPREADSHEET_TABLE_UX_CONTRACT.md` and the common UX
  principles in `../00_UI_UX_SYSTEM.md`.
- It does **not** describe PyQt5 behavior. For PyQt5, see
  `PYQT_TABLE_IMPLEMENTATION.md`.

Tkinter is **not** the default toolkit for new table-heavy desktop
apps. See `../01_TOOLKIT_SELECTION_POLICY.md`. This adapter exists
because existing Tkinter apps must keep meeting the common UX
baseline without being forced into a toolkit migration.

Before choosing an Entry grid or Treeview for `predictor_v3`, determine the
input/result surface shape under
`../05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md`. This adapter implements a
selected shape; it does not decide whether repeated data should be a matrix.

## 1. Where this adapter applies

- Existing Tkinter projects that already ship and need maintenance.
- New table-shaped surfaces inside those Tkinter projects that the
  project chooses to keep in Tkinter under
  `../01_TOOLKIT_SELECTION_POLICY.md` §3.
- Migration of a Tkinter app to PyQt5 is **out of scope** for this
  adapter. That goes through the design gate described in
  `../01_TOOLKIT_SELECTION_POLICY.md` §4.

## 2. Allowed widget patterns

Tkinter has no native model / view / delegate equivalent. The
adapter accepts two patterns, picked per surface:

- **Entry grid**: a 2D grid of `tk.Entry` (or `ttk.Entry`,
  `ttk.Combobox`) widgets laid out by `.grid(...)`. Use this when
  every cell must be editable, with type-to-replace and per-column
  validators.
- **Treeview**: `ttk.Treeview` configured as a multi-column table.
  Use this when the table is primarily display / read-only with at
  most light editing (e.g. inline rename, selection-based actions).

Pick one per surface. Do not mix Entry grid and Treeview into one
hybrid widget for the same table.

## 3. UX baseline still applies

Tkinter is the implementation, not an excuse to drop UX baseline.

- The Excel-like baseline in
  `../03_SPREADSHEET_TABLE_UX_CONTRACT.md` (selection, type-to-
  replace, Ctrl+C / Ctrl+V TSV, Delete clear, Ctrl+Z undo, Tab /
  Enter navigation, distinct cell states, invalid display) applies
  here too.
- These behaviors are not free in Tkinter. You must implement them
  yourself; see §4.

## 4. Implementing the baseline on an Entry grid

Because Tkinter does not provide spreadsheet primitives, the
Entry-grid surface must wire each behavior explicitly:

- **Selection**: maintain a selection model in app code (anchor
  cell, active cell, selected rectangle). Apply a distinct
  background to selected cells with `widget.configure(bg=...)`.
- **Type-to-replace**: on the first keystroke into the active cell,
  clear the existing value before inserting the character.
- **Ctrl + C**: serialize the selected rectangle to TSV and put it
  on the clipboard via `clipboard_clear` + `clipboard_append`.
- **Ctrl + V**: read the clipboard, parse TSV, and apply it to the
  selection anchored at the top-left, following the same size rules
  as the common contract (single-cell repeat, multi-cell no
  auto-repeat, out-of-bounds drop).
- **Delete / Backspace**: clear every editable cell in the
  selection in one undo group; skip disabled / read-only cells.
- **Ctrl + Z**: maintain an undo stack of cell mutations. Each user
  action (edit, paste, clear) is one undo group.
- **Tab / Shift+Tab / Enter / Shift+Enter / Arrow**: bind
  navigation explicitly so the focus moves between cells and not
  out of the table. Override the default Tk focus traversal where
  needed.
- **Esc**: cancel an in-progress edit and restore the prior value.

Treeview surfaces inherit the read-only side of this baseline
(selection, Ctrl+C as TSV, distinct cell states) but skip the
editing pieces.

## 5. Cell states

- **Editable**: default Entry foreground / background.
- **Read-only / auto**: configure the Entry with `state="readonly"`
  and use the read-only background token; pair with a foreground
  that signals "not user-edited". Background alone is not enough.
- **Disabled / inactive**: configure with `state="disabled"`; the
  cell is skipped by edit, paste, delete, and undo paths.
- **Invalid value**: keep the cell editable; mark it with a
  validation background (token: `color.bg.cell.invalid`) and/or a
  border drawn around the cell frame. Use a separate visual from
  read-only.
- **Empty** vs **invalid**: an empty cell is not an error state.
  Do not paint empty cells with the invalid background.

## 6. Long operations: progress and threading

- Any operation longer than ~1 second goes through a progress dialog
  per `../00_UI_UX_SYSTEM.md` §6. The dialog must paint before the
  blocking work begins.
- Schedule blocking work on the Tk event loop using `after()` (or
  `after_idle()`) so the dialog gets a chance to paint first.
- Default to **event-loop scheduling**, not threads. Only introduce
  a worker thread when the operation genuinely cannot be sliced
  inside the event loop, and treat that as an explicit design
  decision.
- When a Tkinter UI talks to Excel via COM (e.g. `pywin32` /
  `xlwings`), be **especially careful** with threads: COM calls
  generally need to happen on the thread that initialized the COM
  apartment for the Excel object. Prefer keeping Excel I/O on the
  Tk main thread and using `after()` scheduling to keep the UI
  responsive.
- On failure, close the progress dialog and show an error message
  in the user's language. Never leave a "please wait..." dialog
  stranded on screen after an exception.

## 7. Dialog patterns

- Sub-dialogs follow the project's existing helper (e.g. SPOT's
  `center_dialog` and `withdraw → deiconify` pattern). Use:
  - `transient(parent)` so the dialog tracks the parent window.
  - `grab_set()` for modal dialogs so input is captured.
  - Center the dialog over the parent before deiconifying.
- Dialogs must not open off-screen. When the parent's geometry is
  not yet known, compute placement after the parent has been mapped.
- Action rows live at the bottom; primary action on the right (or
  the platform's expected side), with the cancel / dismiss control
  to its left.

## 8. Generalized SPOT lessons

These are the Tkinter-side lessons worth carrying to every Tkinter
project, not SPOT-specific quirks:

- A single fixed input must not stretch full width to fill a row.
  Constrain its width and let the remaining space stay empty.
- Multiple fixed inputs use a compact grid or wrap layout, not one
  column of full-width fields.
- The initial-value table should target 2–7 points visible on one
  screen without scrolling. Past that range, prefer narrower entry
  widths or in-table vertical scrolling over a window that grows
  beyond the screen.
- Avoid horizontal scrolling on the root window. Long content lives
  inside a scrollable table or panel.
- Long labels wrap to two lines or use an ellipsis; do not stretch
  the column.
- Every table column declares a sensible `min` / `max` width.
- Numeric values use the project's compact numeric formatter.
- Progress dialogs paint before the calculation starts; failure
  paths close them; completion paths give explicit feedback.

## 9. Forbidden patterns

- Treating Tkinter as the **default** toolkit for new table-heavy
  desktop apps. The default is PyQt5 under
  `../01_TOOLKIT_SELECTION_POLICY.md`.
- Mixing Tkinter and PyQt5 widgets in the same process.
- Dropping the Excel-like UX baseline ("Tkinter can't do it") as a
  justification. The baseline applies; the adapter shows how to
  meet it.
- Long-running work on the Tk main thread with no progress dialog,
  or a progress dialog that appears only after the work begins.
- Background COM calls to Excel from a thread other than the one
  that initialized the COM apartment for the Excel object.
- Communicating "read-only" with background color alone when the
  background is close to the editable background.

## 10. Related documents

- `../00_UI_UX_SYSTEM.md` — common UX principles.
- `../01_TOOLKIT_SELECTION_POLICY.md` — toolkit choice policy.
- `../02_DESIGN_TOKENS_AND_LAYOUT.md` — tokens and layout.
- `../03_SPREADSHEET_TABLE_UX_CONTRACT.md` — common table UX.
- `../05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md` — project-wide
  matrix/result surface-shaping rule applied before widget selection.
- `PYQT_TABLE_IMPLEMENTATION.md` — PyQt5 equivalent for new apps.
