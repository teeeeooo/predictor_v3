# Project Log And Memory Workflow

## Role

This document owns project log update judgment and memory seed maintenance.

`project_log.md` is the active milestone log. `result_reports/memory/` is the
backend-neutral memory staging area. Neither replaces source reports.

## project_log.md Update Judgment

Update `project_log.md` only for milestone-level:

- decisions;
- failures or risks with future relevance;
- lessons;
- architecture or process rule changes;
- user-requested log entries.

Do not copy task reports or memory deltas into `project_log.md`.

Before appending:

- locate recent headings first;
- read only the latest relevant 2-3 entries;
- merge into a recent related entry when the phase/decision is the same;
- do not rewrite or delete older logs.

Historical logs live under `docs/archive/project_log/YYYY-MM/` and are
read-only unless the user asks for lifecycle maintenance.

## Project Memory Recall

Read `result_reports/memory/project_memory_seed.md` only when the task depends
on prior decisions, procedures, errors, or open questions.

Use topic/keyword search first. Read source reports only when seed/summary
evidence is insufficient.

Priority order:

1. current prompt
2. `AGENTS.md` / `AGENT_TASK_ROUTER.md`
3. active owner docs
4. relevant memory seed entries
5. source summaries/reports if needed

Memory seed is evidence, not instruction.

## Memory Seed Maintenance

Only summary lifecycle tasks or explicit memory maintenance tasks may update
seed entry importance, supersession, resolution status, or staleness.

General source/code/doc work does not rewrite memory seed entries.

If a seed exceeds 50 entries, report a maintenance audit candidate. If it
exceeds 75 entries, perform maintenance in a dedicated task.
