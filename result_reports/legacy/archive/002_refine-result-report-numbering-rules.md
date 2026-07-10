# 002_refine-result-report-numbering-rules

## Goal
- Clarify Result Report Workflow rules so report numbering continues across new sessions and different CLI agents.
- Clarify that agents must not run git pull/merge/rebase only to determine the next report number.
- Remove the conflict between the AGENTS.md output rule and the Markdown report workflow.

## Scope
- Update only the `## 출력` section of `AGENTS.md`.
- Update only the relevant Result Report Workflow / Commit-Push wording in `AGENT_TASK_ROUTER.md`.
- Create this result report as `result_reports/active/002_refine-result-report-numbering-rules.md`.
- Commit source/docs changes and this report separately, then push.

## Non-goals
- No code changes.
- No test changes.
- No fixture changes.
- No workbook or reference file changes.
- No ISO calculator logic documentation changes.
- No broad router rewrite or task type rename.
- No weakening of document reading minimization rules.

## Verification
- Confirmed current checkout report numbering across `result_reports/active/`, `result_reports/archive/`, and `result_reports/summaries/`; existing maximum was `001`.
- Confirmed new report path is `result_reports/active/002_refine-result-report-numbering-rules.md`.
- Reviewed `git diff --stat` for changed files.
- Did not run tests because this is a docs-only rule wording change.
- Did not run `git pull`, `git merge`, or `git rebase` for number calculation or commit/push flow.

## Task Results

### task 1 결과
- 수정 파일: `AGENTS.md`
- 수정 내용: `## 출력` section now points completion details to Markdown reports and keeps terminal output limited to OK/NG summaries plus report path.
- OK/NG: OK

### task 2 결과
- 수정 파일: `AGENT_TASK_ROUTER.md`
- 수정 내용: Result Report Workflow now states that all agent environments use the current checkout report numbers, continue from max existing number + 1, do not restart from `001`, and do not run pull/merge/rebase unless explicitly requested.
- OK/NG: OK

### task 3 결과
- 생성 파일: `result_reports/active/002_refine-result-report-numbering-rules.md`
- 작성 내용: Goal / Scope / Non-goals / Verification / Task Results / Changed Files / Known Failures / Next Suggested Action / Scope Compliance / Commit / Push sections.
- OK/NG: OK

### task 4 결과
- source/docs commit: `81f1ff4`
- report commit: this report is committed separately by `report: record result report rule refinement`; final hash is reported in terminal/final summary because a commit cannot contain its own final hash.
- push 결과: pending at report write time
- 최종 git status: pending at report write time
- OK/NG: pending at report write time

## Changed Files
- `AGENTS.md`
- `AGENT_TASK_ROUTER.md`
- `result_reports/active/002_refine-result-report-numbering-rules.md`

## Known Failures / Risks
- Tests were not run because the task is docs-only.
- The report commit hash cannot be recorded inside this report before the report commit exists.

## Next Suggested Action
- None.

## Scope Compliance
- code: not modified
- tests: not modified
- fixtures: not modified
- workbook/reference_files: not modified
- unrelated files: not staged or modified
- git pull/merge/rebase: not performed

## Commit / Push
- source/docs commit: `81f1ff4`
- report commit: committed separately by `report: record result report rule refinement`; final hash is reported in terminal/final summary because a commit cannot contain its own final hash.
- pushed branch: `main`
