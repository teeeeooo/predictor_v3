# 015_add-result-report-no-report-mode

## Goal
- Add a Result Report Workflow exception for no-report / terminal-only mode.

## Scope
- Update `AGENT_TASK_ROUTER.md` only.
- Keep existing numbering, summary, archive, metadata-only lifecycle check, Full report, and Compact report policies intact.

## Changed Files
- `AGENT_TASK_ROUTER.md`
- `result_reports/active/015_add-result-report-no-report-mode.md`

## Verification
- `git diff -- AGENT_TASK_ROUTER.md`
- `git diff --name-only`
- `rg -n "No-report|terminal-only|Compact report|Full report|Lifecycle check|report required|파일 수정 없는|tracked file" AGENT_TASK_ROUTER.md`
- `find result_reports -maxdepth 2 -type d`
- Tests were not run, per task scope.

## Known Risks
- No lifecycle maintenance was performed.
- No summary/archive/project_log changes were made.
- No code, tests, model artifacts, `AGENTS.md`, `docs/WORK_PLAN.md`, `docs/REFACTOR_PLAN.md`, or `docs/archive/AGENTS_FULL.md` changes were made.

## Commit / Push
- source/docs commit: `265717c` (`docs: add no-report result workflow mode`)
- report commit: this commit (`report: record no-report workflow mode`)
- push: pending
