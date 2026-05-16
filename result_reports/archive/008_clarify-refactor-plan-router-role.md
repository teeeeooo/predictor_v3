# 008_clarify-refactor-plan-router-role

## Goal
- Clarify the `docs/REFACTOR_PLAN.md` role in `AGENT_TASK_ROUTER.md`.
- Remove wording that made `REFACTOR_PLAN.md` look like a live TODO or next-execution-order document.

## Scope
- Modify only `AGENT_TASK_ROUTER.md`.
- Keep `docs/WORK_PLAN.md` and `docs/REFACTOR_PLAN.md` roles separate.
- Do not read or modify `docs/archive/AGENTS_FULL.md`.

## Verification
- Ran `git diff -- AGENT_TASK_ROUTER.md`.
- Ran `git diff --name-only` and confirmed the source change was only `AGENT_TASK_ROUTER.md`.
- Ran `rg -n "살아있는 TODO|다음 실행 순서|REFACTOR_PLAN" AGENT_TASK_ROUTER.md`.
- Confirmed `다음 실행 순서` remains only in `docs/WORK_PLAN.md` role wording.
- Confirmed no diff in `AGENTS.md`, `docs/archive/AGENTS_FULL.md`, owner docs, code, tests, or model artifact paths.
- Ran `git diff --check -- AGENT_TASK_ROUTER.md`.
- Did not run tests by request.

## Task Results

### task 1 결과
- 수정 파일: `AGENT_TASK_ROUTER.md`
- 수정 내용:
  - Added a separate `docs/WORK_PLAN.md` item in Documentation Sync & Lifecycle Gate for current priorities, next execution order, phase transitions, and Z-phase management.
  - Reworded `docs/REFACTOR_PLAN.md` as the owner for refactoring candidates, structure-separation triggers, guardrails, and separation strategy.
  - Removed `살아있는 TODO` wording from the REFACTOR_PLAN role.
  - Replaced TODO-list phrasing with refactoring-candidate phrasing.
- 검증 결과: OK
- OK/NG: OK

## Test Results
- Not run by request. This was a docs-only wording cleanup.

## Changed Files
- `AGENT_TASK_ROUTER.md`
- `result_reports/active/008_clarify-refactor-plan-router-role.md`

## Known Risks
- Numbered lifecycle items shifted because `docs/WORK_PLAN.md` now has its own item in that list. No routing behavior was otherwise changed.

## Scope Compliance
- `AGENTS.md`: not modified
- `docs/archive/AGENTS_FULL.md`: not read or modified
- `docs/WORK_PLAN.md`: not modified
- `docs/REFACTOR_PLAN.md`: not modified
- `project_log.md`: not modified
- code/tests/model artifact: not modified
- next documentation phase: not started

## Commit / Push
- source/docs commit: `28c44cf`
- report commit: committed separately by `report: record refactor plan router wording`; final hash is reported in terminal/final summary because a commit cannot contain its own final hash.
- pushed branch: `main`
