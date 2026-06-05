# Result Report Workflow

## Role

This document owns result report creation, numbering, terminal output, and
commit/push expectations for agent work.

`AGENT_TASK_ROUTER.md` only routes to this document; it is not the detailed
report workflow owner.

## When A Report Is Required

Create a Markdown report under `result_reports/active/` when:

- tracked files are created, modified, deleted, or moved;
- code, docs, tests, config, model artifacts, contracts, or public behavior
  change;
- an audit result should remain as a future reference artifact;
- summary/archive/project log lifecycle maintenance is performed;
- the user explicitly asks for a report.

No-report / terminal-only mode is allowed only when no repo files are changed
and the task is a simple status, diff, push, or cause analysis response.

## Report Location And Numbering

- Active reports: `result_reports/active/`
- Summaries: `result_reports/summaries/`
- Archive: `result_reports/archive/`
- Memory staging: `result_reports/memory/`

Report filename format:

- `NNN_verb-target-scope.md`

Numbering rule:

- Use the maximum existing report number across `active`, `archive`, and
  `summaries`, then add 1.
- Do not restart numbering in a new session.
- Do not create phase-specific numbering.
- Do not run `git pull`, `git merge`, or `git rebase` just to determine the
  next number.

## Report Modes

Full report mode is required for:

- logic/code changes;
- architecture-sensitive changes;
- calculator/golden/fixture/config changes;
- test additions or behavior guard changes;
- schema, contract, or public API impact.

Compact report mode is allowed for:

- docs wording or routing cleanup;
- link/path expression updates;
- report lifecycle maintenance;
- audit/report-only work without code behavior changes.

Compact report minimum sections:

- Goal
- Scope
- Changed Files
- Verification
- Known Risks
- Commit / Push

Full report default sections:

- Goal
- Scope
- Non-goals
- Verification
- Task Results
- Test Results
- Changed Files
- Known Failures / Risks
- Next Suggested Action
- Scope Compliance
- Commit / Push
- Project Memory Delta

## Terminal Output

For report-backed work, keep terminal/final output short. Detailed results
belong in the report.

Use this final shape:

- `task N: OK/NG - short summary`
- `modified: path/to/file1, path/to/file2`
- `report: result_reports/active/NNN_name.md`

`modified:` includes only files actually changed by the task. Do not include
pre-existing unrelated dirty files.

## Commit / Push

- Report files are task artifacts and must be committed and pushed when
  created.
- Prefer separate source/docs and report commits when practical.
- Audit/report-only work may commit only the report.
- Record commit hash and push status in the report.
- Do not run `git pull`, `git merge`, or `git rebase` unless the user asks.

## Project Memory Delta

Use `Project Memory Delta` only for long-lived memory candidates.

- Full reports include the section; use `- none` if no candidate exists.
- Compact reports include it only when the work creates a durable decision,
  procedure, error, open question, or relation.
- No-report / terminal-only mode never creates memory deltas.

Memory delta entries are backend-neutral. Required fields:

- `type`
- `topic`
- `content`
- `keywords`
- `assertionStatus`
- `source`

`keywords` must be a YAML list, not a comma-separated string.

Allowed `type` values:

- `fact`
- `decision`
- `error`
- `preference`
- `procedure`
- `relation`
- `episode`
- `open_question`

Allowed `assertionStatus` values:

- `observed`
- `inferred`
- `verified`
- `rejected`
