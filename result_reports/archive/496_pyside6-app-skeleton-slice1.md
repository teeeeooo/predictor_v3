# 496 PySide6 App Skeleton Slice 1

## Goal

Create the first minimal package skeleton for the PySide6 Train/Predict rewrite
without switching root entrypoints or implementing executable UI behavior.

## Scope

- Added `apps/predict/` and `apps/train/` package boundaries.
- Added minimal `main()` and `create_shell()` bootstrap functions.
- Added placeholder `PredictWorkspace`, `PredictShell`, and `TrainShell`.
- Kept root `app_predict.py` and `app_train.py` unchanged for this slice.

## Changed Files

- `apps/predict/__init__.py`
- `apps/predict/app.py`
- `apps/predict/ui/__init__.py`
- `apps/predict/ui/shell.py`
- `apps/predict/ui/workspace.py`
- `apps/train/__init__.py`
- `apps/train/app.py`
- `apps/train/ui/__init__.py`
- `apps/train/ui/shell.py`
- `result_reports/active/496_pyside6-app-skeleton-slice1.md`

## Verification

- `python3 -B -m py_compile apps/predict/app.py apps/predict/ui/shell.py apps/predict/ui/workspace.py apps/train/app.py apps/train/ui/shell.py` - passed.
- `git diff --check` - passed.
- `git status --short` - checked.
- Cached change gate - passed after adding the required source-structure
  report block.

Skipped:

- pytest: package skeleton only.
- GUI smoke: shell execution is intentionally deferred to a later slice.
- PySide6 import smoke: not required for this slice; local PySide6 was installed
  after the initial dependency check for later slice validation.

## Change Gate

```yaml
change_gate:
  new_source: small
  hotspot_delta: none
  code_map_check: checked
  ui_literal_exemption: none
  reuse_commonization: checked
  report_exemption: none
  read_ledger: included
```

Read Ledger:

- `docs/architecture/pyside6_train_predict_architecture.md`: package skeleton
  and entrypoint boundary ranges.
- `app_predict.py`, `app_train.py`: legacy entrypoint state before Slice 2.
- `docs/agent_workflows/AGENT_CHANGE_GATES.md` and gate tool schema: structured
  change-gate enum requirements after initial cached gate failure.

Structure / code map judgment:

- `python3 -B tools/check_code_structure.py` was checked. Warnings were
  pre-existing calculator soft-limit/code-map freshness warnings outside this
  slice.
- No common shell abstraction was added; the architecture contract keeps
  Predict and Train shells separate at this stage.

## Known Risks

- `main()` intentionally raises until a later slice wires an executable PySide6
  shell.
- No Predict table, result table, prediction, training, or mapping behavior was
  implemented.

## Commit / Push

Commit is performed for this slice. Push is not required for this Arc unless
explicitly requested.
