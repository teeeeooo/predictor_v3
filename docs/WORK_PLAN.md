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

- ISO16358, EN14825, and AHRI210240 lifecycle assembly has been audited against
  the active window/profile policy.
- Shared measurement, scheduler, shell, and geometry primitives are sound, but
  their repeated profile-local construction is recorded as structural debt.
- Evidence-based nested activation and settle-cycle differences remain valid
  controller configuration inputs rather than profile-local owner machinery.

## Next Actions

1. Finalize the common profile visible-content lifecycle controller design.
2. Implement the controller foundation and migrate EN14825.

## Active Blockers / Open Decisions

- No active implementation blocker is recorded; task 2 must freeze the common
  controller contract before production migration begins.
- HSPF2 DEV sample values remain isolated and intentionally retained until the
  remaining EN14825/AHRI detail-view prerequisites are implemented.

## Active Constraints

- Do not remove calculator sample/default data during detail-view slices.
- Keep AHRI detail implementations separate from EN14825 detail behavior.
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
