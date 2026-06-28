# 578 Arc 9.5 Train Embedded Predict Header

## Goal

- Remove duplicated Predict title/top environment status when `PredictWorkspace`
  is embedded inside `TrainShell`, while preserving standalone `app_predict`.

## Scope

- Added explicit `PredictWorkspace` constructor options:
  `show_title` and `show_status_strip`.
- Updated `TrainShell` to embed `PredictWorkspace` with title/top status hidden.
- Added focused shell tests for standalone and embedded behavior.

## Non-goals

- No split into a new `PredictWorkspaceBody` class in this slice.
- No changes to prediction execution, mapping, table model, or Train execution.

## Verification

- `PYTHONPATH=. QT_QPA_PLATFORM=offscreen pytest -q tests/test_apps_train_shell.py` - OK, 6 passed.
- `python3 -B tools/check_code_structure.py` - OK with pre-existing unrelated soft warnings and code-map freshness reminder.
- `python3 -B tools/code_checker/build_reference_map.py --check` - STALE; not regenerated in this focused shell wiring slice.
- `git diff --check` - OK.

## Task Results

- `PredictShell` still creates the default standalone workspace with title and
  status strip.
- `TrainShell` now embeds the same `PredictWorkspace` with duplicated top title
  and environment status removed.
- Bottom Predict result/status remains visible because it belongs to the table
  workflow, not the Train shell header.

## Reference Parity / Change Gate

- The audit allowed explicit constructor options as the simpler correction.
- Reuse/commonization decision: no new body/surface split was introduced because
  the current duplication is solved by narrow display flags without adding a new
  reusable surface responsibility.
- `code_map_check`: checked; stale before this slice, not regenerated because
  the slice is narrow shell composition.

## Structure Warnings

- No changed/new source file emitted a LOC/class warning.
- Existing unrelated calculator and code-map freshness warnings remain.

## Changed Files

- `apps/predict/ui/workspace.py`
- `apps/train/ui/shell.py`
- `tests/test_apps_train_shell.py`

## Known Risks

- If Train later needs deeper Predict body composition, a dedicated
  `PredictWorkspaceBody` split may still be preferable.

## Commit / Push

- Commit: pending for this slice.
- Push: deferred per user request until all slices complete.

## Project Memory Delta

- none
