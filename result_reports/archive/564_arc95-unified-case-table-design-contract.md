# 564 - Arc 9.5 Unified Case Table Design Contract

## Goal

Update the PySide6 Train/Predict architecture and visual/table acceptance
references so Arc 9.5 correction targets the B-option unified case table rather
than the previous split input/result table structure.

## Scope

- Replace the current architecture target for Predict main workspace from split
  input/result panes to one unified case table.
- Define column groups, model/view/controller boundaries, and app-side virtual
  status/message columns.
- Keep split table files as historical/foundation paths only, not final UX.
- Update Work Plan next action to Slice 3.

## Decision

Predict uses one unified case table as the Arc 9.5 correction target.

- One visible row equals one prediction case.
- Input, auto-fill/calculated, prediction result, and status/warning columns
  are grouped in the same table.
- Result and status columns are read-only but selectable and copyable.
- Edit, paste, clear, and undo write only to editable input cells.
- Internal `case_id` remains hidden.
- Split table sync and hidden joined-copy behavior are not accepted as final
  visual/table parity.

## Boundary Notes

- Core `COLUMNS` remains the schema owner for existing input/auto/result
  fields.
- App-side unified display schema may add virtual status/message columns.
- Table model must not call mapping repository, prediction service, training
  execution, or calculator APIs.
- Mapping/autofill remains through controller/state boundaries.
- Prediction execution remains through prediction controller/service
  boundaries.

## Changed Files

- `docs/architecture/pyside6_train_predict_architecture.md`
- `docs/designs/2026-06-27-pyside6-visual-table-parity-harvest.md`
- `docs/WORK_PLAN.md`
- `result_reports/active/564_arc95-unified-case-table-design-contract.md`

## Verification

- Split-target wording search: passed; no current-target split phrases remain in
  the architecture/harvest docs.
- `git diff --check`: passed.
- `git status --short`: checked; Slice 2 docs and this report were dirty before
  commit.

Skipped:

- pytest: docs-only architecture contract update.
- GUI smoke: no code change.
- `tools/check_code_structure.py`: no source structure change.

## Known Risks

- Source still uses split table implementation until Slices 3-5.
- The PySide6 toolkit adapter gap remains documented through the UI table
  contract until a dedicated adapter exists.

## Commit / Push

- Commit: pending.
- Push: not run; Slice 11 only.

## Next

Slice 3 - Unified Case Column Adapter.
