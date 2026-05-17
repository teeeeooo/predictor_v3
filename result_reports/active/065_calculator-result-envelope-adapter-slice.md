# 065 Calculator Result Envelope Adapter Slice

## Goal

Start the first implementation slice from the calculator result envelope / ML adapter design without changing calculator public APIs.

## Scope

- `core/calculator_result_adapter.py`
- `tests/test_calculator_result_adapter.py`

## Non-goals

- No ML / inverse-search implementation.
- No calculator return dict structure change.
- No region config schema change.
- No UI table schema or ML registry dependency.

## Changed Files

- `core/calculator_result_adapter.py`
- `tests/test_calculator_result_adapter.py`
- `result_reports/active/065_calculator-result-envelope-adapter-slice.md`

## Verification

- `python3 -B -m py_compile core/calculator_result_adapter.py tests/test_calculator_result_adapter.py`
  - passed
- `python3 -B -m pytest tests/test_calculator_result_adapter.py tests/test_ahri_seer2_smoke.py tests/test_calculator_dispatcher.py -q`
  - `17 passed`
- `rg -n "MODEL_REGISTRY|core\\.models|ui\\.|sklearn|pandas|numpy|COLUMNS|region_configs" core/calculator_result_adapter.py tests/test_calculator_result_adapter.py`
  - no matches
- `git diff --check`
  - passed before source commit.

## Task Results

- Added `wrap_calculator_result_envelope()` as an adapter-owned helper.
- The first supported profile is intentionally narrow: `ahri_usa_seer2`.
- Envelope fields include `calculator_profile_id`, `calculator_id`, `metric`, `value`, `units`, `raw_result`, `diagnostics`, and `warnings`.
- Existing AHRI SEER2 calculator output remains unchanged and is preserved under `raw_result`.
- Unsupported profiles and missing metric keys fail fast.

## Known Risks

- Only AHRI SEER2 result wrapping is implemented. Calculator input envelopes and other profiles remain future slices.
- `project_log.md` update is deferred to the final audit_3 managed-document update so the related adapter/schema/UI work is logged once.

## Commit / Push

- Source commit: `628783f` (`feat: add calculator result envelope adapter`).
- Report commit: this commit (`report: record calculator result adapter slice`).
- Push: deferred until final objective push.
