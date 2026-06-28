# 593 - Mock Smoke Manifest Option

## Goal

Improve DEV-only mock smoke reproducibility by adding an optional
`mock_smoke_manifest.json` output.

## Scope

- Added `--manifest` to both mock smoke generators.
- Added shared manifest upsert logic that records generated output path, seed,
  rows, and UTC `created_at` for `prediction_artifact` and `training_data`.
- Updated README instructions and `.gitignore` so generated manifest JSON stays
  untracked.
- Added focused tests for manifest accumulation and ignore coverage.
- Regenerated the code map after tools/test source changes.

## Modified Files

- `.gitignore`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `tools/dev/mock_smoke/generators.py`
- `tools/dev/mock_smoke/generate_mock_prediction_artifact.py`
- `tools/dev/mock_smoke/generate_mock_training_data.py`
- `tools/dev/mock_smoke/README.md`
- `tests/test_mock_smoke_generators.py`
- `result_reports/active/593_mock-smoke-manifest-option.md`

## Code Map Reuse Gate

```yaml
reuse_commonization: reused-existing-owner
```

- The manifest option extends the existing `tools/dev/mock_smoke` owner.
- No new helper package or production path was introduced.

## Verification Results

- `python3 -B -m py_compile tools/dev/mock_smoke/*.py`: OK.
- `python3 -B -m pytest tests -k "mock_smoke or mock or artifact"`: OK,
  6 passed and 1342 deselected.
- `python3 -B tools/dev/mock_smoke/generate_mock_prediction_artifact.py --output-dir /tmp/predictor_v3_mock_smoke --manifest`: OK.
- `python3 -B tools/dev/mock_smoke/generate_mock_training_data.py --output-dir /tmp/predictor_v3_mock_smoke --manifest`: OK.
- `python3 -B tools/code_checker/build_reference_map.py`: OK, regenerated.
- `python3 -B tools/code_checker/build_reference_map.py --check`: OK, status
  `FRESH`.
- `python3 -B tools/check_code_structure.py`: OK with pre-existing calculator
  soft warnings only.
- `git diff --check`: OK.

## Generated Outputs

- `/tmp/predictor_v3_mock_smoke/mock_smoke_model.pkl`
- `/tmp/predictor_v3_mock_smoke/mock_smoke_training_data.csv`
- `/tmp/predictor_v3_mock_smoke/mock_smoke_manifest.json`

These files are generated DEV smoke outputs and are not committed.

## Excluded Scope

- No production app behavior changes.
- No `apps/predict/`, `apps/train/`, `core/ml` algorithm/schema, calculator,
  or mapping behavior changes.
- No cleanup command implementation in this slice.

## Next Action

- Arc10 manual smoke with mock artifact.

## Change Gate

```yaml
change_gate:
  new_source: none
  hotspot_delta: none
  code_map_check: regenerated
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
  report_exemption: none
  read_ledger: included
```
