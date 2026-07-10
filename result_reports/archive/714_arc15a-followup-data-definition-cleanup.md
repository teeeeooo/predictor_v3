# Arc 15A Follow-up Data Definition Cleanup

## Goal

Clean up minor Arc 15A audit notes before Arc 15B by removing the hard-coded
training data filename from Data Definition readiness, making projection order
policy explicit, and improving parity issue messages while preserving current
projection behavior.

## Modified Files

- `core/data_definition/readiness.py`
- `core/data_definition/projection.py`
- `core/data_definition/validation.py`
- `tests/test_data_definition_core_projection.py`
- `result_reports/active/714_arc15a-followup-data-definition-cleanup.md`

## Cleanup Summary

- Removed the Data Definition core default path to `data/Practice_4.csv`.
- Kept `build_readiness_checks(projected_features, training_data_path=None)`,
  but default training header readiness is now `not_evaluated` and non-blocking.
- Header-only passive checks run only when the caller explicitly provides a
  training data path.
- Added `FEATURE_PROJECTION_COMPATIBILITY_ORDER` for the current
  `features.csv` parity order: input, auto, one-hot, result, derived.
- Improved parity mismatch/orphan/extra issue messages with row index and
  expected/actual row identity.
- Added focused tests for no default training filename, explicit tmp CSV header
  checks, explicit projection order, and parity message identity.

## Hard-coded Path Policy

Data Definition core does not own training data file locations. The caller must
provide a training CSV path when it wants Arc 15A passive header validation.
Missing explicit paths are not failures. Missing explicit files are reported as
`unavailable`; incomplete headers are reported as `missing`.

## Validation Result

- `python3 -m py_compile $(find core/data_definition -name '*.py' -print)`:
  OK.
- `python3 -m pytest tests/test_data_definition_core_projection.py tests/test_predict_schema_catalog_v2_projection.py`:
  OK, 23 passed.
- `python3 -B tools/check_code_structure.py`: OK with pre-existing calculator
  hotspot warnings and stale code-map reminder; no changed-file warning.
- `python3 -B tools/code_checker/build_reference_map.py --check`: STALE;
  recorded as source-change evidence, no unrelated code-map regeneration.
- `git diff --check`: OK.
- `git status --short`: OK; only expected Data Definition files, focused test,
  and this report are present.
- `git diff --name-only`: OK; tracked modifications are
  `core/data_definition/projection.py`, `core/data_definition/readiness.py`,
  `core/data_definition/validation.py`, and
  `tests/test_data_definition_core_projection.py`.
- `git diff --stat`: OK; tracked diff is 4 files changed, 165 insertions, 14
  deletions before staging this new report.

## Manual Check

Manual GUI/training/model checks are not required for this core-only cleanup.

## Excluded Scope

- No Arc 15B UI implementation.
- No Add/Edit/Save behavior.
- No runtime behavior changes.
- No config, data, mapping, model, Predict, Train/Admin, Feature Catalog, or
  Data Mapping Manager changes.
- No model retrain, model artifact inspection, GUI smoke, broad refactor, main
  merge, or main push.

## Structure / Change Gate

change_gate:
  new_source: none
  hotspot_delta: none
  code_map_check: checked
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
  report_exemption: none
  read_ledger: checked

Read Ledger:
- `docs/designs/2026-07-06-arc15-unified-data-definition-manager-foundation.md`:
  Arc 15A readiness/projection constraints, reason: follow-up boundary.
- `result_reports/active/713_arc15a-data-definition-core-projection-validator.md`:
  Arc 15A audit result and validation contract, reason: cleanup target.
- `core/data_definition/readiness.py`: current readiness behavior, reason:
  remove hard-coded training filename.
- `core/data_definition/projection.py`: current projection order, reason:
  make compatibility order explicit.
- `core/data_definition/validation.py`: current parity issue messages, reason:
  improve row identity.
- `core/data_definition/model.py` and `core/data_definition/report_model.py`:
  model fields, reason: confirm no model expansion needed.
- `tests/test_data_definition_core_projection.py`: existing focused tests,
  reason: extend coverage.
- broad read: none.
- repeated read: none.

## Next Action

Arc 15B — Data Definition Read-only UI.
