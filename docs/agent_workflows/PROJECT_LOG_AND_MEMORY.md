# Project Log And Memory Workflow

## Role

This document separates durable history from fast agent recall.

- `project_log.md`: milestone decisions, durable failures, and lessons.
- result records: immutable-at-creation change reasons and evidence.
- `project_memory_seed.md`: compact current memory for resuming a long-running,
  branching project.

None replaces Git history or active owner documents.

## Project Log Judgment

Update `project_log.md` only for:

- milestone-level decisions or completion;
- failures/risks with future relevance;
- architecture or process-rule changes;
- explicit user requests.

Do not copy task reports, test logs, changed-file lists, or memory entries into
the project log. Locate headings first and read only the latest relevant 2-3
entries before appending or merging.

## Memory Recall

Read `result_reports/memory/project_memory_seed.md` only when the task depends
on prior decisions, procedures, repeated errors, open questions, or a paused
workstream.

Use this order:

1. current prompt;
2. `AGENTS.md` and the matching repository-local Skill when task procedure is needed;
3. active owner docs;
4. keyword-matched memory entry;
5. pointed record/legacy evidence only if needed.

Memory is evidence, not instruction.

## Memory Review Gate

Perform a memory review when:

- a compact result record is created;
- a milestone or branch closes;
- the user requests a session/agent handoff;
- work returns to a long-paused branch or domain.

For a compact record, set:

```yaml
memory_review: updated
memory_reason: <what durable memory changed>
```

or:

```yaml
memory_review: no-change
memory_reason: <why current seed is sufficient>
```

The staged checker requires the memory seed in the same change when the value is
`updated`.

For a handoff or workstream transition without a result record, include the same
judgment in the handoff/final status and update the seed before closeout when
needed.

## What Belongs In Memory

Keep:

- current long-lived decisions and invariants;
- cross-workstream owner relationships;
- paused-workstream resume points;
- repeated errors and approaches to avoid;
- unresolved questions with future impact;
- pointers to owner docs and durable evidence.

Exclude:

- routine file/test lists;
- completed slice inventories;
- commit/push status;
- report or owner-doc copies;
- facts easily rediscovered from the current source.

Update or supersede the smallest relevant entry. Memory maintenance must not
rewrite historical result records. A dedicated cleanup is needed only when the
seed itself becomes hard to search or contains many stale active entries; report
counts do not trigger memory cleanup.
