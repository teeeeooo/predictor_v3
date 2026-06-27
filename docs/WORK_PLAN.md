# Work Plan

## Purpose

- Maintain the current slice, next action, active blockers/open decisions,
  active constraints, and deferred/hold items.
- Keep Phase / Arc / Milestone direction in `project_brief.md`.
- Keep long-term goals and Phase 1~5 direction in `PROJECT_CHARTER.md`.
- Keep completed work history in `project_log.md`, `result_reports/summaries/`,
  and `result_reports/archive/`.
- Keep refactor candidates and structural triggers in `docs/REFACTOR_PLAN.md`.

## Work Plan Update Rule

- `WORK_PLAN.md` is the near-term execution board, not a roadmap, task log, or
  report index.
- Update only when current slice, next action, execution order, active
  constraints, blockers/open decisions, or hold status changes.
- Do not append completed report lists, full report content, terminal output, or
  repeated next-action history.
- Arc and milestone status belong to `project_brief.md`; only reference them here
  when they directly constrain the current slice.
- Ordinary work plan maintenance does not create or update `Session Handoff`.
  That section exists only when the user explicitly requests a session or
  next-agent handoff, following
  `docs/agent_workflows/DOCUMENT_SYNC_AND_LIFECYCLE.md`.

## Current Slice

- Calculator lifecycle/detail/empty-state implementation and manual smoke
  closeout are complete.
- Canonical launch, empty batch inputs, and semantic EN14825 cell backgrounds
  are manually confirmed.
- The five approved legacy UI token cleanup slices are complete, with remaining
  values classified in the formal exception/exclusion ledger.
- The four structure audits and their approved helper implementation bundle are
  complete: UI literal sentinel hotfix, detail formatting coercion helper,
  batch matrix controller, batch dialog handle, and detail visibility helper.
- Calculator small cleanup and Hong Kong HSPF batch implementation are complete.
- Hong Kong HSPF batch visual smoke is manually confirmed: `일괄 입력`
  button, dialog open, 7 Full / 7 Half edits, HSPF/HSTL/HSEC result display,
  and close/reopen snapshot retention.
- Report lifecycle cleanup is complete; active reports now retain only the
  near-term implementation decision reports and unresolved design-gate evidence.
- Agent gate/workflow hardening now requires report-backed structural source
  changes to record reuse/commonization decisions and warns on Phase 2 UI
  presentation literal candidates.

## Next Actions

1. Run report lifecycle cleanup for completed calculator helper/batch/detail
   reports.
2. Select the next approved calculator detail/manual-smoke or empty-state slice
   after active reports are reduced.

## Active Blockers / Open Decisions

- No active implementation blocker is recorded.
- A future explicit DEV/demo sample loader remains optional and is not part of
  the production empty-state contract.

## Active Constraints

- Do not restore production performance prefills; focused tests own any samples
  needed for calculation and detail regression coverage.
- Preserve `app_calculator.py` → `apps.calculator.app:main` as the canonical
  calculator launch boundary.
- Preserve calculator, schema, config, fixture, golden, and public result
  contracts.
- Use focused verification rather than full pytest by default.

## Deferred / Hold

- AS/NZS Excel compatibility remains in the deferred Z-phase.
- ML / predictor continuation remains after calculator workflows and result
  boundaries are stable enough for the next approved slice.
- Internal formula trace and broad code-quality refactors remain on hold; their
  candidates belong in `docs/REFACTOR_PLAN.md`.

## Reference Anchors

- Active Arc / Milestone map: `project_brief.md`.
- Last closed EN14825 batch/workflow summary:
  `result_reports/summaries/416_summary-en14825-batch-agent-change-gate-closeout.md`.
- AHRI calculator and supporting UI/workflow closeout:
  `result_reports/summaries/445_summary-ahri-calculator-ui-batch-lifecycle-closeout.md`.
- UI literal legacy inventory and cleanup plan:
  `docs/designs/2026-06-21-ui-magic-literal-legacy-inventory.md`.
- Calculator sample/default inventory and empty-state policy:
  `docs/designs/2026-06-21-calculator-sample-data-empty-state-policy.md`.
- AHRI implementation contract:
  `docs/designs/2026-06-20-ahri-210-240-ui-batch-design-specification.md`.
- Milestone decisions and detailed completed history belong in `project_log.md`
  and the result-report lifecycle directories.
