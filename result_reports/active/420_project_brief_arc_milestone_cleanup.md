# 420 Project Brief Arc and Milestone Cleanup

## Goal

Separate Phase / Arc / Milestone orientation from current-slice execution and
explicit Session Handoff pointers.

## Scope

- Replaced `project_brief.md` and `docs/WORK_PLAN.md` with the approved package
  replacements after confirming `main` matched the handoff 419 state.
- Patched only the affected workflow, owner-map, charter, router, and project-log
  role statements.
- Preserved the existing explicit Session Handoff and its single implementation
  target while removing the duplicated brief-level handoff entry.
- Did not change source, tests, schemas, fixtures, golden expectations, region
  configs, report lifecycle state, or historical log entries.

## Changed Files

- `project_brief.md`
- `docs/WORK_PLAN.md`
- `docs/agent_workflows/DOCUMENT_SYNC_AND_LIFECYCLE.md`
- `ACTIVE_DOCUMENTS.md`
- `PROJECT_CHARTER.md`
- `AGENT_TASK_ROUTER.md`
- `project_log.md`
- `result_reports/active/420_project_brief_arc_milestone_cleanup.md`

## Verification

- `git diff --check`: passed.
- Package comparison: both replacements matched the supplied deployment files.
- Stale `Next Session Entry` and section-4 pointer checks: none found.
- Active-startup naming check: no `AGENTS_FULL`, `OPTIMO`, or `AeroMatch` found.
- Action structure: exactly one normal Next Action and one Session Handoff Next
  Action.
- Changed-path audit: no code, test, schema, fixture, golden, or region-config
  files changed.

## Known Risks

- Arc 2 AHRI milestones remain candidates pending a future readiness audit.
- The preserved Session Handoff becomes stale after the SCOP parent-section
  wiring slice lands and must then be removed or replaced under the workflow.

## Next Action

Wire the EN14825 SCOP batch dialog into `En14825ScopSection` as a thin dialog
lifecycle and snapshot-handoff slice.

## Commit / Push

- Documentation commit: `0ad9be0` (`Separate project map from session handoff`).
- The report commit hash and final push result are reported in terminal output
  to avoid a self-referential report update loop.
