# Document Sync And Lifecycle Workflow

## Role

This document owns active owner-map sync, current-state document boundaries,
session handoff, and legacy-document movement.

## First Judgment

Use filenames, diff stat, changed-file type, and the user request to decide
whether any documentation sync is actually needed. Do not read or edit planning
documents merely because source changed.

## Active Owner Map

Check `ACTIVE_DOCUMENTS.md` when:

- a top-level owner, root, index, or control document is created or retired;
- one of those documents changes responsibility or is physically moved.

Do not update the map for every active child document or ordinary multi-document wording change. Discover children through the nearest owner README, index, repository-local Skill, or owner document, and use filesystem search when completeness matters.

Update the matching design index when a new root active design is created, an
active decision is absorbed into an owner, an active record moves to legacy,
or a legacy record is explicitly re-promoted.

## Document Boundaries

- `docs/WORK_PLAN.md`: current slice, next action, blockers, constraints, hold.
- `project_brief.md`: current Phase / Arc / Milestone map only.
- `docs/REFACTOR_PLAN.md`: refactor candidates and structural triggers.
- `project_log.md`: milestone decisions, durable failures/lessons, process rules.
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

## Git And Final-State Sync

When commit/push is in scope, synchronize only documents whose owned state actually changed. Final reporting follows `AGENTS.md`: state material document-sync changes, verification, remaining blockers, and the requested Git action/result. This lifecycle owner does not create a separate Git or reporting ceremony.
