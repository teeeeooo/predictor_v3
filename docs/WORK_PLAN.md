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

- AHRI HSPF2 batch, pending explicit implementation approval.
- The SEER2 main/batch and HSPF2 main/polish are complete; HSPF2 batch remains
  a separate slice under the approved AHRI UI/Batch design contract.

## Next Actions

1. Implement AHRI HSPF2 batch as a separately approved slice.

## Active Blockers / Open Decisions

- No active blocker is recorded.
- No AHRI main/batch layout or optional-point design decision remains open for
  the approved implementation slices.

## Active Constraints

- Follow
  `docs/designs/2026-06-20-ahri-210-240-ui-batch-design-specification.md`.
- Keep the next slice to HSPF2 batch only.
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
- EN14825 lifecycle closeout evidence:
  `result_reports/active/424_close-en14825-calculator-lifecycle.md`.
- AHRI implementation contract:
  `docs/designs/2026-06-20-ahri-210-240-ui-batch-design-specification.md`.
- Milestone decisions and detailed completed history belong in `project_log.md`
  and the result-report lifecycle directories.
