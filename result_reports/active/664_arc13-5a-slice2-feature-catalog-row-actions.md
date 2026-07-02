# Arc 13.5A Slice 2 - Feature Catalog Row Actions

## Goal

Implement draft-state Add, Duplicate, and Delete workflows for Feature Catalog rows while preserving validation-gated save.

## Scope

- Added `FeatureCatalogDraftRequest` application DTO.
- Added service/controller row builder for draft rows with generated `order` and collision-safe `ui_key`.
- Added Add Feature dialog for user-facing row fields.
- Added Add, Duplicate, and Delete buttons to the Feature Catalog panel.
- Added table-model append/remove helpers that update baseline-diff dirty state.
- Added focused tests for draft row generation, `ui_key` collision handling, add/remove dirty behavior, row dialog requests, and panel delete behavior.

## Non-goals Held

- No derived formula editor.
- No new one-hot group workflow beyond accepting existing/free text group values.
- No model artifact compatibility implementation.
- No schema live refresh implementation.

## Verification

- `python3 -m compileall apps/train core/ml tests/test_apps_train_feature_catalog.py tests/test_apps_train_shell.py` - OK
- `python3 -m pytest tests/test_apps_train_feature_catalog.py tests/test_apps_train_shell.py` - OK, 29 passed
- `git diff --check` - OK
- `python3 -B tools/check_code_structure.py --verbose` - NG, pre-existing unrelated raw hex literal:
  - `apps/calculator/ui/calculator_app.py:105`
  - Existing unrelated soft warnings remained outside changed files.
- `python3 -B tools/code_checker/build_reference_map.py --check` - STALE from existing repository state; checked and not regenerated in this feature slice.

## Structure

```yaml
change_gate:
  new_source: justified
  hotspot_delta: none
  code_map_check: checked
  ui_literal_exemption: none
  reuse_commonization: local-with-reason
  report_exemption: none
  read_ledger: included
```

New source justification: `apps/train/ui/feature_catalog/row_dialog.py` owns row-input dialog UI and keeps panel responsibilities below the soft limit.

Reuse/commonization decision: row add/duplicate/delete behavior is Feature Catalog-specific and routes through the existing Feature Catalog service/controller/model owners. No shared row-action helper is introduced in Slice 2.

## Changed Files

- `apps/train/application/feature_catalog/__init__.py`
- `apps/train/application/feature_catalog/models.py`
- `apps/train/application/feature_catalog/service.py`
- `apps/train/controllers/feature_catalog_controller.py`
- `apps/train/ui/feature_catalog/__init__.py`
- `apps/train/ui/feature_catalog/panel.py`
- `apps/train/ui/feature_catalog/row_dialog.py`
- `apps/train/ui/feature_catalog/table_model.py`
- `tests/test_apps_train_feature_catalog.py`

## Risks

- Add dialog currently allows free text for source/mapping/one-hot fields because dedicated allowlist ownership remains an open design question.
- Duplicate defaults to `<old> Copy` for `ml_name` and label; validation still gates save if the user keeps an invalid or conflicting value.

## Commit / Push

Committed as one Slice 2 commit. Push remains deferred until all requested remaining slices are complete.

## Next

Arc 13.5A Slice 3 - Schema refresh and apply behavior.
