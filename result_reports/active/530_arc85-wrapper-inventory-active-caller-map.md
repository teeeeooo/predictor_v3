# 530 - Arc 8.5 Wrapper Inventory and Active Caller Map

## Goal

Inventory the remaining root compatibility wrappers and flat root
calculator-adjacent adapters before Arc 8.5 active caller migration and wrapper
retirement.

## Wrapper Candidates

Root ML/schema/mapping compatibility surfaces:

- `core/predictor.py` -> wrapper for `core.ml.inference`.
- `core/data_pipeline.py` -> wrapper for `core.ml.preprocessing`.
- `core/models.py` -> wrapper for `core.ml.registry`.
- `core/trainer.py` -> wrapper for `core.ml.training`.
- `core/constants.py` -> compatibility surface for `core.ml.artifacts`,
  `core.ml.features`, `core.mapping.paths`, `core.predictor_schema.columns`,
  and `LOG_DIR`.

Root calculator compatibility wrappers:

- `core/calculator_dispatcher.py` -> `core.calculators.dispatcher`.
- `core/calculator_profiles.py` -> `core.calculators.profiles`.
- `core/calculator_input_adapter.py` -> `core.calculators.adapters.input_adapter`.
- `core/calculator_prediction_adapter.py` -> `core.calculators.adapters.prediction_adapter`.
- `core/calculator_unit_adapter.py` -> `core.calculators.adapters.unit_adapter`.
- `core/calculator_iso16358.py` -> `core.calculators.standards.iso16358`.
- `core/calculator_ks_c9306.py` -> `core.calculators.standards.ks_c9306`.
- `core/calculator_en14825.py` -> `core.calculators.standards.en14825`.
- `core/calculator_ahri_seer2.py` -> `core.calculators.standards.ahri_seer2`.
- `core/calculator_ahri_hspf2.py` -> `core.calculators.standards.ahri_hspf2`.
- `core/calculator_asnzs_hspf_excel.py` -> `core.calculators.standards.asnzs_hspf_excel`.

Flat root calculator-adjacent adapters to move, then delete:

- `core/calculator_result_adapter.py` -> `core.calculators.adapters.result_adapter`.
- `core/calculator_ranking_adapter.py` -> `core.calculators.adapters.ranking_adapter`.

Entry/script wrapper:

- `scripts/update_mapping.py` remains a script/entrypoint wrapper with file-dialog
  behavior and is not a `core` compatibility wrapper deletion target in this Arc.

## Active Caller Map

Production/current app callers:

- `apps/predict/services/prediction_service.py` imports `core.constants` and
  `core.predictor`.
- `apps/calculator/ui/**` imports `core.calculator_dispatcher` and
  `core.calculator_en14825`.

Legacy/reference-only UI callers that must remain importable:

- `ui/base_view.py`, `ui/base_model.py`, `ui/predict_window.py`, and
  `ui/train_window.py` import `core.constants`, `core.predictor`, or
  `core.trainer`.

Internal core caller:

- `core/utils.py` imports `LOG_DIR` from `core.constants`.
- `core/calculator_result_adapter.py` imports `core.calculator_profiles` and
  must move to the calculator adapter owner path.
- `core/_legacy/calculator_iso16358_legacy.py` imports `core.calculator_ks_c9306`;
  this historical legacy module still needs import-path migration if it remains
  importable under active source.

Active tests:

- Calculator tests import root calculator wrappers heavily and must migrate to
  `core.calculators.*`.
- ML/schema tests that import `core.constants`, `core.predictor`,
  `core.models`, `core.trainer`, or `core.data_pipeline` must migrate to
  owner packages.
- `tests/test_calculator_schema_boundaries.py` explicitly checks flat root
  adapter paths and must be updated when result/ranking adapters move.

Current docs requiring update during later slices:

- `docs/WORK_PLAN.md`, `project_brief.md`, and
  `docs/architecture/project_architecture.md` currently describe root
  compatibility wrappers as accepted transition state.
- `docs/architecture/project_wide_architecture_restructuring_plan.md` is an
  architecture input/decision history document and may retain historical
  examples unless closeout docs require a current-path note.
- `docs/code_map/CODEBASE_REFERENCE_MAP.md` is generated and should be
  refreshed after structure changes.

Historical/archive references not edited in this inventory:

- `docs/archive/**`.
- `result_reports/archive/**`.
- Historical design/report examples unless they block active absence guards.

## Deletion and Move Plan

Slice 2 delete after migration:

- `core/predictor.py`
- `core/data_pipeline.py`
- `core/models.py`
- `core/trainer.py`
- `core/constants.py`

Slice 3 delete after migration:

- `core/calculator_dispatcher.py`
- `core/calculator_profiles.py`
- `core/calculator_input_adapter.py`
- `core/calculator_prediction_adapter.py`
- `core/calculator_unit_adapter.py`
- `core/calculator_iso16358.py`
- `core/calculator_ks_c9306.py`
- `core/calculator_en14825.py`
- `core/calculator_ahri_seer2.py`
- `core/calculator_ahri_hspf2.py`
- `core/calculator_asnzs_hspf_excel.py`

Slice 4 move and delete:

- `core/calculator_result_adapter.py`
- `core/calculator_ranking_adapter.py`

## Blockers

None found in inventory. If a later slice reveals behavior changes are required
to delete a wrapper, that slice should stop and report rather than preserving
the wrapper.

## Validation

- Wrapper candidate files inspected.
- Active caller searches run for ML/constants wrappers, calculator wrappers,
  and result/ranking adapters.
- `git diff --check`: pending after report write.
- `git status --short`: pending after report write.

## Next

Slice 2 - ML/root constants caller migration and root wrapper deletion.
