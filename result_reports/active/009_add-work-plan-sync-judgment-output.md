# 009_add-work-plan-sync-judgment-output

## Goal
- Add `WORK_PLAN.md` to the Documentation Sync & Lifecycle Gate output checklist.
- Finish the WORK_PLAN / REFACTOR_PLAN role split in `AGENT_TASK_ROUTER.md`.

## Scope
- Modify only `AGENT_TASK_ROUTER.md`.
- Add only the missing output-list item.
- Do not read or modify `docs/archive/AGENTS_FULL.md`.

## Verification
- Ran `git diff -- AGENT_TASK_ROUTER.md`.
- Ran `git diff --name-only` and confirmed the source change was only `AGENT_TASK_ROUTER.md`.
- Ran `rg -n "문서 동기화 판단|WORK_PLAN|REFACTOR_PLAN" AGENT_TASK_ROUTER.md`.
- Confirmed `WORK_PLAN.md` remains the execution order / priority judgment item.
- Confirmed `REFACTOR_PLAN.md` remains the refactoring candidate / structure separation judgment item.
- Confirmed no diff in `AGENTS.md`, `docs/archive/AGENTS_FULL.md`, owner docs, code, tests, or model artifact paths.
- Ran `git diff --check -- AGENT_TASK_ROUTER.md`.
- Did not run tests by request.

## Task Results

### task 1 결과
- 수정 파일: `AGENT_TASK_ROUTER.md`
- 수정 내용:
  - Added `WORK_PLAN.md: 필요/불필요 + 이유` to the `[문서 동기화 판단]` output list.
  - Left the existing WORK_PLAN and REFACTOR_PLAN lifecycle role wording unchanged.
- 검증 결과: OK
- OK/NG: OK

## Test Results
- Not run by request. This was a docs-only wording update.

## Changed Files
- `AGENT_TASK_ROUTER.md`
- `result_reports/active/009_add-work-plan-sync-judgment-output.md`

## Known Risks
- None identified. The change only adds the missing output checklist line.

## Scope Compliance
- `AGENTS.md`: not modified
- `docs/archive/AGENTS_FULL.md`: not read or modified
- `docs/WORK_PLAN.md`: not modified
- `docs/REFACTOR_PLAN.md`: not modified
- `project_log.md`: not modified
- code/tests/model artifact: not modified
- next documentation phase: not started

## Commit / Push
- source/docs commit: `0142ad4`
- report commit: committed separately by `report: record work plan sync output`; final hash is reported in terminal/final summary because a commit cannot contain its own final hash.
- pushed branch: `main`
