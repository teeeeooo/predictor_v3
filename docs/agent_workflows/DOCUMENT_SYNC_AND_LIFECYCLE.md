# Document Sync And Lifecycle Workflow

## Role

This document owns active-document sync, current-state document boundaries,
session handoff, and legacy-document movement.

## First Judgment

Use filenames, diff stat, changed-file type, and the user request to decide
whether any documentation sync is actually needed. Do not read or edit planning
documents merely because source changed.

## Active Document Inventory

Check `ACTIVE_DOCUMENTS.md` when:

- multiple active documents are affected;
- a new active owner/index/control document is created;
- an active document changes owner role or inbound/outbound relationships;
- an active document becomes legacy or is physically moved.

Design-record additions and lifecycle status changes also update
`docs/designs/README.md`.

## Document Boundaries

- `docs/WORK_PLAN.md`: current slice, next action, blockers, constraints, hold.
- `project_brief.md`: current Phase / Arc / Milestone map only.
- `docs/REFACTOR_PLAN.md`: refactor candidates and structural triggers.
- `project_log.md`: milestone decisions, durable failures, lessons.
- standard/dev notes: reusable specification interpretation, calculation
  rationale, and schema meaning.
- result records: durable change reason/evidence at one point in time.
- memory seed: compact active recall across workstreams.

Update only the document whose owned state changed.

## Result Record Lifecycle

New records are written directly to their final date-based path and indexed.
They do not move through active/summary/archive stages.

Existing `result_reports/active/` remains a legacy input at its historical path.
Existing archive and summary evidence is read-only under
`result_reports/legacy/archive/` and `result_reports/legacy/summaries/`.
Historical report/summary bodies remain unchanged.

Do not create cleanup reports, summaries, or memory deltas merely to manage a
report count.

## Session Handoff

Run only when the user explicitly requests a handoff, next-session plan, or
next-agent read pointer.

1. Check whether `project_brief.md` broad state is accurate.
2. Update `docs/WORK_PLAN.md` only where current execution state changed.
3. Create or fully replace one `Session Handoff` section.
4. Perform the Memory Review Gate.

Use:

- Status
- Updated
- Reason
- Read First
- Task-Specific Pointers
- Active Blocker / Open Decision
- Memory Review
- Next Action
- Do Not Read Unless Needed

Keep the combined read pointers to about 3-7 items. Include one Next Action.
Do not reconstruct completed report history or use legacy report bodies as
default first reads.

## Commit/Git Sync Status

When commit/push is requested, mention only sync judgments that matter to the
change. The universal final fields remain:

```text
modified:
validation:
commit:
push:
report:
```
