# Pre-Arc14 Numbering / Status Sync

## Goal

Align near-term project docs with the current implementation state before Arc
14 starts.

## Background

`app_train.py` now opens Predict, Train / Model, Data Mapping, and Feature
Catalog tabs. Feature Catalog Manager is complete after Arc 13.5A, but the Data
Mapping tab is still placeholder-like: mapping source selection is marked for a
follow-up arc and mapping update controls are disabled. The existing
`scripts/update_mapping.py` and `core.mapping.update` conversion logic is not
yet connected through the Train/Admin Data Mapping tab service/controller/adapter
boundary.

## Changes

- `docs/WORK_PLAN.md`: changed the next action to Arc 14 Data Mapping Manager /
  Mapping Update Execution and moved real dataset readiness audit to Arc 15.
- `project_brief.md`: updated current phase wording, added new Arc 14 Data
  Mapping Manager / Mapping Update Execution, and renumbered ML
  Catalog-Aligned Real Dataset Readiness Audit to Arc 15.
- `project_log.md`: recorded the Arc 14/15 renumbering decision.

## Excluded Scope

- No code changes.
- No Data Mapping implementation.
- No mapping conversion logic changes.
- No Feature Catalog changes.
- No test expected changes.
- No report lifecycle movement.

## Verification

- `git diff --check`: OK.
- `git status --short`: expected docs/report changes only.

## Next Action

- Arc 14 Data Mapping Manager design/foundation.

## Commit / Push

- commit: final hash reported in terminal output after push
- push: final status reported in terminal output after push
- local_head: final SHA reported in terminal output after push
- remote_main: final SHA reported in terminal output after push
- match: final match status reported in terminal output after push

## Project Memory Delta

- none
