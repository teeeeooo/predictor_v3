# Arc 15E Feature Catalog Owner Switch

## Goal

Demote Feature Catalog from canonical editor to legacy compatibility surface while keeping read/export/parity behavior available.

## Scope

- Added default canonical-save guard for the current `config/ml/features.csv` path.
- Kept tmp-path compatibility saves available for tests and review artifacts.
- Updated controller load messages to mark Feature Catalog as a legacy compatibility surface and Data Definition as canonical owner.
- Added focused owner-switch tests for canonical save blocking, tmp-path compatibility, controller messaging, and panel save-block feedback.

## Non-goals

- No actual `config/ml/features.csv` or `config/predict/schema.csv` modification.
- No Data Mapping, schema writer, Predict runtime, training, model, retrain, or artifact activation changes.
- No Feature Catalog tab deletion.

## Verification

- `python3 -B tools/check_code_structure.py`: passed with existing unrelated soft warnings.
- `python3 -B tools/code_checker/build_reference_map.py --check`: checked; reference map remains stale and was not regenerated.
- `python3 -m py_compile $(find core/ml core/data_definition apps/train -name '*.py' -print)`: passed.
- `python3 -m pytest tests/test_feature_catalog_*.py tests/test_train_feature_catalog_*.py tests/test_data_definition_core_projection.py tests/test_data_definition_schema_writer.py`: passed, 29 tests.
- Compatibility check: `python3 -m pytest tests/test_apps_train_feature_catalog.py`: passed, 21 tests.
- Known pre-existing broader-suite caveat: `python3 -m pytest tests/test_apps_train_feature_catalog.py tests/test_ml_feature_catalog.py` fails during `tests/test_ml_feature_catalog.py` collection because `core.predictor_schema.columns` no longer exports `ROLE_PRESENTATION_DEFAULTS`; this was not introduced by this slice and is outside the requested validation command.
- `git diff --check`: passed after report creation.
- `git status --short`: expected slice 4 source/test/report files only before staging.

## Task Results

- `FeatureCatalogService.save_records()` blocks canonical default path writes with a legacy compatibility message before any writer call.
- Explicit non-default paths still use the existing writer/validation path, preserving compatibility tests and export-review workflows.
- `FeatureCatalogController.refresh()` now labels the surface as legacy compatibility and names Data Definition as canonical owner.
- The existing panel surfaces the controller message and blocked save result without modifying the actual panel file; the prompt path `apps/train/ui/feature_catalog_panel.py` does not exist in this repo.

## Change Gate

```yaml
change_gate:
  new_source: none
  hotspot_delta: wiring-only
  code_map_check: checked
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
  report_exemption: none
  read_ledger: included
```

- `hotspot_delta`: wiring-only guard/message additions in existing Feature Catalog service/controller owners.
- `reuse_commonization`: reused the existing save result/controller/panel feedback path instead of adding a new advanced-save framework.

## Read Ledger

- `apps/train/application/feature_catalog/service.py`: save path and writer boundary.
- `apps/train/controllers/feature_catalog_controller.py`: UI-facing owner-mode messages.
- `apps/train/ui/feature_catalog/panel.py`: existing panel feedback behavior; read only, not modified because prompt allowed path does not exist.
- `core/ml/feature_catalog.py`, `core/ml/feature_catalog_projection.py`: compatibility read/projection behavior.
- `tests/test_apps_train_feature_catalog.py`: compatibility save/export behavior.
- broad read: none.
- repeated read: none.

## Structure Warnings

Existing unrelated calculator/code-map warnings remain. No changed/new source file emitted a structure warning.

## Known Failures / Risks

- The visible tab title remains `Feature Catalog`; the controller/panel status text now provides the legacy compatibility warning. Renaming the actual tab/panel file would require touching `apps/train/ui/feature_catalog/panel.py`, which was outside the prompt's exact allowed path.
- Canonical default save is guarded; tmp-path saves remain available for tests and compatibility artifacts.

## Scope Compliance

- No `config/**`, `data/**`, `model/**`, Data Mapping, schema writer, Predict runtime, training, retrain, artifact activation, main merge, or main push changes.
- No `features.csv` direct canonical write occurred.

## Commit / Push

Slice 4 source, test, and report changes are included in the slice commit. Push is deferred until all requested slices complete.

## Project Memory Delta

No memory seed update required. The slice completes the Feature Catalog owner demotion without adding a new unresolved decision.
