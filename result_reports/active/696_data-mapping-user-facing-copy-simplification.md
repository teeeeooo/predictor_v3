# Data Mapping User-facing Copy Simplification

## Goal

Remove internal implementation terms from the Data Mapping Manager main screen
while preserving the current read-only behavior.

## Modified Files

- `apps/train/controllers/data_mapping_controller.py`
- `apps/train/services/data_mapping_service.py`
- `apps/train/ui/data_mapping_panel.py`
- `apps/train/ui/data_mapping_view_models.py`
- `tests/test_apps_train_data_mapping_controller.py`
- `tests/test_apps_train_data_mapping_service.py`
- `tests/test_apps_train_data_mapping_ui_models.py`

## UI Copy Policy

- Main-screen buttons are short: `Refresh`, `Import`, `Export`, `Save`,
  `Reload`.
- Main table titles are short: `Groups`, `Fields`, `Data`, `Issues`.
- The Future Actions table is removed from the main screen.
- The read-only actions remain disabled.
- Main-screen status is concise: `Ready.`, `Issues found.`, or
  `Unable to load data.`
- Main-screen source display shows `File: <path>` and does not expose runtime or
  repository wording.
- Detailed load errors remain in the Issues table.

## Validation

- `python3 -m py_compile apps/train/services/data_mapping_service.py apps/train/controllers/data_mapping_controller.py apps/train/ui/data_mapping_view_models.py apps/train/ui/data_mapping_panel.py`: OK
- `python3 -m pytest tests/test_apps_train_data_mapping_service.py tests/test_apps_train_data_mapping_controller.py tests/test_apps_train_data_mapping_ui_models.py -q`: OK, 15 passed
- Programmatic Qt smoke: OK; verified short button labels, `File: <path>`,
  hidden Future Actions table, and `load_failed` issue row.

## Excluded Scope

- No editable CRUD.
- No CSV import/export implementation.
- No save/reload implementation.
- No raw JSON parsing in UI.
- No initial entity row `selectRow()` restoration.
- No broad layout rewrite.

## Structure

```yaml
change_gate:
  new_source: none
  hotspot_delta: small
  code_map_check: not_required
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
  report_exemption: none
  read_ledger: included
```

Read Ledger:
- Target controller, service, panel, view-model, and focused tests.
- Prior workflow guidance already active in session; no broad document reread.

## Next Action

Arc 14B-3 editable CRUD or CSV v2 loader/exporter boundary decision.

## Commit / Push

Final commit/push result will be reported in terminal output.
