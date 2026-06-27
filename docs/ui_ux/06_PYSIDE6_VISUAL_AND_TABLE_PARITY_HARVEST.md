# PySide6 Visual and Table Parity Harvest

## Role

This document preserves useful UX and visual ideas from the retired legacy
Train/Predict PyQt path so Arc 9.5 can reimplement them in the new PySide6
surface without copying legacy code.

This is a harvest/reference document, not a toolkit adapter and not a
pixel-perfect design specification. Active behavior contracts remain:

- `docs/ui_ux/00_UI_UX_SYSTEM.md`
- `docs/ui_ux/02_DESIGN_TOKENS_AND_LAYOUT.md`
- `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md`
- `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md`
- `docs/architecture/pyside6_train_predict_architecture.md`

Visual reference assets for Arc 9.5:

- `docs/designs/assets/predict_ref_img.png`
- `docs/designs/assets/train_ref_img.png`

These images guide layout density, surface hierarchy, and visual rhythm. They
are not pixel-perfect targets.

## Harvested UX Ideas

### Dropdown Cells

Source idea: legacy `ui/base_view.py`.

Target behavior for PySide6:

- dropdown-capable cells should visibly communicate that they are selectable;
- a cell may draw a dropdown affordance even when it is not actively editing;
- clicking a dropdown cell should enter edit mode and open the option list
  without requiring an extra click;
- dependent dropdown option updates should flow through controller/state, not
  direct widget mutation from business logic.

Do not copy:

- the PyQt5 `QStyledItemDelegate` implementation;
- direct table/widget coupling;
- any import from legacy `ui.*`.

### Spreadsheet Table Interaction

Source idea: legacy `ui/spreadsheet_table.py`.

Target behavior for PySide6:

- copy selected ranges as TSV;
- paste TSV anchored at the active/top-left cell;
- clear selected editable cells;
- support grouped undo for paste/clear/edit operations;
- keep read-only result cells copyable but mutation-protected;
- detect invalid numeric values and expose validation state near the cell.

The active completion checklist is still
`03_SPREADSHEET_TABLE_UX_CONTRACT.md`; the legacy module is evidence only.

### Visual Tokens

Source idea: legacy `ui/theme.py`.

Target behavior for PySide6:

- use semantic roles for surfaces, borders, text, table states, result states,
  spacing, radius, and fonts;
- keep token values toolkit-neutral in `ui_common.visual_tokens`;
- build a PySide6 style adapter later, rather than placing raw colors directly
  inside product widgets.

Do not copy:

- legacy `ui.theme` token names as a parallel owner;
- PyQt/PySide concrete styling into `ui_common`.

### Predict / Train Feature Inventory

Source ideas: legacy `ui/predict_window.py` and `ui/train_window.py`.

Useful feature inventory:

- model status visibility;
- explicit predict/run action;
- mapping update flow;
- Train / Model and Data Mapping admin affordances;
- row-level prediction errors that do not crash the app.

Do not copy:

- monolithic window/controller structure;
- direct model loading from widgets;
- direct file-dialog or mapping-update calls from widgets;
- PyQt thread wiring.

## Arc 9.5 Acceptance Hints

Arc 9.5 should make the new PySide6 Predict/Train foundation visually usable
from the design assets while preserving current architecture boundaries.

Acceptance hints:

- Predict remains a split input/result workspace.
- Trainer remains a tabbed admin shell with Predict / Train Model /
  Data Mapping surfaces.
- User-facing row identity remains row headers, not visible `case_id` columns.
- `case_id` remains internal state identity for result lookup.
- Visual styling should use semantic roles from `ui_common.visual_tokens`.
- Table parity can be improved in slices, but every deferred checklist item
  must remain explicit in reports.

## Remaining Table UX Gap From Arc 9

- TSV copy
- TSV paste
- Delete/Backspace clear
- grouped undo
- Tab/Enter navigation
- click/type replace-on-type
- dropdown delegate rendering
- validation rendering

These gaps are not Arc 10 worker/progress work. Keep them in a dedicated table
UX parity slice unless a later prompt explicitly changes the order.
