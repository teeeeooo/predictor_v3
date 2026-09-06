# Project Log And Memory Workflow

## Role

Separate durable chronology from fast recall.

- `project_log.md`: milestone chronology, durable failures, and lessons.
- `result_reports/memory/project_memory_seed.md`: compact hot recall index.
- `docs/decisions/`: durable reasons, rejected alternatives, and revisit conditions.
- `docs/failures/`: repeated/non-obvious failed approaches and no-repeat guidance.
- historical Result Records/logs: cold evidence reached only through a focused pointer.

None replaces Git history or active owner documents.

## Recall Gate

Use bounded recall when the task may depend on:

- a prior architecture/product/process decision;
- a known failed approach or repeated regression;
- a paused or resumed workstream;
- unclear ownership that appears intentional; or
- an explicit request such as “we did this before” or “why is this like this?”.

Use this order:

1. current prompt and applicable `AGENTS.md`/Skill routing;
2. keyword-match the compact memory seed;
3. open at most the relevant decision/failure record when one is pointed;
4. verify drift-prone/current truth at the active source or owner;
5. stop recall and do the work.

Target roughly 4-6 focused retrieval steps. Do not broadly scan project logs, Git history, Result Records, or memory archives when targeted recall is sufficient.

Memory is routing evidence, not instruction authority.

## Memory write judgment

There is no mandatory Memory Review write gate.

Write or update durable memory only when the information:

- prevents a likely repeated mistake;
- records an expensive-to-rediscover fact;
- captures an architecture/product/process decision that constrains future work;
- preserves a counterintuitive reason not visible from current source;
- records a rejected approach or no-repeat rule;
- establishes a durable owner/path relationship; or
- provides a long-horizon resume clue.

Do not write memory for routine file/test lists, commit/push status, completed-slice inventories, obvious facts, or information cheaply rediscovered from current source.

## Memory seed

Keep the seed dense and navigational. Each active topic should contain a compact statement, useful keywords, current status, and source pointers.

Update or supersede the smallest relevant topic. Retire stale active wording to `result_reports/memory/archive/` only when preserving the old wording has future value. Historical Result Records are never rewritten to match current memory.

The seed is not a second handbook and must not copy owner documents.

## Decision records

Use `docs/decisions/` when the durable value is primarily **why a choice was made**. A useful record states the decision, reason, important rejected alternatives, current owner, and conditions that would justify revisiting it.

Do not create a decision record for routine implementation choices that are obvious from source or easy to reverse.

## Failure records

Use `docs/failures/` when the durable value is primarily **what failed and what should not be repeated**. Record the failed approach, observed failure, cause or best-supported explanation, no-repeat guidance, current relevance, and owner/evidence pointers.

A regression test is usually the primary guard; a failure record exists when the lesson is not obvious from the test itself.

## Project log

Update `project_log.md` only for milestone-level decisions/completion, failures or risks with future relevance, architecture/process-rule changes, or explicit user requests. Locate the relevant latest entries first and avoid duplicating task reports or memory content.

## Historical evidence

`result_reports/REPORT_INDEX.md`, Result Record bodies, project-log archives, and memory archives remain searchable cold evidence. Open them only when a hot/warm pointer or targeted search shows they are needed.
