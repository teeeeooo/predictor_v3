# 006_audit-agents-full-archive-move-readiness

## Goal
- Perform final read-only audit before moving `AGENTS_FULL.md` to archive.
- Identify inbound references that must be updated during a future archive move.
- Do not move or modify source documents in this task.

## Scope
- Read active rules, documentation maps, prior reports, and `AGENTS_FULL.md`.
- Search Markdown inbound references to `AGENTS_FULL.md`, `Detailed Domain Reference`, `상세 에이전트`, and `전체 규칙`.
- Create this result report only.

## Checked Files
- `AGENTS.md`
- `AGENTS_FULL.md`
- `AGENT_TASK_ROUTER.md`
- `README.md`
- `project_brief.md`
- `docs/README.md`
- `docs/architecture/project_architecture.md`
- `result_reports/active/003_audit-agents-full-archive-readiness.md`
- `result_reports/active/004_migrate-ml-training-artifact-guardrails.md`
- `result_reports/active/005_cleanup-agents-full-archive-readiness.md`

## Inbound References
- Active source references that should be updated if `AGENTS_FULL.md` moves:
  - `AGENTS.md`: root-path references to `AGENTS_FULL.md` in the intro and file-reading policy.
  - `AGENT_TASK_ROUTER.md`: root-path references to `AGENTS_FULL.md` in task routing read/do-not-read lists.
  - `docs/PACKAGING.md`: historical owner note references `AGENTS_FULL.md`; update to the archive path or clarify as archived source.
- No direct `AGENTS_FULL.md` reference found in:
  - `README.md`
  - `project_brief.md`
  - `docs/README.md`
- Historical references that do not need cleanup during the move:
  - existing `result_reports/active/003_*`, `004_*`, `005_*`
  - existing files under `docs/archive/`

## Archive Readiness
- 판단: **ready for user-approved archive move**.
- `AGENTS_FULL.md` now identifies itself as a Detailed Domain Reference, not active working rules.
- Its stale migration note has been refreshed.
- Its obsolete bracket-style completion format has been downgraded to a historical example.
- Owner-document migration blockers from report `003` were handled by reports `004` and `005`.
- No current evidence that `AGENTS_FULL.md` must remain at repository root after active inbound links are updated.

## Recommended Archive Path
- `docs/archive/AGENTS_FULL.md`

Reason:
- `docs/archive/` already exists.
- `AGENTS_FULL.md` is a project-level historical/reference document, not a standard-specific document.
- A direct path under `docs/archive/` keeps future references simple.

## Required Follow-up Changes
- Future archive move task should minimally:
  - move `AGENTS_FULL.md` to `docs/archive/AGENTS_FULL.md`;
  - update `AGENTS.md` references from `AGENTS_FULL.md` to `docs/archive/AGENTS_FULL.md` or equivalent wording;
  - update `AGENT_TASK_ROUTER.md` references from `AGENTS_FULL.md` to `docs/archive/AGENTS_FULL.md` or equivalent wording;
  - update `docs/PACKAGING.md` owner note if direct path accuracy is desired;
  - run `rg -n "AGENTS_FULL|Detailed Domain Reference|상세 에이전트|전체 규칙" . --glob "*.md"` after the move to confirm no active root-path references remain.

## Task Results

### task 1 결과
- 확인 파일: see `Checked Files`.
- archive readiness 판단: OK for archive move after user approval.
- 남은 blocker: none found for archive readiness. The only required work is link/path update during the move.
- archive move 시 수정 필요 파일:
  - `AGENTS.md`
  - `AGENT_TASK_ROUTER.md`
  - optionally `docs/PACKAGING.md`
- 추천 archive 경로: `docs/archive/AGENTS_FULL.md`
- 다음 작업 프롬프트 방향:
  - "Move `AGENTS_FULL.md` to `docs/archive/AGENTS_FULL.md`, update active inbound references in `AGENTS.md` and `AGENT_TASK_ROUTER.md`, optionally update `docs/PACKAGING.md`, create result report, commit, and push."
- OK/NG: OK

## Verification
- Ran `git status --short` before audit; working tree was clean.
- Ran `git diff --name-only` before report creation; no source diffs.
- Ran inbound reference search:
  - `rg -n "AGENTS_FULL|Detailed Domain Reference|상세 에이전트|전체 규칙" . --glob "*.md"`
- Confirmed existing max report number was `005`; this report uses `006`.
- Did not run tests by request.

## Changed Files
- `result_reports/active/006_audit-agents-full-archive-move-readiness.md`

## Known Risks
- The future move will break root-path references unless `AGENTS.md` and `AGENT_TASK_ROUTER.md` are updated in the same change.
- Historical reports and archived logs will continue to mention `AGENTS_FULL.md`; these should remain historical unless the user requests broader cleanup.

## Scope Compliance
- `AGENTS_FULL.md` archive move: not performed
- `AGENTS_FULL.md`: not modified
- source docs: not modified
- links: not modified
- code/tests/model artifact: not modified
- next archive move phase: not started
- tests: not run

## Commit / Push
- source/docs commit: source change 없음
- report commit: committed separately by `report: record agents full archive move audit`; final hash is reported in terminal/final summary because a commit cannot contain its own final hash.
- pushed branch: `main`
