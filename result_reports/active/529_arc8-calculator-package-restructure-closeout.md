# 529 - Arc 8 Calculator Package Restructure Closeout

## Goal

Close Arc 8 after moving calculator implementation ownership under
`core/calculators/` without changing formulas, schemas, fixtures, golden data,
public calculator APIs, or calculator behavior.

## Completed Scope

- Arc 7 polish:
  - Removed an unreachable duplicate block from `core/ml/inference.py`.
- Calculator package shell:
  - Added `core/calculators/`, `core/calculators/adapters/`, and
    `core/calculators/standards/` package boundaries.
- Dispatcher/profile/adapter ownership:
  - Moved dispatcher and profile implementation to `core/calculators/`.
  - Moved calculator input/prediction/unit adapter implementation to
    `core/calculators/adapters/`.
  - Preserved root compatibility wrappers.
- Standard-engine ownership:
  - Moved ISO16358, KS C 9306, EN14825, AHRI SEER2, AHRI HSPF2, and AS/NZS
    Excel compatibility implementation to `core/calculators/standards/`.
  - Preserved root compatibility wrappers.
- Validation and code map:
  - Ran focused calculator tests across dispatcher/profiles/adapters and
    standard engines.
  - Regenerated `docs/code_map/CODEBASE_REFERENCE_MAP.md` after the structure
    move.
  - Corrected EN14825 direct-constructor default config lookup after relocation.
- Closeout docs:
  - Updated `docs/WORK_PLAN.md` next action to Arc 9.
  - Updated `project_brief.md` arc state.
  - Updated `docs/architecture/project_architecture.md` to describe
    `core/calculators` as current calculator implementation owner and root
    `core/calculator_*` modules as compatibility wrappers.

## Preserved Contracts

- Calculator formulas and result contracts unchanged.
- Region config files unchanged.
- Fixtures and golden data unchanged.
- Public root imports preserved through compatibility wrappers.
- `app_calculator.py`, `app_predict.py`, and `app_train.py` entrypoints
  unchanged.
- No dependency, model artifact, or data changes.

## Verification

- `python3 -B -m pytest tests/test_calculator_dispatcher.py tests/test_calculator_profiles.py tests/test_en14825_golden.py tests/test_ahri_seer2_smoke.py tests/test_ahri_hspf2_smoke.py tests/test_ahri_hspf2_v3_smoke.py tests/test_iso16358_hspf_smoke.py tests/test_iso16358_cspf_iso_t1_default_golden.py tests/test_iso16358_hspf_official_exact_golden.py tests/test_iso16358_cspf_hong_kong_config.py tests/test_iso16358_hspf_hong_kong_config.py tests/test_calculator_input_adapter.py tests/test_calculator_prediction_adapter.py tests/test_calculator_unit_adapter.py`
  - Result: 167 passed.
- `python3 -B -m py_compile core/*.py core/ml/*.py core/predictor_schema/*.py core/mapping/*.py core/calculators/*.py core/calculators/adapters/*.py core/calculators/standards/*.py scripts/update_mapping.py app_calculator.py app_predict.py app_train.py`
  - Result: passed.
- `python3 -B -c "import app_calculator; import app_predict; import app_train"`
  - Result: passed.
- Root/new dispatcher identity smoke:
  - Result: passed.
- Calculator profile creation smoke for KS, ISO/Hong Kong, AHRI, and EN14825:
  - Result: passed.
- `python3 -B tools/check_code_structure.py`
  - Result: passed with soft warnings for existing large calculator/UI files and a code-map freshness reminder.
- `python3 -B tools/code_checker/build_reference_map.py --check`
  - Result: warning-first check reports stale after the Slice 5 refresh commit because the map records the pre-commit hash and dirty generated-map metadata. No source structure changed after that refresh; this is recorded for the next code-map maintenance slice.
- `git diff --check`
  - Result: passed.
- `git status --short`
  - Result: expected closeout docs/report before commit.

## Skipped

- Full pytest: prompt requested focused calculator tests.
- GUI smoke: no UI behavior was changed.
- Packaging check: no dependency/package artifact changes.

## Known Follow-Up

- Root compatibility callers remain in apps/tests and should be migrated only in
  an approved caller-migration slice.
- Root compatibility wrappers are transition safety, not final architecture.
- Code map tool metadata remains commit-hash sensitive after committed refreshes.

## Next

Arc 9 - PySide6 Predictor Schema / Mapping Recovery.
