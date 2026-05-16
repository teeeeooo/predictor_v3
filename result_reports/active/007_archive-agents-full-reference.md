# 007_archive-agents-full-reference

## Goal
- Move `AGENTS_FULL.md` from the active repository root to archive.
- Update active inbound references so root-path references do not break.

## Scope
- Move `AGENTS_FULL.md` to `docs/archive/AGENTS_FULL.md`.
- Update only active references in `AGENTS.md`, `AGENT_TASK_ROUTER.md`, and `docs/PACKAGING.md`.
- Create this result report.

## Non-goals
- No rewrite or bulk deletion of archived `AGENTS_FULL.md` content.
- No routing structure change.
- No new policy.
- No code, tests, model artifact, `docs/knowledge/*`, `docs/architecture/*`, `docs/WORK_PLAN.md`, `docs/REFACTOR_PLAN.md`, or `project_log.md` edits.

## Task Results

### task 1 결과
- 이동 파일: `AGENTS_FULL.md` -> `docs/archive/AGENTS_FULL.md`
- 이동 내용: File moved with `git mv`; content retained without rewrite or bulk deletion.
- 검증 결과: OK. `docs/archive/AGENTS_FULL.md` exists and root `AGENTS_FULL.md` no longer exists.
- OK/NG: OK

### task 2 결과
- 수정 파일:
  - `AGENTS.md`
  - `AGENT_TASK_ROUTER.md`
  - `docs/PACKAGING.md`
- 수정 내용:
  - Updated active references from root `AGENTS_FULL.md` to `docs/archive/AGENTS_FULL.md`.
  - Preserved the default rule that the archived detailed reference is not read unless explicitly requested or needed for high-risk rationale.
  - Updated packaging historical owner note to point at the archived path.
- 검증 결과: OK. Active root-path references were removed; historical result reports and archive logs still mention `AGENTS_FULL.md` as historical context.
- OK/NG: OK

## Verification
- Ran `git status --short`.
- Ran `git diff --name-only`.
- Ran `rg -n "AGENTS_FULL|Detailed Domain Reference|상세 에이전트|전체 규칙" . --glob "*.md"`.
- Confirmed `docs/archive/AGENTS_FULL.md` exists.
- Confirmed root `AGENTS_FULL.md` no longer exists.
- Checked no source diffs under code/test/model artifact or forbidden doc areas.
- Did not run tests by request.

## Changed Files
- `AGENTS.md`
- `AGENT_TASK_ROUTER.md`
- `docs/PACKAGING.md`
- `docs/archive/AGENTS_FULL.md`
- `result_reports/active/007_archive-agents-full-reference.md`

## Known Risks
- Historical result reports and archived logs still mention `AGENTS_FULL.md`; these are intentionally left unchanged as historical records.
- Future prompts that explicitly ask for root `AGENTS_FULL.md` should use `docs/archive/AGENTS_FULL.md` instead.

## Scope Compliance
- archive move: performed to `docs/archive/AGENTS_FULL.md`
- archived file content rewrite/bulk deletion: not performed
- active inbound references: updated
- code/tests/model artifact: not modified
- `docs/knowledge/*`: not modified
- `docs/architecture/*`: not modified
- `docs/WORK_PLAN.md`: not modified
- `docs/REFACTOR_PLAN.md`: not modified
- `project_log.md`: not modified
- next documentation cleanup phase: not started

## Commit / Push
- source/docs commit: `461f5a0`
- report commit: committed separately by `report: record agents full archive move`; final hash is reported in terminal/final summary because a commit cannot contain its own final hash.
- pushed branch: `main`
