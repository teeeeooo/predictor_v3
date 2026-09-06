# Document Sync And Lifecycle Workflow

## Role

Own active owner-map synchronization, current-state document boundaries, explicit session handoff, and historical-document movement.

## First judgment

Use the request, changed-file type, and diff scope to decide whether documentation sync is needed. Do not read or edit planning documents merely because source changed.

## Active Owner Map

Check `ACTIVE_DOCUMENTS.md` when a top-level owner, root, index, or Skill is created, retired, moved, or changes responsibility.

Do not update the map for ordinary child-document changes. Discover children through the nearest owner README, index, Skill, or owner document and use filesystem search when completeness matters.

Update a design index only when a root active design is created, changes ownership status, or moves to/from historical storage.

## Document boundaries

- `docs/WORK_PLAN.md`: current slice, next action, blockers, constraints, and holds.
- `project_brief.md`: current Phase / Arc / Milestone map.
- `docs/REFACTOR_PLAN.md`: refactor candidates and structural triggers.
- `project_log.md`: durable chronology, milestone decisions, failures, and lessons.
- `docs/decisions/`: compact decision rationale whose reason is not obvious from current source.
- `docs/failures/`: repeated/non-obvious failed approaches and no-repeat guidance.
- `result_reports/memory/project_memory_seed.md`: compact routing/index for bounded recall.
- standard/dev notes: reusable specification interpretation, calculation rationale, and schema meaning.
- historical Result Records: point-in-time evidence only.

Update only the owner whose state actually changed.

## Historical Result Records

Existing `result_reports/records/`, `result_reports/legacy/`, `result_reports/REPORT_INDEX.md`, and memory archives remain historical evidence. Do not create a Result Record merely because a change affects architecture, harness policy, schema, calculator behavior, release state, or manual evidence.

When a new durable reason is needed, prefer the current owner document or a focused decision/failure record. Git history already owns commit-level changed-file provenance.

## Session handoff

Run only when the user explicitly requests a handoff, next-session plan, or next-agent read pointer.

1. Check whether `project_brief.md` broad state is accurate.
2. Update `docs/WORK_PLAN.md` only where current execution state changed.
3. Provide a compact read-first set and one next action.
4. Update durable memory only when the handoff reveals a genuinely reusable decision, failure, resume clue, or owner relationship.

Keep combined read pointers to roughly 3-7 items. Do not reconstruct completed report history or make historical Result Records default first reads.

## Git and final-state sync

When commit/push is in scope, synchronize only documents whose owned state changed. This lifecycle owner does not create an additional approval, report, memory-review, or terminal-report ceremony.
