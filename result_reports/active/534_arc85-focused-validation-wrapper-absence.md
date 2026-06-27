# 534 - Arc 8.5 Focused Validation and Wrapper Absence Guard

## Goal

Verify that active production code and tests no longer depend on root
compatibility wrappers after Arc 8.5 migrations.

## Validation

- `python3 -B -m pytest tests/test_calculator_dispatcher.py tests/test_calculator_input_adapter.py tests/test_calculator_prediction_adapter.py tests/test_calculator_result_adapter.py tests/test_calculator_ranking_adapter.py tests/test_calculator_envelope_chain.py tests/test_ui_tk_calculator_foundation.py tests/test_ui_tk_hong_kong_cspf_batch_spec.py`
  - First run exposed an existing test owner drift: the ISO fit-path test
    patched `iso16358_tab.TkContentHuggingShell`, while shell composition is now
    owned by `apps.calculator.ui.lifecycle.controller`.
  - Corrected the test to patch the lifecycle controller owner and call the
    public `fit_toplevel_to_current_content_once()` method.
  - Re-run result: 120 passed.
- Arc 8 focused calculator set:
  - `python3 -B -m pytest tests/test_calculator_profiles.py tests/test_en14825_golden.py tests/test_ahri_seer2_smoke.py tests/test_ahri_hspf2_smoke.py tests/test_ahri_hspf2_v3_smoke.py tests/test_iso16358_hspf_smoke.py tests/test_iso16358_cspf_iso_t1_default_golden.py tests/test_iso16358_hspf_official_exact_golden.py tests/test_iso16358_cspf_hong_kong_config.py tests/test_iso16358_hspf_hong_kong_config.py tests/test_calculator_unit_adapter.py`
  - Result: 99 passed.
- `python3 -B -m py_compile core/*.py core/ml/*.py core/predictor_schema/*.py core/mapping/*.py core/common/*.py core/calculators/*.py core/calculators/adapters/*.py core/calculators/standards/*.py scripts/update_mapping.py app_calculator.py app_predict.py app_train.py`
  - Result: passed.
- `python3 -B -c "import app_calculator; import app_predict; import app_train"`
  - Result: passed.
- `python3 -B -c "from core.ml.inference import predict_row; from core.ml.training import train_all_models; from core.predictor_schema.columns import COLUMNS; from core.mapping.repository import load_mapping_data; from core.calculators.dispatcher import create_calculator_for_profile"`
  - Result: passed.
- Active-tree ML/root wrapper absence search with `docs/archive/**` excluded:
  - Result: no hits.
- Active-tree calculator root wrapper absence search with `docs/archive/**`
  excluded:
  - Result: no hits.
- Active-tree result/ranking root adapter absence search with `docs/archive/**`
  excluded:
  - Result: no hits.
- Root file absence guard for all ML, constants, calculator, result, and ranking
  root files:
  - Result: passed.
- `python3 -B tools/check_code_structure.py`
  - Result: passed with existing soft warnings for large calculator/UI files.
- `python3 -B tools/code_checker/build_reference_map.py`
  - Result: regenerated code map after wrapper retirement.
- `python3 -B tools/code_checker/build_reference_map.py --check`
  - Result: fresh against current commit; warning notes the expected
    uncommitted working tree.
- `git diff --check`
  - Result: passed.
- `git status --short`
  - Result: expected code map/test/report changes before commit.

## Changed For Validation

- `tests/test_ui_tk_calculator_foundation.py`
  - Updated the shell-fit monkeypatch to the current lifecycle controller owner.
  - No production code changed for this test correction.

## Excluded

- No calculator formula, config, fixture, golden, public result key, ML
  algorithm, feature list, target list, model artifact, mapping schema, PySide6
  recovery, worker/progress, or Trainer app behavior changes.

## Next

Slice 6 - Arc 8.5 closeout and next action update.
