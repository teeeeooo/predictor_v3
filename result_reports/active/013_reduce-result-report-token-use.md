# 013_reduce-result-report-token-use

## Goal
- Clarify that routine lifecycle checks are metadata-only.
- Add Full report / Compact report mode guidance to reduce token use on simple work.

## Scope
- Changed only `AGENT_TASK_ROUTER.md`.
- No summary, archive, or `project_log.md` lifecycle maintenance was performed.
- Did not read or modify `docs/archive/AGENTS_FULL.md`.

## Changed Files
- `AGENT_TASK_ROUTER.md`
- `result_reports/active/013_reduce-result-report-token-use.md`

## Verification
- Ran `git diff -- AGENT_TASK_ROUTER.md`.
- Ran `git diff --name-only`; source change was only `AGENT_TASK_ROUTER.md` before this report.
- Ran `rg -n "metadata-only|Compact report|Full report|Lifecycle check|report 본문|summary|archive|project_log" AGENT_TASK_ROUTER.md`.
- Ran `find result_reports -maxdepth 2 -type d`; no new `result_reports/archive` directory was created.
- Confirmed no diff in `AGENTS.md`, `docs/archive/AGENTS_FULL.md`, `project_log.md`, code, tests, model artifact, `docs/WORK_PLAN.md`, or `docs/REFACTOR_PLAN.md`.
- Ran `git diff --check -- AGENT_TASK_ROUTER.md`.
- Tests were not run by request.

## Known Risks
- Current repository state still has a summary with covered active reports not archived, but actual lifecycle maintenance was explicitly out of scope for this task.
- Compact report mode was introduced by this change, so this report uses the new compact shape with the required verification/scope notes.

## Commit / Push
- source/docs commit: `9351f05`
- report commit: committed separately by `report: record result report token use update`; final hash is reported in terminal/final summary because a commit cannot contain its own final hash.
- pushed branch: `main`
