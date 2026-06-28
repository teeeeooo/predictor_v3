# 590 - Arc 10 Prediction Worker Progress Closeout

## Goal

Close Arc 10 Prediction Worker / Progress after confirming the implemented
worker, progress, cancel, resource-status, and partial-result boundaries.

## Scope

- Confirmed prediction execution runs through worker/progress/cancel boundaries.
- Confirmed invalid rows, model-missing errors, partial success/error, and
  cancellation have controlled row-level outcomes.
- Confirmed Predict model/mapping resource status no longer depends on direct
  workspace file checks.
- Updated project state docs for Arc 10 implementation closeout and next manual
  smoke action.
- Regenerated the codebase reference map after Arc 10 source changes.

## Modified Files

- `docs/WORK_PLAN.md`
- `project_brief.md`
- `project_log.md`
- `result_reports/memory/project_memory_seed.md`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `result_reports/active/590_arc10-prediction-worker-progress-closeout.md`

## Validation Results

- `python3 -B -m py_compile apps/predict/**/*.py apps/train/**/*.py apps/common/**/*.py ui_common/*.py app_predict.py app_train.py app_calculator.py`: OK.
- `python3 -B -m pytest tests -k "predict or train or visual or table or mapping or schema or worker or progress"`: OK, 516 passed and 825 deselected.
- `python3 -B tools/check_code_structure.py`: OK with pre-existing calculator
  soft warnings only.
- `python3 -B tools/code_checker/build_reference_map.py`: OK, reference map
  regenerated.
- `python3 -B tools/code_checker/build_reference_map.py --check`: OK, fresh.
- `git diff --check`: OK.
- `git status --short`: checked before closeout commit.

## Acceptance Checklist

- Prediction execution runs through the worker/progress boundary: OK.
- UI run path is non-blocking by design through `QThread` worker ownership: OK.
- Cancel is available and cooperative: OK.
- Row-level result updates work: OK.
- Invalid rows do not go to the worker: OK.
- Model missing produces controlled row-level errors: OK.
- Partial complete/error/cancel states are stable: OK.
- `PredictWorkspace` no longer owns direct model file existence checks: OK.
- Data Mapping wording reflects adapter/core mapping owner: OK.
- Arc 9.5 unified table behavior has focused non-regression coverage: OK.
- `app_train.py` still reuses Predict workspace and does not implement Trainer
  execution: OK.

## Known Risks

- Manual GUI smoke has not yet been run after Slice 7.
- Real-model success smoke remains blocked in this checkout because
  `model/model.pkl` is absent.
- Structure guard still reports pre-existing calculator soft warnings unrelated
  to Arc 10 changes.

## Manual Smoke Needed

- Run the Arc 10 manual smoke checklist for `app_predict` and `app_train`.
- Repeat real-model prediction success smoke when a valid model artifact is
  available.

## Excluded Scope

- No Arc 11 Trainer execution foundation was implemented.
- No ML algorithm, feature schema, model artifact, mapping JSON schema,
  calculator, or unified table contract changes were made.
- No broad report lifecycle cleanup was performed.

## Next Action

- Arc 10 manual smoke.

## Read Ledger

- `arc10_lifecycle_worker_prompt_pack.md`: full file, reason: task owner prompt
  and slice instructions.
- `AGENTS.md`: provided in prompt, reason: project work contract.
- `AGENT_TASK_ROUTER.md`: relevant Coding, Commit/Git, Result Report, and
  project memory routing, reason: required closeout workflow.
- `docs/agent_workflows/RESULT_REPORT_WORKFLOW.md`: relevant report and
  commit/push rules.
- `docs/WORK_PLAN.md`, `project_brief.md`, `project_log.md`: relevant active
  state sections, reason: closeout sync.
- `result_reports/memory/project_memory_seed.md`: relevant recent durable
  decision section, reason: compact Arc 10 memory delta.
- Arc 10 active reports 583-589: focused status and verification history.
- broad read: none beyond the user-required prompt pack.

## Change Gate

```yaml
change_gate:
  new_source: none
  hotspot_delta: none
  code_map_check: regenerated
  ui_literal_exemption: none
  reuse_commonization: not_required
  report_exemption: none
  read_ledger: included
```

- `code_map_check: regenerated` because
  `docs/code_map/CODEBASE_REFERENCE_MAP.md` is included in this closeout diff.
- `reuse_commonization: not_required` because this slice changes documentation,
  report, memory seed, and generated code-map state only.

## Push Result

- Push is performed after the closeout commit per Slice 7 instructions.
- Final `local_head`, `remote_main`, and match status are reported in the
  terminal response to avoid a self-referential report update loop.
