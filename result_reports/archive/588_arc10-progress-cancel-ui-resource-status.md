# 588 - Arc 10 Progress / Cancel UI and Resource Status Cleanup

## Goal

Connect visible progress/cancel behavior in Predict UI and move model/mapping
resource status display away from widget-owned raw file checks.

## Scope

- Added a cancel button and running-state command disabling to
  `PredictCommandBar`.
- Wired `PredictWorkspace` to show progress, request cancellation, finish with
  complete/cancelled summary text, and disable row mutation commands while
  prediction is running.
- Added mapping resource status through `DropdownOptionAdapter`.
- Moved model status display through `PredictionController.model_status()`.
- Moved status text formatting to the existing `status_widgets.py` UI helper.
- Updated Data Mapping wording to `DropdownOptionAdapter / core mapping owner`.
- Added focused tests for progress/cancel state, resource-status ownership, and
  Data Mapping wording.
- Advanced `docs/WORK_PLAN.md` to Slice 6.

## Non-goals

- No Trainer execution foundation.
- No broad visual redesign.
- No ML behavior, mapping JSON schema, calculator, or model artifact changes.

## Verification

- `python3 -B -m py_compile apps/predict/**/*.py apps/train/ui/data_mapping_panel.py app_predict.py app_train.py`: OK.
- `python3 -B -m pytest tests -k "predict and (workspace or progress or worker or command or status)"`: OK, 53 passed and 1285 deselected.
- `python3 -B -m pytest tests/test_apps_train_shell.py`: OK, 7 passed.
- `python3 -B tools/check_code_structure.py`: OK with pre-existing calculator
  soft warnings and code-map freshness reminder; no changed/new source warning
  after moving status formatting out of `PredictWorkspace`.
- `python3 -B tools/code_checker/build_reference_map.py --check`: checked;
  stale by metadata from prior commits and not regenerated in this slice.
- `python3 -B tools/check_agent_change_gate.py --cached`: OK.
- `git diff --check`: OK.
- `git status --short`: checked before commit.

## Task Results

- task 1: OK - command bar now includes cancel, disables run/reset/add/delete/
  paste while running, and re-enables commands after finish.
- task 2: OK - workspace run path uses controller callbacks for progress and
  final complete/cancelled summaries.
- task 3: OK - workspace no longer imports `MODEL_FILE` or owns direct model
  artifact checks; mapping badge status comes through `DropdownOptionAdapter`.
- task 4: OK - Data Mapping wording reflects `DropdownOptionAdapter / core
  mapping owner`.
- task 5: OK - focused tests cover command state, progress/final text,
  resource ownership guard, mapping status, and Train Data Mapping wording.

## Read Ledger

- `apps/predict/ui/command_bar.py`: full file, reason: command-state owner.
- `apps/predict/ui/workspace.py`: full file, reason: progress/cancel run path
  and resource badge owner under active edit.
- `apps/predict/ui/status_widgets.py`: full file, reason: existing status UI
  helper reused for summary/badge text.
- `apps/predict/adapters/dropdown_option_adapter.py`: full file, reason:
  mapping resource status adapter owner.
- `apps/train/ui/data_mapping_panel.py`: full file, reason: wording cleanup.
- `tests/test_apps_predict_workspace_unified_table.py`: relevant workspace
  state tests, reason: focused progress/command assertions.
- `tests/test_apps_predict_mapping_backed_dropdown.py`: relevant adapter status
  tests, reason: mapping status boundary.
- `tests/test_apps_train_shell.py`: relevant Data Mapping text tests.
- broad read: none.
- repeated read: none.

## Change Gate

```yaml
change_gate:
  new_source: none
  hotspot_delta: none
  code_map_check: checked
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
  report_exemption: none
  read_ledger: included
```

- `reuse_commonization: reused-existing-owner` because status text moved into
  the existing Predict status widget owner instead of expanding workspace.

## Structure Warnings

- Initial Slice 5 work pushed `PredictWorkspace` over the 400 LOC soft warning.
  Moving status formatting into `status_widgets.py` brought it back under the
  guard threshold.
- Remaining structure warnings are pre-existing calculator soft warnings plus
  the code-map freshness reminder.

## Known Risks

- Direct table editing while a run is active is not fully locked; row mutation
  commands are disabled and guarded. Slice 6 will strengthen running-state and
  cancelled/partial behavior tests.
- Row-level cancelled presentation remains part of Slice 6 handling.
- Real-model success smoke remains blocked until `model/model.pkl` is present.

## Commit / Push

- Commit: this report is included in the Slice 5 commit.
- Push: deferred until Slice 7 per user request.

## Project Memory Delta

- none
