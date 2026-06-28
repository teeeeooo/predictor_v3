# 566 - Arc 9.5 Unified Case Table Model

## Goal

Add a unified `QAbstractTableModel` that exposes one visible row per prediction
case with input, auto-fill, result, and status columns in one table model.

## Scope

- Add `apps/predict/ui/tables/case_table_model.py`.
- Use the Slice 3 unified schema adapter.
- Read input/autofill values from `CaseRow` and result/status values from
  `ResultRow`.
- Permit edits only for input columns.
- Add focused model tests.
- Update Work Plan next action to Slice 5.

## Non-goals

- No workspace switch.
- No split table file deletion.
- No mapping repository, prediction service, training, ML, or calculator
  changes.
- No push before Slice 11.

## Boundary Decision

Owner boundary: `apps/predict/ui/tables/`.

The table model owns Qt model/view presentation roles only. Business side
effects stay outside the model: edit side effects are surfaced through an
optional callback, mapping/autofill remains controller-owned, and prediction
execution remains service/controller-owned.

change_gate:
  new_source: small
  hotspot_delta: none
  code_map_check: skipped
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
  report_exemption: none
  read_ledger: included

Change gate notes:

- `code_map_check`: skipped because the prompt limits Slice 4 modifications to
  the model, focused tests, Work Plan, and report; code-map regeneration is
  deferred to final closeout if still needed.
- `reuse_commonization`: reused current `InputTableModel` and `ResultTableModel`
  behavior patterns while replacing split final UX with the approved unified
  model target.

Read Ledger:

- `apps/predict/ui/tables/input_table_model.py`: lines 1-180, reason: reuse
  editability, invalid numeric rendering, and refresh behavior.
- `apps/predict/ui/tables/result_table_model.py`: lines 1-128, reason: reuse
  result/status rendering and case_id lookup behavior.
- `apps/predict/state/predict_session.py`: lines 1-67, reason: confirm
  case_order and result lookup API.
- `apps/predict/state/case_store.py`: lines 1-84, reason: confirm edit path and
  row lookup API.
- `apps/predict/state/case_row.py`: lines 1-20, reason: confirm input/autofill
  storage fields.
- `tests/test_apps_predict_table_models.py`: lines 1-93, reason: mirror current
  table model test patterns.
- broad read: none.
- repeated read: none.

## Verification

- `python3 -B -m py_compile apps/predict/ui/tables/*.py apps/predict/schema/*.py`: passed.
- `python3 -B -m pytest tests/test_apps_predict_case_table_model.py tests/test_apps_predict_case_table_schema_adapter.py`: passed, 13 tests.
- `python3 -B tools/check_code_structure.py`: passed with pre-existing
  calculator soft warnings plus code-map freshness reminder; no changed/new
  source file warning.
- `git diff --check`: passed.
- `git status --short`: checked; Slice 4 model, tests, Work Plan, and this
  report were dirty before commit.

Structure Warnings:

- none for changed/new source files.

## Known Risks

- Workspace still uses split models until Slice 5.
- Unified table copy/paste/navigation/undo behavior belongs to later view
  slices.

## Commit / Push

- Commit: pending.
- Push: not run; Slice 11 only.

## Next

Slice 5 - Unified Case Table View / Workspace Integration.
