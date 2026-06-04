# Tkinter Table Adapter

## Role and scope

- This document is the **Tkinter-specific adapter** for table-shaped
  UI in existing Tkinter applications.
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

For existing `calculator_tk` screens, preserve the current section order and
primary user flow before changing widgets. Hong Kong calculator sections are
immediate-calculation screens by default; adding a Calculate button or batch
Run action is a product-flow change and must be scoped as such. Predictor and
Trainer batch/model workflows may use explicit Run/Predict/Train actions.

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

### Responsive Entry-grid construction

- Wrap editable entries in cell frames and expose row, column, role, and
  editable-widget metadata so a later interaction controller can register
  against the existing table surface.
- Use character/font-based requested cell sizes for initial readability, then
  use parent `fill`/`expand` or grid `weight` plus `sticky="ew"` so related
  matrix/result surfaces stretch together.
- Do not use a fixed pixel table width as the alignment mechanism. Related
  rated, trial, and result surfaces share a responsive parent width policy.
- Typography and row padding are density choices: readable table fonts should
  be paired with compact cell padding rather than inflated fixed row heights.

## 3. UX baseline still applies

Tkinter is the implementation, not an excuse to drop UX baseline.

- The Excel-like baseline in
  `../03_SPREADSHEET_TABLE_UX_CONTRACT.md` (including its selection/edit
  state machine, Ctrl+C / Ctrl+V TSV, clear, undo, navigation, distinct cell
  states, and invalid display) applies here too.
- These behaviors are not free in Tkinter. You must implement them
  yourself; see §4.

## 4. Implementing the baseline on an Entry grid

Because Tkinter does not provide spreadsheet primitives, the
Entry-grid surface must wire each behavior explicitly. A table builder may
create the cell registry and rendering surface first; a separate interaction
controller may later `register()` those cells and own the behaviors below:

- **Selection**: maintain a selection model in app code (anchor
  cell, active cell, selected rectangle). Apply a distinct
  background to selected cells with `widget.configure(bg=...)`.
- **Selection mode**: keep the caret hidden. On the first printable key into
  the active cell, clear the existing value before inserting that character.
- **Edit mode**: keep the caret visible and retain the existing value when
  entering through a same-cell second click, double click, or `F2`; text
  input then performs ordinary partial editing.
- **Ctrl + C**: serialize the selected rectangle to TSV and put it
  on the clipboard via `clipboard_clear` + `clipboard_append`.
- **Ctrl + V**: read the clipboard, parse TSV, and apply it to the
  selection anchored at the top-left, following the same size rules
  as the common contract (single-cell repeat, multi-cell no
  auto-repeat, out-of-bounds drop).
- **Delete / Backspace**: in selection mode, clear every editable cell in the
  selection in one undo group and skip disabled / read-only cells; in edit
  mode, edit the text at the caret.
- **Ctrl + Z**: maintain an undo stack of cell mutations. Each user
  action (edit, paste, clear) is one undo group.
- **Tab / Shift+Tab / Enter / Shift+Enter**: commit an active edit, when
  present, and move to the contract-defined destination cell.
- **Arrow**: in selection mode, move the active cell; in edit mode, allow
  caret movement within the value.
- **Esc**: in edit mode, cancel the edit and restore the prior value while
  keeping the cell selected; in selection mode, clear selection.

Treeview surfaces inherit the read-only side of this baseline
(selection, Ctrl+C as TSV, distinct cell states) but skip the
editing pieces.

### Predictor_v3 Tkinter calculator binding

The ISO Hong Kong Tkinter calculator attaches a separate
`ExcelLikeTableController` to each rated and trial `MetricInputTable`.
The table surface exposes metadata plus grouped mutation hooks; the
controller owns rectangular selection, TSV clipboard actions, grouped
clear/undo, navigation, and type-to-replace without creating cells.

For this numeric auto-calculation surface, a paste is validated as one
action before applying any values. If any pasted numeric cell is invalid,
no cell is changed and no recalculation is scheduled. Inline invalid edits
remain visible through the existing result-status path. This atomic paste
policy is a **paste-specific deviation** from the common baseline, retained
for the current `predictor_v3` binding to avoid partially updated automatic
results; it does not change the selection/edit state machine.

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

- Sub-dialogs follow the project's existing helper (for example a
  `center_dialog` and `withdraw → deiconify` pattern). Use:
  - `transient(parent)` so the dialog tracks the parent window.
  - `grab_set()` for modal dialogs so input is captured.
  - Center the dialog over the parent before deiconifying.
- Dialogs must not open off-screen. When the parent's geometry is
  not yet known, compute placement after the parent has been mapped.
- Action rows live at the bottom; primary action on the right (or
  the platform's expected side), with the cancel / dismiss control
  to its left.

## 8. Reusable Tkinter reference lessons

These are the Tkinter-side lessons worth carrying to every Tkinter
project when reviewing existing implementation evidence:

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
- Every table column declares sensible readable sizing and stretch behavior;
  do not freeze a responsive surface to a single pixel width.
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
- Exposing mock rows, component smoke controls, or demo-only dropdowns in the
  default user-facing calculator screen.
- Using the adapter as permission to replace an immediate-calc calculator
  workflow with a button-run demo layout.

## 10. Related documents

- `../00_UI_UX_SYSTEM.md` — common UX principles.
- `../01_TOOLKIT_SELECTION_POLICY.md` — toolkit choice policy.
- `../02_DESIGN_TOKENS_AND_LAYOUT.md` — tokens and layout.
- `../03_SPREADSHEET_TABLE_UX_CONTRACT.md` — common table UX.
- `../05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md` — project-wide
  matrix/result surface-shaping rule applied before widget selection.
- `PYQT_TABLE_IMPLEMENTATION.md` — PyQt5 equivalent for new apps.
