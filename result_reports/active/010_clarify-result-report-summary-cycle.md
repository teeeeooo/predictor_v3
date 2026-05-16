# 010_clarify-result-report-summary-cycle

## Goal
- Clarify Result Report Workflow rules for numbering, summary grouping, archive candidates, and project_log sync timing.
- Keep global sequential report numbering and avoid phase-specific numbering or folders.

## Scope
- Modify only the Result Report Workflow section of `AGENT_TASK_ROUTER.md`.
- Do not create `result_reports/summaries/` or `result_reports/archive/`.
- Do not move or rename existing reports.
- Do not read or modify `docs/archive/AGENTS_FULL.md`.

## Verification
- Ran `git diff -- AGENT_TASK_ROUTER.md`.
- Ran `git diff --name-only` and confirmed the source change was only `AGENT_TASK_ROUTER.md`.
- Ran `rg -n "Summary grouping|archive|project_log|workstream|phase-specific|result_reports/summaries|result_reports/archive|다음 번호" AGENT_TASK_ROUTER.md`.
- Ran `find result_reports -maxdepth 2 -type d` and confirmed only `result_reports` and `result_reports/active` exist.
- Confirmed no diff in `AGENTS.md`, `docs/archive/AGENTS_FULL.md`, `docs/WORK_PLAN.md`, `docs/REFACTOR_PLAN.md`, `project_log.md`, code, tests, model artifact paths, or active reports.
- Ran `git diff --check -- AGENT_TASK_ROUTER.md`.
- Did not run tests by request.

## Task Results

### task 1 결과
- 수정 파일: `AGENT_TASK_ROUTER.md`
- 수정 내용:
  - Kept max-number + 1 global numbering across active/archive/summaries paths.
  - Added explicit global sequential numbering and no phase-specific numbering/folder rules.
  - Added Summary grouping / archive cycle guidance using workstream/arc grouping.
  - Added example workstreams: `agent-rules`, `iso16358-hspf`, `docs-linktree`, `calculator-ui`, `ml-knowledge`.
  - Added summary timing guidance for about 8-12 active reports or a completed large workstream.
  - Added summary-time `project_log.md` sync judgment rules.
  - Clarified archive candidate handling and user-approved archive moves without renaming report files.
  - Clarified that `summaries/` and `archive/` folders are created only when an approved summary/archive phase needs them.
- 검증 결과: OK
- OK/NG: OK

## Test Results
- Not run by request. This was a docs-only workflow wording update.

## Changed Files
- `AGENT_TASK_ROUTER.md`
- `result_reports/active/010_clarify-result-report-summary-cycle.md`

## Known Risks
- `result_reports/summaries/` and `result_reports/archive/` are referenced as workflow paths but do not exist yet; the updated rule explicitly leaves their creation to a future approved summary/archive phase.

## Scope Compliance
- report move/rename: not performed
- summaries/archive folder creation: not performed
- `project_log.md`: not modified
- `AGENTS.md`: not modified
- `docs/archive/AGENTS_FULL.md`: not read or modified
- `docs/WORK_PLAN.md`: not modified
- `docs/REFACTOR_PLAN.md`: not modified
- code/tests/model artifact: not modified
- next documentation phase: not started

## Commit / Push
- source/docs commit: `862ee41`
- report commit: committed separately by `report: record result report summary cycle`; final hash is reported in terminal/final summary because a commit cannot contain its own final hash.
- pushed branch: `main`
