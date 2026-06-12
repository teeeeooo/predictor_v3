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
7. Only if still needed: `git diff -U1 -- <file>` or a narrow hunk/range.

Keep source and test searches separate by default. Search source owners first;
search tests only after the behavior or assertion surface is clear. Avoid one
large `rg` across source and tests unless the task is specifically locating a
symbol across both.

## Audit / Report Read Sequence

For audit/report work, make the first source pass structural, then targeted:

1. locate headings, classes, and methods with `rg -n`;
2. read only the matched heading or method ranges needed for the inventory;
3. use adjacent owner/helper files only to confirm responsibility boundaries;
4. expand to broad chunks only when method boundaries are unclear or the audit
   explicitly requires full-file inventory, and state that blocker first.

Do not use large top-of-file reads such as `sed -n '1,160p'` for policy,
workflow, or source files when a heading/method hit already identifies the
needed range.

For implementation diff review, prefer `git diff --stat` followed by
`git diff -U1 -- <changed file>`. Use full-file diff output only when the hunk
context is insufficient to verify ownership, behavior, or accidental edits.

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

## Reference Evidence Gate

The code_checker reference map (`docs/code_map/CODEBASE_REFERENCE_MAP.md`) is a
conditional pre-write warning-first evidence gate, not a default hard gate. It serves
as a helper to prevent unintended code duplication or architecture bypasses, rather
than a semantic linter. Hard structure rules are enforced by tools like
`tools/check_code_structure.py`.

### Warning-First Checklist

Before editing code, briefly check the following items:
1. **New Responsibility/Surface**: Does the task introduce a new responsibility or surface?
2. **Duplicate Responsibility**: Is there a risk of repeating the same logic across multiple standards, profiles, or sections?
3. **Owner Bypass**: Does it bypass existing owner/helper/adapter paths?
4. **Hotspot Expansion**: Does it add responsibility to already bloated hotspot files?

If the answer to all of the above is **No**, the agent can skip a detailed architecture preflight and proceed directly with the scoped task.

### When to Run

Run only when the task creates, moves, splits, replaces, or commonizes code
surfaces. Examples:

- new helper / adapter / controller / table surface / result formatter /
  workflow script
- file move / split / delete / replacement
- result / detail / export / table / window commonization
- new profile UI / calculator section
- adding responsibility to a known hotspot file

### When to Skip

Skip for work that does not change structure or surface inventory:

- report closeout / lifecycle maintenance
- project_log / WORK_PLAN wording
- Windows smoke result reflection
- focused test expectation correction
- fixture / golden value-only update
- typo / formatting-only change

### Map Read Policy

- Do **not** read the entire map by default.
- Use `rg -n "<keyword>" docs/code_map/CODEBASE_REFERENCE_MAP.md` first.
- Read only the matched 30–80 line range.
- Broad map reads require a stated blocker.

### Map Regenerate Policy

- Regenerate (`python3 -B tools/code_checker/build_reference_map.py`) only after
  structural code changes (new files, moved files, new symbols, removed
  helpers).
- Do not regenerate for wording-only or test-only changes.

### Map Commit Policy

- Commit regenerated map only after significant architecture or surface changes.
- Do not commit map-only changes as standalone noise commits.

### Caveat

The map is reference evidence, not a source of truth or a semantic linter. Canonical rules live in `AGENTS.md`,
`docs/architecture/`, and `docs/WORK_PLAN.md`.

## Tests And Command Output

- During implementation, run the highest-risk focused test or compile command
  first; defer the full required validation command set to the final check.
- If an early focused check already passed, do not rerun it before final
  validation unless code affecting that path changed again.
- Inspect long tracebacks only after failure.
- Full pytest is allowed when the task touches core, calculator, ML, schema,
  golden, or broad behavior, but the need must be explicit.
