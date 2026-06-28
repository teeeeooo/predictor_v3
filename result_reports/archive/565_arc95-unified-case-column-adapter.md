# 565 - Arc 9.5 Unified Case Column Adapter

## Goal

Add a Qt-free app-side display column schema adapter for the B-option unified
Predict case table without changing core schema, mapping schema, ML behavior,
or calculator contracts.

## Scope

- Add `UnifiedCaseColumn` metadata for unified table display columns.
- Preserve core input, auto-fill, and result column order through the existing
  Predict schema adapter.
- Add app-side virtual `status` and `message` columns.
- Add focused adapter tests.
- Update Work Plan next action to Slice 4.

## Non-goals

- No core schema changes.
- No split table removal or workspace switch.
- No mapping, ML, calculator, or visual polish changes.
- No push before Slice 11.

## Boundary Decision

Owner boundary: `apps/predict/schema/`.

The new adapter is an app-side display schema adapter. It wraps existing
`PredictColumn` metadata from `column_schema_adapter` and adds virtual
status/message display columns only. It does not import Qt, mapping
repositories, prediction services, training code, or calculators.

change_gate:
  new_source: small
  hotspot_delta: none
  code_map_check: skipped
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
  report_exemption: none
  read_ledger: included

Change gate notes:

- `code_map_check`: skipped because the prompt limits Slice 3 modifications to
  the adapter, focused tests, Work Plan, and report; code map regeneration is
  deferred to the final closeout if still needed.
- `reuse_commonization`: reused the existing schema owner
  `apps/predict/schema/column_schema_adapter.py` instead of duplicating core
  column metadata conversion.

Read Ledger:

- `apps/predict/schema/column_schema_adapter.py`: lines 1-108, reason: reuse
  existing Qt-free schema conversion and metadata fields.
- `core/predictor_schema/columns.py`: lines 1-107, reason: confirm core column
  groups/order and virtual status absence.
- `tests/test_apps_predict_schema_adapter.py`: lines 1-66, reason: mirror
  existing predict schema adapter test style.
- `docs/architecture/PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md`: lines 1-220,
  reason: new source owner boundary preflight.
- `docs/agent_workflows/DIFF_READ_BUDGET.md`: lines 1-220, reason: read-ledger
  and code-map judgment policy.
- broad read: none.
- repeated read: none.

## Verification

- `python3 -B -m py_compile apps/predict/schema/*.py`: passed.
- `python3 -B -m pytest tests/test_apps_predict_case_table_schema_adapter.py tests/test_apps_predict_schema_adapter.py`: passed, 12 tests.
- `python3 -B tools/check_code_structure.py`: passed with pre-existing
  calculator soft warnings plus code-map freshness reminder; no changed/new
  source file warning.
- `git diff --check`: passed.
- `git status --short`: checked; Slice 3 adapter, tests, Work Plan, and this
  report were dirty before commit.

Structure Warnings:

- none for changed/new source files.

## Known Risks

- The unified table model/view still need to consume this adapter in later
  slices.
- The flat focused test path is used because it is explicitly named by the
  slice prompt and matches existing Predict tests.

## Commit / Push

- Commit: pending.
- Push: not run; Slice 11 only.

## Next

Slice 4 - Unified Case Table Model.
