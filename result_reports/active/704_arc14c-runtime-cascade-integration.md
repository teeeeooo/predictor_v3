# Arc 14C Runtime Cascade Integration

## Goal

Connect Data Mapping Manager generated `mapping.json` runtime sections to
Predict dropdown/autofill cascade behavior while preserving `mapping.json` as
the runtime SSOT.

## Scope

- Core mapping cascade lookup for ODU Cond Specs.
- Predict dropdown base-vs-row-specific option coordination.
- Predict row edit autofill for Cond Area and Cond Volume.
- Missing/invalid mapping behavior tests.
- Arc 14C design note and Work Plan update.

## Non-goals

- Data Mapping CRUD changes.
- Import, CSV import/export contract, or XLSX export implementation.
- Predict Schema Catalog, Feature Catalog, fixture/golden, ML, model, or
  calculator changes.
- UI polish or report lifecycle cleanup.

## Slice Results

- 14C-0: OK - audited current runtime cascade path and documented schema/runtime
  section contract.
- 14C-1: OK - hardened Qt-free core lookup for ODU cascade options, base
  fin/pi/row options, direct composite `cond_specs` keys, missing sections, and
  invalid shapes.
- 14C-2: OK - integrated Predict row-specific dropdown state so calculated empty
  options do not silently fall back to base options after ODU selection.
- 14C-3: OK - added missing/invalid mapping coverage for missing files,
  missing ref/exp sections, missing/invalid ODU cascade, invalid cond specs, and
  invalid top-level mapping shape.
- 14C-4: OK - updated docs/report and prepared final focused validation.

## Design Contract

- `mapping.json` SSOT preserved: yes.
- `ref_type` / `exp_type` fallback remains removed: yes.
- ODU cascade uses `odu_cascade`: yes.
- Cond Area / Cond Volume autofill uses `cond_specs`: yes.
- `fin_type` / `pi` / `row` base options used before ODU selection: yes.
- Missing mapping fallback created: no.
- UI raw JSON parse/write: no.
- Import/XLSX export touched: no.
- Predict Schema Catalog changed: no.

## Architecture

- Core owns cascade lookup: yes, in `core/mapping/autofill.py`.
- Predict adapter/controller owns runtime coordination only: yes.
- UI remains display/input only: yes.
- Unrelated refactor: no.
- Schema/public API changed: no.
- Feature Catalog changed: no.
- ML/model/calculator changed: no.

## Verification

- 14C-0 `git diff --check`: OK.
- 14C-0 `git status --short`: expected docs changes only before commit.
- 14C-1 `python3 -m py_compile core/mapping/autofill.py`: OK.
- 14C-1 `python3 -m pytest tests/test_core_mapping_autofill.py -q`: OK,
  12 passed.
- 14C-1 `git diff --check`: OK.
- 14C-2 `python3 -m py_compile apps/predict/adapters/dropdown_option_adapter.py apps/predict/controllers/input_edit_controller.py`: OK.
- 14C-2 `python3 -m pytest tests/test_apps_predict_mapping_backed_dropdown.py -q`: OK,
  16 passed.
- 14C-2 `python3 -m pytest tests/test_apps_predict_mapping_controller.py -q`: OK,
  3 passed.
- 14C-2 `python3 -m pytest tests/test_core_mapping_autofill.py -q`: OK,
  12 passed.
- 14C-2 `git diff --check`: OK.
- 14C-3 `python3 -m py_compile core/mapping/autofill.py apps/predict/adapters/dropdown_option_adapter.py apps/predict/controllers/input_edit_controller.py`: OK.
- 14C-3 `python3 -m pytest tests/test_apps_predict_mapping_backed_dropdown.py tests/test_apps_predict_mapping_controller.py -q`: OK,
  23 passed.
- 14C-3 `python3 -m pytest tests/test_core_mapping_autofill.py -q`: OK,
  13 passed.
- 14C-3 `git diff --check`: OK.
- Final `python3 -m py_compile core/mapping/autofill.py apps/predict/adapters/dropdown_option_adapter.py apps/predict/controllers/input_edit_controller.py`: OK.
- Final `python3 -m pytest tests/test_core_mapping_autofill.py -q`: OK,
  13 passed.
- Final `python3 -m pytest tests/test_apps_predict_mapping_backed_dropdown.py -q`: OK,
  20 passed.
- Final `python3 -m pytest tests/test_apps_predict_mapping_controller.py -q`: OK,
  3 passed.
- Final affected Train Data Mapping tests: OK,
  `tests/test_apps_train_data_mapping_service.py`,
  `tests/test_apps_train_data_mapping_controller.py`, and
  `tests/test_apps_train_data_mapping_ui_models.py` passed, 31 tests.
- Final `git diff --check`: OK.
- Final `python3 tools/code_checker/build_reference_map.py --check`: OK,
  freshness FRESH with expected dirty-tree note before the 14C-4 commit.
- Final `python3 -B tools/check_code_structure.py`: OK with pre-existing
  calculator soft warnings and no changed-file structure warning.

## Changed Files

