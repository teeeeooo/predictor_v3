# 005_cleanup-agents-full-archive-readiness

## Goal
- Perform first-pass cleanup of `AGENTS_FULL.md` before any archive move.
- Refresh stale archive/migration wording.
- Retire obsolete completion/report format wording as active guidance.

## Scope
- Modify only `AGENTS_FULL.md` as source documentation.
- Create this result report as the workflow artifact.
- Do not move `AGENTS_FULL.md` to archive.

## Non-goals
- No archive move.
- No full rewrite or bulk deletion of `AGENTS_FULL.md`.
- No changes to `AGENTS.md`, `AGENT_TASK_ROUTER.md`, owner docs, code, tests, or model artifacts.
- No next archive phase.

## Verification
- Ran `git diff -- AGENTS_FULL.md`.
- Ran `git diff --name-only` before report creation and confirmed the source change was only `AGENTS_FULL.md`.
- Checked `AGENTS.md`, `AGENT_TASK_ROUTER.md`, `docs`, `core`, `tests`, and `model` had no source diff.
- Ran `git diff --check -- AGENTS_FULL.md`.
- Did not run tests by request.

## Task Results

### task 1 결과
- 수정 파일: `AGENTS_FULL.md`
- 수정 내용:
  - Updated `Migration & Archive Note` to state that `AGENTS_FULL.md` is a Detailed Domain Reference, not active working rules.
  - Recorded that Packaging, UI, ML knowledge, KS C 9306, AHRI HSPF2, and ML training/model artifact guardrails have owner documents.
  - Kept archive move as a separate user-approved task.
- 검증 결과: OK. Source diff was limited to `AGENTS_FULL.md`.
- OK/NG: OK

### task 2 결과
- 수정 파일: `AGENTS_FULL.md`
- 수정 내용:
  - Renamed the reporting section from old completion-format wording to reporting baseline wording.
  - Pointed current completion, commit, and result report workflow to `AGENTS.md` and `AGENT_TASK_ROUTER.md`.
  - Downgraded the old bracket-style completion report to a historical example and removed active-rule wording.
- 검증 결과: OK. Result report workflow itself was not changed.
- OK/NG: OK

## Test Results
- Not run by request. This was a docs-only cleanup.

## Changed Files
- `AGENTS_FULL.md`
- `result_reports/active/005_cleanup-agents-full-archive-readiness.md`

## Known Failures / Risks
- `AGENTS_FULL.md` is still not archived; archive move remains a separate user-approved phase.
- This cleanup does not remove all historical domain rules from `AGENTS_FULL.md`; it only updates stale archive/readiness wording and obsolete report format wording.

## Next Suggested Action
- If approved later, run a separate archive-readiness confirmation or archive-move task.

## Scope Compliance
- `AGENTS_FULL.md` archive move: not performed
- `AGENTS_FULL.md` full rewrite/bulk deletion: not performed
- `AGENTS.md`: not modified
- `AGENT_TASK_ROUTER.md`: not modified
- owner docs: not modified
- code/tests/model artifact: not modified
- tests/training: not run
- next archive phase: not started

## Commit / Push
- source/docs commit: `547f5b5`
- report commit: committed separately by `report: record agents full cleanup`; final hash is reported in terminal/final summary because a commit cannot contain its own final hash.
- pushed branch: `main`
