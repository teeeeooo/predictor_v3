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

- EN14825 calculator smoke / lifecycle closeout after SCOP batch parent wiring.
- Confirm the completed SEER/SCOP batch access and cleanup path without
  reopening calculator or data contracts.

## Next Actions

1. Run the focused EN14825 calculator smoke / lifecycle closeout.

## Active Blockers / Open Decisions

- No active blocker is recorded.
- No schema, calculator, region-config, fixture, golden, result-contract, or
  SCOP profile-state ownership decision is open for this slice.

## Active Constraints

- SCOP dynamic rebuild/snapshot state remains profile-local.
- Preserve current calculator, schema, region-config, fixture, golden, and result
  behavior unless a separate approved task changes them.
- Use focused verification rather than full pytest by default.
- Run the cached agent change gate for structure-impacting source work.

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
- Current product evidence:
  `result_reports/active/422_wire-en14825-scop-batch-parent-section.md`.
- Handoff creation report:
  `result_reports/active/419_next_session_scop_batch_parent_wiring_handoff.md`.
- Milestone decisions and detailed completed history belong in `project_log.md`
  and the result-report lifecycle directories.

## Session Handoff

### Status

Ready for the next implementation session.

### Updated

2026-06-20.

### Reason

User-requested session handoff after closing the EN14825 batch foundation and
hardening the manually invoked cached agent change gate.

### Read First

- `AGENTS.md` - apply the repository work contract and routing rules before
  task-specific reads.
- `project_brief.md` - confirm current Phase, active Arc, and Milestone position;
  do not use it for task-specific code pointers.
- `AGENT_TASK_ROUTER.md` sections for Coding Work, UI Modification, and Result
  Report Workflow - load only the rules needed for this wiring slice.

### Task-Specific Pointers

- `result_reports/summaries/416_summary-en14825-batch-agent-change-gate-closeout.md`
  sections `Closed Results` and `Next Actions` - accepted SCOP batch ownership
  and the boundary left for parent wiring.
- `apps/calculator/ui/sections/en14825_scop_section.py`, class
  `En14825ScopSection` - target parent section; use `en14825_seer_section.py`
  methods `_open_batch_dialog()` and `_clear_batch_dialog()` as the established
  thin lifecycle/snapshot reference.
- `apps/calculator/ui/batch_dialogs/profiles/en14825_scop_dialog.py` and
  `apps/calculator/ui/batch_dialogs/profiles/en14825_scop.py` - existing dialog
  wrapper and profile-local dynamic rebuild/snapshot implementation to reuse
  unchanged where possible.
- `tests/test_apps_calculator_ui_en14825_batch.py` - focused batch contract tests;
  add parent/dialog lifecycle coverage without broad test reorganization.

### Active Blocker / Open Decision

None. Do not reopen schema, calculator, region-config, fixture, golden,
result-contract, or SCOP profile-state ownership decisions for the thin
parent-section wiring slice.

### Next Action

Wire the EN14825 SCOP batch dialog into `En14825ScopSection` as a thin dialog
lifecycle and snapshot-handoff slice.

### Do Not Read Unless Needed

- Archived reports 405-415; Summary 416 is their compact replacement.
- `core/`, region config, golden/fixture files, and broad test suites; the next
  slice does not change calculation or data contracts.
- Full workflow documents outside the routed Coding/UI/Result Report sections.
