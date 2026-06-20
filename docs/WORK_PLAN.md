# Work Plan

## Purpose

- Maintain the current focus, next action, active blockers/open decisions,
  active constraints, and deferred/hold items.
- Keep completed work history in `project_log.md`,
  `result_reports/summaries/`, and `result_reports/archive/`.
- Keep long-term goals and Phase 1~5 direction in `PROJECT_CHARTER.md`.
- Keep refactor candidates and structural triggers in `docs/REFACTOR_PLAN.md`.

## Work Plan Update Rule

- `WORK_PLAN.md` is the current execution board, not a task or report index.
- Replace closed-arc checkpoints with at most a compact reference anchor.
- Update only when current focus, execution order, active constraints,
  blockers/open decisions, or hold status changes.
- Do not append completed report lists, full report content, terminal output, or
  repeated next-action history.
- Ordinary work plan maintenance does not create or update `Session Handoff`.
  That section exists only when the user explicitly requests a session or
  next-agent handoff, following
  `docs/agent_workflows/DOCUMENT_SYNC_AND_LIFECYCLE.md`.

## Current Focus

- Product arc: expose the implemented EN14825 SCOP batch profile through its
  parent section without moving profile-local rebuild/snapshot ownership.
- Workflow follow-up: the cached agent change gate is hardened and remains
  manually invoked until hook integration is handled as a separate slice.

## Next Actions

1. Wire the EN14825 SCOP batch dialog into its parent section as a thin
   lifecycle slice.

## Active Blockers / Open Decisions

- No active blocker is recorded.
- No schema, calculator, region-config, or result-contract decision is open for
  the parent-section wiring slice.

## Active Constraints

- Keep SCOP dynamic rebuild/snapshot state profile-local; the parent section
  owns only dialog lifecycle and snapshot handoff.
- Preserve current calculator, schema, region-config, fixture, and golden
  behavior unless a separate approved task changes them.
- Apply the Design First Gate if the slice expands beyond thin lifecycle
  wiring, and use focused verification rather than full pytest by default.
- Run the cached agent change gate manually for structure-impacting source work
  until hook integration is complete.

## Deferred / Hold

- Pre-commit and commit-msg hook integration for the cached agent change gate
  is a separate workflow follow-up.
- AS/NZS Excel compatibility remains in the deferred Z-phase.
- ML / inverse-search continuation remains after the calculator result-envelope
  and adapter boundary is ready for the next approved slice.
- Internal formula trace and broad code-quality refactors remain on hold; their
  candidates belong in `docs/REFACTOR_PLAN.md`.

## Reference Anchors

- Last closed arc:
  `result_reports/summaries/416_summary-en14825-batch-agent-change-gate-closeout.md`.
- Current workflow evidence:
  `result_reports/active/417_agent_change_gate_manifest_index_hardening.md`.
- Milestone decisions and detailed completed history belong in
  `project_log.md` and the result-report lifecycle directories.
