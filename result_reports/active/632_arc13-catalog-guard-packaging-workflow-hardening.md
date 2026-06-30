# 632 Arc 13 Catalog Guard Packaging Workflow Hardening

## Goal

Recheck the ML feature catalog runtime guard coverage, reduce packaging/resource
risk around `config/ml/features.csv`, and document the user workflow for feature
catalog edits.

## Changed Files

- `core/ml/feature_catalog_validation.py`
- `tests/test_ml_feature_catalog.py`
- `docs/workflows/ml_feature_catalog_workflow.md`
- `docs/WORK_PLAN.md`
- `project_brief.md`
- `project_log.md`
- `result_reports/active/632_arc13-catalog-guard-packaging-workflow-hardening.md`

## Registry / Leakage Guard Recheck

Existing coverage already checked that registry target, exclude, and allowed
names exist in the catalog.

This slice tightened the guard:

- registry targets must be active catalog `result` rows;
- target-rule keys must be active catalog `result` rows;
- focused tests verify catalog result rows match `TARGETS`;
- focused tests verify `prepare_pipeline()` keeps global target names out of
  feature matrices;
- focused tests verify target-specific `exclude` and `allowed` rules remain
  enforceable after catalog projection;
- seasonal calculator output names remain blocked from model input projection
  by catalog validation.

## Packaging / Resource Guard

`config/ml/features.csv` is now required at runtime by ML feature constants,
predictor schema projection, one-hot adapter projection, training header guard,
and inference zero-fill policy.

Checked packaging state:

- no active `pyproject.toml`, `setup.py`, `setup.cfg`, `MANIFEST.in`,
  PyInstaller `.spec`, Dockerfile, docker-compose file, or GitHub workflow file
  was present in the repository root search scope;
- no broad packaging framework was added;
- focused tests assert `DEFAULT_CATALOG_PATH` points to
  `config/ml/features.csv` under the repo root and that the file exists;
- existing missing-file errors include the catalog path.

The workflow document records that packaging or deployment must include
`config/ml/features.csv`.

## Feature Edit Workflow

Added `docs/workflows/ml_feature_catalog_workflow.md`.

The workflow documents:

- `features.csv` is the ML feature contract;
- `ml_name` equals raw training data header and internal ML name;
- no training header alias or mapping layer exists;
- feature add/change steps;
- role-specific CSV fields;
- width/color and UI-only columns remain code-owned;
- one-hot groups are catalog-owned;
- zero-fill is allowed only for Cooling/Heating Capa/Power;
- training fails when headers do not match catalog `ml_name`;
- Numbers/Excel edits must preserve UTF-8 comma CSV.

## Same-slice Risk Cleanup

Handled in this slice:

- registry validator no longer accepts a target that is present in the catalog
  only as a non-result role;
- registry leakage/allowed rule behavior is guarded by focused tests;
- catalog runtime resource path has a direct focused test;
- user workflow docs now match the current code owners.

Not changed:

- no production training dataset was edited;
- no model was trained;
- no UI layout or predictor schema contract was changed;
- no packaging framework was introduced.

## Read Ledger

- `config/ml/features.csv`: full small file, reason: runtime catalog policy.
- `core/ml/feature_catalog.py`: targeted loader/default path.
- `core/ml/feature_catalog_projection.py`: targeted projection helper review.
- `core/ml/feature_catalog_validation.py`: full file, reason:
  registry/catalog guard hardening.
- `core/ml/features.py`: full small file, reason: runtime catalog import
  surface.
- `core/ml/training.py`: targeted training guard boundary.
- `core/ml/inference.py`: targeted zero-fill guard boundary.
- `core/ml/registry.py`: full small file, reason: target/rule consistency.
- `core/ml/artifacts.py`: full small file, reason: path owner check.
- `core/predictor_schema/columns.py`: targeted catalog runtime dependency.
- `core/predictor_schema/ui_columns.py`: targeted UI-only owner boundary.
- `apps/predict/adapters/row_to_ml_input_adapter.py`: targeted one-hot catalog
  dependency.
- `apps/predict/adapters/prediction_result_adapter.py`: targeted target result
  mapping.
- `docs/designs/2026-06-30-arc13-ml-feature-manifest-design-gate.md`:
  targeted workflow/schema sections.
- `result_reports/active/631_arc13-training-input-contract-runtime-guard.md`:
  targeted prior risk/next sections.
- `docs/WORK_PLAN.md`: current slice/next action sections.
- packaging/build/devcontainer search: root-level packaging candidates by
  filename.
- broad read: none.

## change_gate

```yaml
change_gate:
  new_source: small
  hotspot_delta: wiring-only
  code_map_check: regenerated
  ui_literal_exemption: none
  reuse_commonization: checked
  report_exemption: none
  read_ledger: included
```

The new source is documentation only. Runtime code changes are limited to
registry/catalog validation tightening.

## Known Risks / Open Questions

- Future packaging work must explicitly include `config/ml/features.csv` if a
  packaging system is added.
- Real production training data still needs to be catalog-aligned outside this
  repository before training.

## Next Action

Arc 13 Slice 7 - Arc 13 Final Closeout.

## Verification

- `python3 -B -m compileall -q core/ml tests/test_ml_feature_catalog.py`: OK.
- `python3 -B -m pytest tests/test_ml_feature_catalog.py -q`: OK, 40
  passed.
- `python3 -B -m compileall -q core/ml core/predictor_schema apps/predict apps/train tests`:
  OK.
- `python3 -B -m pytest tests -k "feature_catalog"`: OK, 40 passed and
  1418 deselected.
- `python3 -B -m pytest tests -k "training or train or inference or ml"`:
  OK, 85 passed and 1373 deselected.
- `python3 -B -m pytest tests -k "predict_schema or prediction_adapter or prediction_usecase or apps_predict"`:
  OK, 132 passed and 1326 deselected.
- `python3 -B tools/code_checker/build_reference_map.py --check`: initially
  stale after source changes.
- `python3 -B tools/code_checker/build_reference_map.py`: regenerated
  `docs/code_map/CODEBASE_REFERENCE_MAP.md`.
- `python3 -B tools/code_checker/build_reference_map.py --check`: OK, fresh.
- `python3 -B tools/check_code_structure.py`: OK with pre-existing calculator
  soft warnings outside this slice.
- `git diff --check`: OK.
- `git status --short`: task files only before staging.

## Commit / Push

- pending commit for Slice 6; push intentionally deferred until Slice 7 commit.

## Project Memory Delta

- type: decision
  topic: Arc 13 catalog guard and workflow
  content: Registry targets must be active catalog result rows, catalog runtime
    presence is guarded, and user feature edits are documented around
    `features.csv` and `ml_name` training headers.
  keywords: arc13, feature-catalog, registry, packaging, workflow
