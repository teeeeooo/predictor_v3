# 012_add-result-report-lifecycle-check

## Goal
- Add explicit lifecycle auto-check rules to the Result Report Workflow.
- Let future agents detect when summary, project_log sync, or archive lifecycle maintenance is needed.

## Scope
- Modify only `AGENT_TASK_ROUTER.md`.
- Add lifecycle check trigger and maintenance scope rules inside Result Report Workflow.
- Do not perform actual lifecycle maintenance in this task.
- Do not read or modify `docs/archive/AGENTS_FULL.md`.

## Verification
- Ran `git diff -- AGENT_TASK_ROUTER.md`.
- Ran `git diff --name-only` and confirmed the source change was only `AGENT_TASK_ROUTER.md`.
- Ran `rg -n "Lifecycle check|lifecycle maintenance|summary|archive|project_log|standing approval|workstream" AGENT_TASK_ROUTER.md`.
- Ran `find result_reports -maxdepth 2 -type d` and confirmed no `result_reports/archive` directory was created.
- Confirmed no diff in `AGENTS.md`, `docs/archive/AGENTS_FULL.md`, `docs/WORK_PLAN.md`, `docs/REFACTOR_PLAN.md`, `project_log.md`, code, tests, model artifact paths, or result reports.
- Ran `git diff --check -- AGENT_TASK_ROUTER.md`.
- Did not run tests by request.

## Task Results

### task 1 결과
- 수정 파일: `AGENT_TASK_ROUTER.md`
- 수정 내용:
  - Added `Lifecycle check` rules under Result Report Workflow.
  - Added check timing after result report create/commit/push work and before final response.
  - Added trigger conditions for 8-12 active reports, completed workstream/arc, existing summary with unarchived covered reports, and pending `project_log.md` recommendation.
  - Added behavior that safe lifecycle maintenance proceeds as a separate step/commit instead of only reporting pending work.
  - Added lifecycle maintenance scope: summary creation or reuse, `project_log.md` sync judgment/update, covered active report archive move, archive folder creation when needed, and no report renaming.
  - Added standing approval limitation to result reports, summary, archive, and `project_log.md` only.
  - Added explicit handling for existing `011_summary-agent-rules-doc-workflow.md`: do not create duplicate summary; continue from existing summary candidates and sync judgment.
- 검증 결과: OK
- OK/NG: OK

## Test Results
- Not run by request. This was a docs-only workflow update.

## Changed Files
- `AGENT_TASK_ROUTER.md`
- `result_reports/active/012_add-result-report-lifecycle-check.md`

## Known Risks
- The new lifecycle rule would identify the current `011` summary plus unarchived covered reports as a pending lifecycle condition, but this task explicitly prohibited actual summary/archive/project_log maintenance.
- Future agents should treat that as lifecycle maintenance pending when scope and working tree are safe.

## Scope Compliance
- actual summary creation: not performed
- active report archive move/rename: not performed
- `project_log.md`: not modified
- `result_reports/archive`: not created
- `AGENTS.md`: not modified
- `docs/archive/AGENTS_FULL.md`: not read or modified
- `docs/WORK_PLAN.md`: not modified
- `docs/REFACTOR_PLAN.md`: not modified
- code/tests/model artifact: not modified
- unrelated refactor: not performed

## Commit / Push
- source/docs commit: `eeb454a`
- report commit: committed separately by `report: record result report lifecycle check`; final hash is reported in terminal/final summary because a commit cannot contain its own final hash.
- pushed branch: `main`
