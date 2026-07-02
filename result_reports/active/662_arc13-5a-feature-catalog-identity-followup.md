# Arc 13.5A Slice 0 Follow-up - ml_name Identity Validation

## Goal

Close the Slice 0 audit follow-up by enforcing non-empty `ml_name` at core validation and syncing Feature Catalog docs to the post-`feature_id` contract.

## Scope

- Added core validation error for blank `ml_name` on every catalog row, including inactive rows.
- Added focused coverage for a blank inactive `ml_name` row.
- Removed stale `feature_id` guidance from the ML Feature Catalog workflow.
- Updated the correction design recommended next action to Arc 13.5A Slice 1 UX foundation.

## Changed Files

- `core/ml/feature_catalog_validation.py`
- `tests/test_ml_feature_catalog.py`
- `docs/workflows/ml_feature_catalog_workflow.md`
- `docs/designs/2026-07-02-arc13-5a-feature-catalog-manager-correction-design.md`

## Verification

- `python3 -m compileall core apps tests` - OK
- `python3 -m pytest tests/test_ml_feature_catalog.py` - OK, 40 passed
- `git diff --check` - OK
- `python3 -B tools/check_code_structure.py` - NG, pre-existing unrelated raw hex literal:
  - `apps/calculator/ui/calculator_app.py:105`
  - The same `#202020` literal is present in `HEAD`, so this follow-up did not introduce it.

## Excluded

- No Feature Manager UX implementation.
- No user-friendly header, dropdown, or help implementation.
- No add/delete/duplicate feature row implementation.
- No schema refresh, live table refresh, or model artifact catalog hash work.
- No report lifecycle movement.

## Docs Sync Judgment

- `ACTIVE_DOCUMENTS.md`: not needed; no active document owner or lifecycle relationship changed.
- `project_log.md`: not needed; this is a narrow follow-up, with evidence captured in this report.
- `docs/WORK_PLAN.md`, `docs/REFACTOR_PLAN.md`, `project_brief.md`: not needed; next action was updated in the owner design document.

## Change Gate

```yaml
change_gate:
  new_source: none
  hotspot_delta: none
  code_map_check: not_required
  ui_literal_exemption: none
  reuse_commonization: not_required
  report_exemption: none
  read_ledger: included
```

## Commit / Push

This report is committed with the implementation. Final pushed SHA and remote match are reported in terminal output to avoid a self-referential report update loop.

## Next

Arc 13.5A Slice 1 UX foundation.
