# Diff And Read Budget

## Role

This document owns token/read discipline for document, diff, and code
inspection.

`AGENT_TASK_ROUTER.md` points here when a task needs detailed read-budget
rules.

## Start Gate

Before reading long files, define one short read budget:

- target files;
- target headings / keywords;
- allowed initial range size;
- blocker that would justify broad-read expansion.

Use target files and heading ranges first. Broad reads are allowed only after
a blocker is stated. "Might be useful" is not a blocker.

## Default Order

1. Define the read budget.
2. `git diff --name-only`
3. `git diff --stat`
4. `git status --short`
5. `rg -n "<function_or_keyword>" <target files>`
6. `sed -n '<small range>' <file>`
7. Only if still needed: `git diff -- <file>` or a narrow hunk/range.

## Smoke Follow-up Order

For manual-smoke follow-up or narrow bug follow-up work, keep the first pass to
the reported issue path:

1. issue symptom / acceptance gap;
2. likely owner file or owner function;
3. focused test or fake-surface guard for that owner;
4. impacted boundary tests only after the owner path is understood.

Do not re-read broad history, full reports, or `docs/WORK_PLAN.md` unless the
owner path is ambiguous or the task changes direction.

## Search Rules

- Use exact phrases, function names, filenames, or stable labels before broad
  keywords.
- Avoid searching many broad keywords at once.
- If broad search is needed, first reduce candidate files with `rg -l` or
  already confirmed owner files.
- For docs-wide questions, start with `docs/WORK_PLAN.md` and active reports,
  then expand only if owner/pending evidence is missing.

## Read Range Rules

- Start `sed` at 30-80 lines.
- Reading more than 100 lines from one file at once requires a stated blocker.
- `head` / `tail` broad checks are not allowed for policy or log files unless
  a blocker is stated.
- Parallel reads should keep combined output small; target 150 lines or less.
- Tool output budget starts small and increases only when truncated output is
  needed.

## project_log.md

When project log sync judgment is needed:

- first locate headings with `rg -n "^## " project_log.md | tail -n 5`;
- read only the latest relevant 2-3 entries;
- do not use broad `head` or `tail` content reads.

## Tests And Command Output

- Run focused tests first.
- Inspect long tracebacks only after failure.
- Full pytest is allowed when the task touches core, calculator, ML, schema,
  golden, or broad behavior, but the need must be explicit.
