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

- `docs/WORK_PLAN.md`: update only when current priority, next action, phase,
  or execution order changes.
- `docs/REFACTOR_PLAN.md`: update only when refactor candidates, split
  strategy, or structural guardrails change.
- `project_brief.md`: update only when the new-session handoff state changes.
- standards/dev notes: update only for reusable specification interpretation,
  calculation rationale, or schema meaning.
- `docs/archive/`: report archive candidates; do not move/delete without
  user approval unless the task is lifecycle maintenance.

## project_log.md

Use `docs/agent_workflows/PROJECT_LOG_AND_MEMORY.md` for project log update
judgment and read limits.

## Output

For commit/git tasks, include a short documentation sync judgment:

- `project_log.md`: needed/not needed + reason
- `WORK_PLAN.md`: needed/not needed + reason
- `REFACTOR_PLAN.md`: needed/not needed + reason
- `project_brief.md`: needed/not needed + reason
- `ACTIVE_DOCUMENTS.md`: needed/not needed + reason