- `core/mapping/autofill.py`
- `apps/predict/adapters/dropdown_option_adapter.py`
- `apps/predict/controllers/input_edit_controller.py`
- `tests/test_core_mapping_autofill.py`
- `tests/test_apps_predict_mapping_backed_dropdown.py`
- `docs/designs/2026-07-05-arc14c-runtime-cascade-integration.md`
- `docs/designs/README.md`
- `docs/WORK_PLAN.md`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `result_reports/active/704_arc14c-runtime-cascade-integration.md`

## Known Failures / Risks

- Qt/programmatic visual smoke was not run; focused Qt-backed dropdown delegate
  tests covered the runtime option provider path.
- Affected Train Data Mapping tests are expected to be unaffected because Data
  Mapping CRUD/persistence code was not changed; final validation records
  whether a focused train suite was run.
- This checkout may still lack production `data/mapping.json`; tests use
  focused repositories/fixtures for runtime cascade behavior.

## Scope Compliance

- No Data Mapping CRUD, import, CSV import/export contract, or XLSX export
  implementation.
- No Predict Schema Catalog, Feature Catalog, fixture/golden, ML/model, or
  calculator changes.
- No report lifecycle cleanup or main merge work.

## Reference Parity

- Existing owners were reused: `core.mapping.autofill` for Qt-free policy,
  `DropdownOptionAdapter` for option resolution, and `InputEditController` for
  row edit side effects.
- No new source module was created because the existing owners already matched
  the required responsibility boundaries.

## Structure Warnings

- Changed source files remain below project soft limits.
- Structure guard reported existing calculator soft warnings for large
  calculator standard/section files and one batch controller class-count
  warning; none are in changed source files.
- Code map freshness warning was resolved by regenerating
  `docs/code_map/CODEBASE_REFERENCE_MAP.md`.

## Read Ledger

- `AGENT_TASK_ROUTER.md`: lines 124-260 and 296-345, reason: report, commit,
  coding, test, UI, and ML/Predictor route requirements.
- `docs/architecture/PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md`: lines 1-260,
  reason: owner boundary and new-source policy.
- `docs/agent_workflows/RESULT_REPORT_WORKFLOW.md`: lines 1-220, reason:
  report numbering, content, commit/push requirements.
- `docs/agent_workflows/AGENT_CHANGE_GATES.md`: lines 1-220, reason:
  change_gate and Read Ledger requirements.
- `docs/WORK_PLAN.md`: lines 1-220, reason: current Arc 14 context and next
  action update.
- `docs/designs/2026-07-05-arc14b5-data-mapping-ui-crud-workflow-design.md`:
  keyword ranges for mapping, ref/exp, ODU Cond Specs, and excluded runtime
  cascade scope.
- `result_reports/active/702_arc14b5-data-mapping-crud-implementation-bundle.md`:
  keyword ranges for Data Mapping CRUD and Predict dropdown fallback removal.
- `result_reports/active/703_arc14b5g-data-mapping-validation-reload-feedback-fixes.md`:
  keyword ranges for Arc 14B-5G closeout and next Arc 14C pointer.
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`: keyword ranges for mapping
  hotspots.
- `config/predict/schema.csv`: lines 1-24, reason: relevant Predict column,
  mapping target, and rule metadata.
- `core/mapping/autofill.py`: lines 1-260, reason: core cascade owner.
- `apps/predict/adapters/dropdown_option_adapter.py`: lines 1-260, reason:
  dropdown option owner.
- `apps/predict/controllers/input_edit_controller.py`: lines 1-320, reason:
  row edit side-effect owner.
- `apps/predict/mapping/mapping_repository.py`: lines 1-240, reason: mapping
  load/cache boundary.
- `apps/predict/schema/case_table_schema_adapter.py`: lines 1-260, reason:
  dropdown column metadata boundary.
- `apps/predict/ui/workspace.py`: lines 60-210 and 320-350, reason: UI wiring
  and status path confirmation.
- `core/mapping/repository.py`: lines 1-220, reason: missing/invalid mapping
  load behavior.
- `core/mapping/editor_projection.py`: lines 120-260, reason: generated ODU
  Cond Specs runtime sections.
- `core/mapping/editor_persistence.py`: lines 1-260, reason: saved runtime
  section shape.
- `tests/test_core_mapping_autofill.py`: lines 1-320, reason: focused core
  mapping tests.
- `tests/test_apps_predict_mapping_backed_dropdown.py`: lines 1-320, reason:
  Predict dropdown and Qt-backed provider tests.
- `tests/test_apps_predict_mapping_controller.py`: lines 1-320, reason:
  Predict input edit controller tests.

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

Code map judgment: regenerated after source changes; the regenerated map is
included in the 14C-4 docs/report commit.

## Commit / Push

- 14C-0: `0e6bbae1` docs: audit runtime mapping cascade integration.
- 14C-1: `bc53a515` fix: harden runtime mapping cascade lookup.
- 14C-2: `68ef7863` fix: integrate predict mapping cascade options.
- 14C-3: `9097ab8a` fix: surface missing runtime mapping cascade safely.
- 14C-4 report/docs commit and push result are recorded in the final terminal
  response to avoid a self-referential report hash loop.

## Next Suggested Action

Data Mapping XLSX read-only export snapshot.
