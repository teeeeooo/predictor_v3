# Document Sync And Lifecycle Workflow

## Role

This document owns documentation sync judgment, lifecycle decisions, and
active document inventory maintenance.

`AGENT_TASK_ROUTER.md` should only route to this workflow.

## First Judgment

Before reading docs, judge from filenames, diff stat, changed-file type, and
user request:

- whether docs sync is required;
- whether `project_log.md` may need an update;
- whether `docs/WORK_PLAN.md`, `docs/REFACTOR_PLAN.md`, or
  `project_brief.md` may need a change.

If ambiguous, do not read or edit the docs automatically. Report
`documentation update may be needed` or `project_log update recommended`.

## ACTIVE_DOCUMENTS.md

Check `ACTIVE_DOCUMENTS.md` when:

- the user requests documentation updates;
- multiple docs are affected;
- a new active document is created;
- an active document owner role or inbound/outbound relationship changes.

Design record additions or lifecycle changes update `docs/designs/README.md`,
not individual rows in `ACTIVE_DOCUMENTS.md`.

## Document-specific Rules

- `docs/WORK_PLAN.md`: update only when current slice, next action, active
  blockers/open decisions, execution order, active constraints, or hold status
  changes.
- `docs/REFACTOR_PLAN.md`: update only when refactor candidates, split
  strategy, or structural guardrails change.
- `project_brief.md`: update only when Phase / Arc / Milestone position or broad
  project-state map changes.
- standards/dev notes: update only for reusable specification interpretation,
  calculation rationale, or schema meaning.
- `docs/archive/`: report archive candidates; do not move/delete without
  user approval unless the task is lifecycle maintenance.

## project_log.md

Use `docs/agent_workflows/PROJECT_LOG_AND_MEMORY.md` for project log update
judgment and read limits.

## Session Handoff Workflow

Run this workflow only when the user explicitly requests a handoff,
next-session handover, context handoff, or next-agent read plan.

Ordinary `WORK_PLAN.md` maintenance, routine result-report closeout, and small
bugfix or micro-task completion do not create or update a handoff.

When triggered:

1. Check `project_brief.md` for Phase / Arc / Milestone accuracy and update it
   only when the broad project-state map is stale.
2. Update the normal execution-board sections in `docs/WORK_PLAN.md` when the
   current slice, next action, blockers/open decisions, constraints, or hold
   status changed.
3. Create or fully replace the `Session Handoff` section in
   `docs/WORK_PLAN.md`; never append a new handoff to an old one.

Ownership remains split:

- `project_brief.md`: Phase / Arc / Milestone map and broad project-state
  orientation;
- `docs/WORK_PLAN.md`: current slice, next action, blockers/open decisions,
  constraints, hold items, and temporary handoff pointers;
- `project_log.md`: completed milestone decisions, durable failures, and
  lessons;
- `result_reports/summaries/`: completed report-group summaries and evidence
  anchors.

If an existing handoff conflicts with current state after ordinary work, do
not silently refresh it. Remove it or mark it stale. A fresh handoff requires
an explicit user trigger.

Use this compact `Session Handoff` shape:

- Status
- Updated
- Reason
- Read First
- Task-Specific Pointers
- Active Blocker / Open Decision
- Next Action
- Do Not Read Unless Needed

Keep the combined Read First and task-specific pointer set to about 3-7 items.
Each pointer includes a one-line Why and, where possible, a file plus heading,
function, or report pointer. Do not put archive/report originals in Read First
by default. Include exactly one Next Action and do not reproduce completed
report history.

Do not place task-specific code pointers, focused test pointers, or next-session
read lists in `project_brief.md`. Those belong in `docs/WORK_PLAN.md` under the
explicitly requested `Session Handoff` section.

## Output

For commit/git tasks, include a short documentation sync judgment:

- `project_log.md`: needed/not needed + reason
- `WORK_PLAN.md`: needed/not needed + reason
- `REFACTOR_PLAN.md`: needed/not needed + reason
- `project_brief.md`: needed/not needed + reason
- `ACTIVE_DOCUMENTS.md`: needed/not needed + reason
