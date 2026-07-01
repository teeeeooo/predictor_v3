# 635 Planning Doc Sync - Arc 13.5 Feature Catalog Editor

## Goal

Sync active planning documents to reflect the current execution order:
Calculator Sub-Arc - KOREA Notebook Entry first, then Arc 13.5 Feature Catalog
Editor work, then Arc 14 real dataset readiness audit.

## Scope

- Updated the near-term execution board.
- Updated the compact Arc/Milestone map.
- Added a milestone decision log entry.
- Added the Arc 13.5 Feature Catalog Editor design gate.
- Registered the new design gate in the design records index.

## Changed Files

- `docs/WORK_PLAN.md`
- `project_brief.md`
- `project_log.md`
- `docs/designs/2026-07-01-arc13-5-feature-catalog-editor-design-gate.md`
- `docs/designs/README.md`
- `result_reports/active/635_planning-doc-sync-arc13-5-feature-catalog-editor.md`

## Reflected Decisions

- Arc 13 remains complete for automated feature catalog scope.
- Arc 14 is not the immediate next action.
- Calculator Sub-Arc - KOREA Notebook Entry is the next action before Arc 13.5.
- Arc 13.5 is a bridge arc for an `app_train.py` Feature Catalog
  viewer/editor workflow.
- `config/ml/features.csv` remains the storage and contract file.
- Direct CSV editing is no longer the default user workflow.
- CSV export remains useful for storage, sharing, and Excel/Numbers review.
- Excel Korean label corruption is treated as a UTF-8 CSV auto-detection issue;
  Arc 13.5 should evaluate export encoding policy such as UTF-8-SIG.
- Train UI catalog work should route through controller/service/usecase and
  catalog loader/validator/writer boundaries rather than direct UI CSV
  parsing/writing.

## Excluded Scope

- No code implementation.
- No `config/ml/features.csv` changes.
- No `docs/workflows/ml_feature_catalog_workflow.md` changes.
- No `config/ml/README.md` creation.
- No Calculator KOREA notebook implementation.
- No Arc 13.5 UI implementation.
- No report lifecycle cleanup.
- No generated artifact commit.

## Verification

- `python3 -B tools/code_checker/build_reference_map.py --check`: STALE. Not
  regenerated because this task changed only planning/design/report docs and did
  not affect source structure inventory.
- `git diff --check`: OK.
- `git status --short`: OK, expected docs/report changes only before commit.

## Known Risks

- Arc 13.5 still needs implementation-slice decisions for tab/panel placement,
  export encoding, validation display, and save blocking behavior.
- Real-model prediction smoke remains blocked by absent production model
  artifact in this checkout.

## Next Action

Calculator Sub-Arc - KOREA Notebook Entry.

## Commit / Push

Final commit hash and push status are reported in the terminal response to avoid
a self-referential report update loop.
