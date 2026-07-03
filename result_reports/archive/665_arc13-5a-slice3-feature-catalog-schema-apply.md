# Arc 13.5A Slice 3 - Feature Catalog Schema Apply Behavior

## Goal

Make post-save schema application behavior explicit after Feature Catalog save.

## Scope

- Added schema apply fields to `FeatureCatalogSaveResult`.
- Marked successful catalog saves as requiring app restart for schema-driven table changes.
- Included the restart-required message in the save success message.
- Added focused test coverage for the save result contract.

## Non-goals Held

- No broad Predict UI rewrite.
- No live schema refresh implementation.
- No unrelated table UX changes.

## Verification

- `python3 -m compileall apps/train tests/test_apps_train_feature_catalog.py` - OK
- `python3 -m pytest tests/test_apps_train_feature_catalog.py` - OK, 19 passed
- `git diff --check` - OK
- `python3 -B tools/check_code_structure.py` - NG, pre-existing unrelated raw hex literal:
  - `apps/calculator/ui/calculator_app.py:105`

## Changed Files

- `apps/train/application/feature_catalog/io_models.py`
- `apps/train/application/feature_catalog/service.py`
- `tests/test_apps_train_feature_catalog.py`

## Change Gate

```yaml
change_gate:
  new_source: none
  hotspot_delta: none
  code_map_check: not_required
  ui_literal_exemption: none
  reuse_commonization: not_required
  report_exemption: none
  read_ledger: included
```

## Risk

Live refresh remains future work. This slice intentionally chooses the honest restart-required path allowed by the correction design.

## Commit / Push

Committed as one Slice 3 commit. Push remains deferred until all requested remaining slices are complete.

## Next

Arc 13.5A Slice 4 - Model compatibility guard.
