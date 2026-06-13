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

Summary/archive lifecycle maintenance must route to
`docs/agent_workflows/PROJECT_LOG_AND_MEMORY.md` for the memory seed check
before closeout.

Compact report minimum sections:

- Goal
- Scope
- Changed Files
- Verification
- Known Risks
- Commit / Push

Compact audit reports should preserve the decision, not duplicate terminal
output. Prefer a short inventory table or tight bullets for evidence,
classification, decision, and next action. Keep validation and command output to
one-line status summaries unless a failure/blocker needs detail.

For compact report-only or narrow UI correction work, keep MVC/SoC, behavior
preservation, and known risks to one or two bullets each unless the decision
would otherwise be ambiguous.

If the user explicitly asks for no report on a docs/workflow cleanup, do not
create a report solely because a tracked docs file changed. Keep the terminal
summary short and record the commit/push result there.

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

When a new UI surface, script, helper, adapter, workflow path, or reusable
component is created or an existing stable path is replaced/extended, include a
short reference parity section: whether an existing reference was checked, why it
was or was not reused, and any unresolved parity gaps.

For structure-impacting source changes, include a compact code map judgment from
`docs/agent_workflows/DIFF_READ_BUDGET.md`:

- `code_map_check`: `checked`, `skipped`, `regenerated`, or `no-change`
- if skipped, record the short reason;
- if regenerated, record whether `docs/code_map/CODEBASE_REFERENCE_MAP.md` is
  included in the diff.

For report-backed source/test changes, include compact structure warning
coverage when relevant:

- `Structure Warnings`: `none` is enough when no changed/new source file emits a
  structure warning, or for docs-only work.
- `Warning Triage`: if a changed/new source file emits a soft warning, record
  the warning path, reason, and action.

Recommended warning triage actions:

- `none`
- `accepted for this slice with reason`
- `split audit required before next code slice`
- `split implementation required before continuing`
- `blocked`

Do not turn every report into a long template. The rule is to prevent source
structure warnings from being hidden behind "validation OK"; it does not change
the active report count policy or the commit/push wording policy.

## Report Content

- Do not record personal author names, email addresses, or other identifying
  information in report bodies. The report is a task artifact, not a personal
  attribution document. Git commit metadata already tracks authorship.

## Terminal Output

For report-backed work, keep terminal/final output short. Detailed results
belong in the report.

When the user does not require a fixed long output schema, use at most six short
lines: `modified`, `created/report` when relevant, `validation`, `commit`,
`push`, and `next`. Do not repeat report sections in terminal output.

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
- If recording the report commit hash would require editing the same report,
  do not create a self-referential hash/update loop. Record the source/docs
  commit when useful, and put the final pushed commit hash and push result in
  the terminal/final response.
- Do not leave `pending` commit/push wording in a completed report when no
  follow-up report update is planned.
- For a user-requested commit/push-only follow-up after validation already ran
  and no files changed since, do not repeat validation. Use one compact
  commit/push command sequence and one short final line with hash, push status,
  and clean/dirty status.
- When the user requested commit/push for a report-backed task, check the
  active report count before final output. If `result_reports/active/` has
  more than 10 reports, do not run lifecycle maintenance automatically; add a
  short terminal note that summary/archive maintenance is pending and should
  be handled as a separate follow-up.
- Active report count command: `find result_reports/active -maxdepth 1 -type f -name '*.md' | wc -l`
- Do not run `git pull`, `git merge`, or `git rebase` unless the user asks.
- **Active Report Count Wording Policy**:
  - Do not write the exact active report count in durable documents (e.g., `WORK_PLAN.md`, `project_log.md`, or report bodies).
  - Use threshold wording instead (e.g., "active report count exceeds lifecycle threshold; cleanup pending").
  - Report the exact count only in the final agent terminal output under the `active_report_count` key.
  - If the exact count is absolutely required in the report body, calculate it during the final verification step *after* all new active report files have been created. The default policy remains to omit exact numbers from durable documents.

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
