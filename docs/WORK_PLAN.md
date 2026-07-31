# Work Plan

## Purpose

- Own the current slice, one next action, blockers, constraints, and deferred work.
- Keep phase, owner, and milestone direction in `project_brief.md`.
- Keep durable history in `project_log.md` and its archives; keep conditional
  evidence in records.

## Update Rule

- This file is a near-term execution board, not a roadmap or task log.
- Update it only when the current slice, next action, blocker, constraint, or
  hold state changes.
- Do not repeat completed audit, validation, repair, or merge history.

## Current Baseline

- Train/Admin Phase 5 is complete and merged.
- Predict Findings #1–#7 are complete and merged.
- The active product workstream is **Predict input workflow broad overhaul**.
- The current step records confirmed product direction and the disposable mock
  evaluation baseline. Final layout and context presentation remain open.
- No prototype or production source implementation has started.

## Next Action

The next owner is the Orchestrator, which must:

1. prepare and run a disposable PySide6 comparison of the open layout candidates
   under `/tmp`;
2. present common-fixture evidence for the user's layout, context, and Result
   Review reveal decision;
3. fix the implementation boundary and owner gaps; and
4. prepare a Lane C Build handoff before production source implementation.

## Active Blockers

- Final layout, Compact versus Full Context behavior, preference persistence,
  and Result Review reveal behavior are blocked on comparable standalone and
  embedded mock evidence.
- The public case-table workflow crosses shared workspace, schema/mapping,
  calculation, execution, result, status, and viewport owners; it cannot enter
  production source implementation without the user decision, explicit Lane C
  boundary, and acceptance.
- A model-incompatible saved Definition generation continues to block Predict
  with Retraining required until compatibility is proven; the overhaul does not
  auto-replace or auto-promote a model.

## Active Constraints

- Preserve completed Findings #1–#7 and existing prediction execution, row
  isolation, cancellation, and partial-result behavior.
- Preserve model lifecycle, reload, Active observation, no-hot-swap, schema,
  mapping, preprocessing, runtime snapshot, and inference contracts.
- Preserve Data Definition, Data Mapping, Train, Predict, and Calculator owner
  directions. Predict remains a consumer of saved contracts, mapping values, and
  a compatible loaded model.
- Standalone and embedded Predict must continue to use shared workspace behavior.
- Keep root-level horizontal scrolling prohibited; evaluate table-owned internal
  scrolling, frozen identity candidates, and responsive viewport behavior during
  the audit.
- Use repository fixtures or mock data only. Do not infer production readiness or
  mutate production data or models.

## Deferred / Hold

- Result graph or Advanced surface, export redesign, Train navigation, lifecycle
  wording redesign, model training workflow, ML feature/schema changes,
  calculator formula changes, and packaging/deployment require separate approval
  or follow-up workstreams.
- Production confirmation/promotion, migration apply, and retention/delete apply
  remain separately authorized controlled operations.
- Real mapping values, training data, model quality, and production-readiness
  validation remain company-local.
- Windows native Feature Manager smoke and deferred Phase 2 native interaction
  acceptance remain separate verification items and do not define this overhaul.

## Minimal Anchors

- Authoritative product exploration and mock baseline:
  `docs/designs/2026-07-14-future-predict-ui-ux-overhaul-boundary.md`
- Product and owner map: `project_brief.md`
- UI/UX owner root: `docs/ui_ux/00_UI_UX_SYSTEM.md`
- Spreadsheet behavior: `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md`
- Input/result roles: `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md`
- Viewport policy: `docs/ui_ux/07_WINDOW_GEOMETRY_AND_VIEWPORT_POLICY.md`
