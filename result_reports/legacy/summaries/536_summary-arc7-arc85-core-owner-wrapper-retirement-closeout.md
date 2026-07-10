# 536 Summary - Arc 7 to Arc 8.5 Core Owner and Wrapper Retirement Closeout

## Goal

Compact the completed Arc 7, Arc 8, and Arc 8.5 active reports into one source
summary so active reports can return to current blockers and next-decision
evidence only.

## Covered Reports

- `517_active-report-lifecycle-cleanup-architecture-reset.md`
- `518_arc7-restructure-doc-realignment.md`
- `519_arc7-package-shell-boundary-imports.md`
- `520_arc7-ml-implementation-move.md`
- `521_arc7-predictor-schema-move.md`
- `522_arc7-mapping-package-move.md`
- `523_arc7-core-ml-schema-mapping-closeout.md`
- `524_arc7-polish-inference-code-map-decision.md`
- `525_arc8-calculator-package-shell.md`
- `526_arc8-dispatcher-profiles-adapters-move.md`
- `527_arc8-standard-engines-move.md`
- `528_arc8-focused-tests-caller-classification-code-map.md`
- `529_arc8-calculator-package-restructure-closeout.md`
- `530_arc85-wrapper-inventory-active-caller-map.md`
- `531_arc85-ml-constants-wrapper-retirement.md`
- `532_arc85-calculator-wrapper-retirement.md`
- `533_arc85-flat-calculator-adapter-move.md`
- `534_arc85-focused-validation-wrapper-absence.md`
- `535_arc85-root-wrapper-retirement-closeout.md`

## Arc 7 Closeout

- `core/ml/` became the owner for inference, preprocessing, registry,
  training, feature/target constants, and artifact paths.
- `core/predictor_schema/` became the owner for predictor table columns,
  indexes, dropdown metadata, column groups, and row count constants.
- `core/mapping/` became the owner for mapping paths, repository loading,
  pure update conversion, and future autofill policy extraction.
- `core/common/` was established as the common helper/path boundary.
- The initial Arc 7 migration preserved root wrappers temporarily for active
  callers and recorded that wrappers were transition safety only.

## Arc 8 Closeout

- `core/calculators/` became the owner for calculator profiles and dispatcher.
- `core/calculators/adapters/` became the owner for input, prediction, and unit
  adapters.
- `core/calculators/standards/` became the owner for ISO16358, KS C 9306,
  EN14825, AHRI SEER2, AHRI HSPF2, and AS/NZS Excel compatibility engines.
- EN14825 direct-constructor config lookup was corrected after relocation to
  keep resolving the existing `data/region_configs/en14825.json` SSOT.
- Focused calculator tests and profile creation smokes passed, and the code map
  was refreshed after the structure move.

## Arc 8.5 Closeout

- Root ML wrappers were deleted:
  - `core/predictor.py`
  - `core/data_pipeline.py`
  - `core/models.py`
  - `core/trainer.py`
  - `core/constants.py`
- Root calculator wrappers were deleted:
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
- Flat root calculator-adjacent adapters moved and root files were deleted:
  - `core/calculator_result_adapter.py` ->
    `core/calculators/adapters/result_adapter.py`
  - `core/calculator_ranking_adapter.py` ->
    `core/calculators/adapters/ranking_adapter.py`
- Active production code, legacy/reference-only `ui/` imports, and tests were
  migrated to package owner paths.
- Active wrapper absence guards passed with `docs/archive/**` excluded.

## Current Owner Paths

- ML: `core/ml/`
- Predictor schema: `core/predictor_schema/`
- Mapping: `core/mapping/`
- Common paths/helpers: `core/common/`
- Calculator profiles/dispatcher/adapters/standards:
  `core/calculators/`
- Calculator result/ranking envelope adapters:
  `core/calculators/adapters/result_adapter.py` and
  `core/calculators/adapters/ranking_adapter.py`

## Verification Summary

- Arc 8.5 focused calculator tests passed:
  - dispatcher/input/prediction/result/ranking/envelope chain and selected Tk
    calculator UI guard tests.
- Arc 8 focused calculator set passed:
  - profiles, EN14825 golden, AHRI smoke, ISO/Hong Kong smoke/golden, unit
    adapter.
- Final py_compile and app import smokes passed.
- Final owner import smoke passed.
- Active wrapper absence guards passed.
- `tools/check_code_structure.py` passed with existing large-file soft warnings.
- Code map was regenerated during Arc 8.5 validation and closeout, with the
  known commit-hash metadata caveat recorded in the closeout report.

## Deferred / Known Risks

- Code map freshness can report stale immediately after a commit because the
  generated metadata records the pre-commit hash.
- `model/model.pkl` remains absent in this checkout, so real model prediction
  success smoke remains incomplete.
- PySide6 Predictor schema/mapping recovery was intentionally not implemented
  in Arc 7, Arc 8, or Arc 8.5.
- Worker/progress/cancel UI remains deferred.
- Memory seed has crossed the maintenance-audit threshold; a future dedicated
  memory seed maintenance task should compact or audit entries.

## Memory Seed

Updated:

- registered this summary under Source Summaries;
- added one durable decision that root compatibility wrappers are retired and
  active code should import package owner paths directly.

## Next Action

Arc 9 - PySide6 Predictor Schema / Mapping Recovery.
