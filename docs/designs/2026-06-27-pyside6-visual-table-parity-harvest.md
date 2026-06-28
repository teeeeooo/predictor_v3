# PySide6 Visual and Table Parity Harvest

## Role

This document is a project-specific design/harvest reference for the
predictor_v3 PySide6 Train/Predict rewrite. It preserves useful UX, table,
visual, and admin-surface evidence from the retired legacy `ui/` path so Arc
9.5 can implement visual/table parity without copying legacy code.

This document is not a portable UI/UX owner contract, toolkit adapter, or
pixel-perfect design specification. Use it together with:

- `docs/designs/assets/predict_ref_img.png`
- `docs/designs/assets/train_ref_img.png`
- `docs/ui_ux/00_UI_UX_SYSTEM.md`
- `docs/ui_ux/02_DESIGN_TOKENS_AND_LAYOUT.md`
- `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md`
- `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md`
- `docs/architecture/pyside6_train_predict_architecture.md`

The visual assets guide layout density, surface hierarchy, and interaction
expectations. They are non-binding references, not pixel-perfect targets.

Legacy `ui/` code is evidence only. Do not restore it, import it, or copy the
PyQt implementation into active PySide6 code.

## Source Evidence

Legacy files inspected from pre-retirement ref
`f8adf7075563838dc8217833b46242ad618fc3ae`:

- `ui/base_model.py`
- `ui/base_view.py`
- `ui/spreadsheet_table.py`
- `ui/predict_window.py`
- `ui/train_window.py`
- `ui/theme.py`

## Arc 9.5 Acceptance Checklist

### A. Predict Table Visual / Interaction Parity

- Row height and column width should follow schema intent where available.
- Input, auto-filled, and result cells should be visually distinct.
- Read-only cells remain selectable and copyable, but mutation-protected.
- Dropdown-capable cells should render an affordance even when not editing.
- Dropdown cells should support one-click popup behavior.
- `ref_type` dropdown fallback options: `R410A`, `R32`, `R290`.
- `exp_type` dropdown fallback options: `EEV`, `Capi`.
- Dependent dropdown update boundaries should flow through state/controller,
  not direct business logic inside the table view/model.
- Invalid numeric state should render near the cell with a tooltip or status
  surface.
- User-facing row identity stays in the row header. Visible `case_id` columns
  should not return.

### B. Spreadsheet Interaction Parity

- Copy selected rectangle as TSV.
- Paste TSV anchored at the current cell or top-left of the current selection.
- Normalize CRLF, CR, and LF line endings on paste.
- Drop the trailing blank row from Excel/Sheets-style trailing newlines.
- Out-of-bounds paste cells are dropped without shifting the table shape.
- Delete/Backspace clears editable cells only.
- Edits, paste, and clear operations should be grouped into undo units.
- Snapshot-based undo depth from legacy evidence was 64; PySide6 may choose a
  documented equivalent.
- Idempotent edit/paste/clear should not create noisy undo entries or
  high-level value-change signals.
- Tab / Shift+Tab / Enter / Shift+Enter navigation should follow the portable
  table contract.
- Click/type replace-on-type should be considered part of spreadsheet parity
  if the PySide6 table adapter does not already provide it.
- Table model/view code must not own prediction, mapping repository, training,
  or calculator business logic.

### C. Mapping / Autofill Parity

- Legacy `DROPDOWN_TARGET` section relation is evidence for mapping-driven
  dropdown ownership; active implementation should route through current core
  owners.
- Legacy `source` / `mapping_key` relations are evidence for auto-filled
  columns.
- IDU selection should support simple mapping auto-fill.
- ODU selection should update dependent Fin / Pi / Row options.
- ODU upstream changes should clear stale Fin / Pi / Row / Cond Area /
  Cond Volume values.
- `cond_specs` lookup key composition should preserve the legacy relation:
  `ODU Fin Pi Row`.
- Missing mapping data or mapping load failure should surface as controlled
  status, not silent table failure.
- The table model should not call the mapping repository directly.

### D. Row-To-ML / Result Parity

- `ml_feature` metadata remains the row-to-model extraction guide.
- `ref_type` one-hot features should preserve `R410A`, `R32`, and `R290`.
- `exp_type` one-hot features should preserve `EEV` and `Capi`.
- Blank/invalid input rows should be skipped or reported according to the
  active validation policy before prediction.
- Missing model state should be shown as a controlled error/status.
- Row-level prediction errors should be reported without crashing the whole
  batch.
- Results should be mapped through the active result adapter and internal
  `case_id` lookup.
- Legacy TODO placeholders such as missing CSPF/HSPF2 result text must not be
  copied into the PySide6 result table.

### E. Predict Surface Visual Hierarchy

- Top status area should make model, mapping, and preprocessing state visible.
- Command bar should group prediction, clear/reset, row operations, and future
  import/export actions without crowding the tables.
- Predict workspace remains an input/result split surface.
- Result status, row errors, and warnings need a dedicated surface.
- Bottom or side status summary should support large-batch scanning.
- Variable-size batch prediction remains the target; do not assume fixed row
  count as the user-facing model.

### F. Train Admin Visual / Function Inventory

- Trainer app keeps the tabbed shell.
- Predict tab reuses the Predict workspace.
- Train Model tab inventory: dataset path, train action, model status, and
  log/status area.
- Data Mapping tab inventory: mapping source, update action, mapping status,
  and log/status area.
- Duplicate train-run prevention and controlled success/failure status are
  useful behavior evidence.
- Background worker/progress/cancel concepts belong to Arc 10 or Arc 11
  depending on explicit scope.
- Do not copy PyQt thread code.

### G. Visual Token Adoption

- `ui_common.visual_tokens` is the active toolkit-neutral token owner.
- Arc 9.5 may add or use a PySide6 style adapter, but should not create a
  second token registry.
- Use semantic tokens for app surface, card/panel surface, header surface,
  readonly cell, invalid cell, primary/secondary/disabled text, accent,
  success/warning/danger status, borders, fonts, and spacing.
- Avoid raw scattered colors when a semantic token exists.
- Legacy `ui/theme.py` is evidence only.

## Deferred Items By Target Arc

### Arc 9.5

- Visual parity from `predict_ref_img.png` and `train_ref_img.png`.
- Predict table visual/interaction parity.
- Spreadsheet table UX parity where explicitly scoped.
- PySide6 visual token adapter or equivalent semantic style binding.

### Arc 10

- Prediction execution worker/progress/cancel foundation, if explicitly scoped.
- Controlled async status/error surfaces for long-running prediction work.

### Arc 11

- Trainer admin execution foundation.
- Train Model and Data Mapping execution surfaces.
- Background worker behavior for training/mapping update, if explicitly scoped.

### Later

- Export/import polish.
- Additional spreadsheet conveniences not selected for Arc 9.5.

## Anti-Patterns To Avoid

- Restoring or importing the retired `ui/` package.
- Reintroducing PyQt production dependencies.
- Copying legacy monolithic window/controller structure.
- Placing mapping repository calls, ML inference, or training execution inside
  table models/views.
- Treating this harvest as a replacement for `docs/ui_ux/` portable contracts.
