# Cleanup AGENTS_FULL Stale References

**Goal:** Remove stale `docs/archive/AGENTS_FULL.md` read instructions from active workflow documents.

**Scope:**
- Task 1: Update `AGENTS.md`, `AGENT_TASK_ROUTER.md`, and `docs/PACKAGING.md` to remove or replace AGENTS_FULL references with active owner docs / `ACTIVE_DOCUMENTS.md`.
- Task 2: Evaluated `project_log.md` — existing 2026-05-23 entry covers process-rule changes; AGENTS_FULL cleanup is docs wording cleanup, no update needed.
- Task 3: Compact report.

**Non-goals:** No project_log.md, project_memory_seed.md, archived reports, code, test, or config changes.

---

## Changed Files

- `AGENTS.md`
  - Line 5: Replaced "상세 배경은 ... `docs/archive/AGENTS_FULL.md`에서 제한적으로 확인한다" with "상세 배경은 작업 유형에 맞는 active owner docs와 `ACTIVE_DOCUMENTS.md`를 필요한 범위만 확인한다."
- `AGENT_TASK_ROUTER.md`
  - Shared Guardrails > 문서 경계: Removed AGENTS_FULL conditional read instruction.
  - Commit/Git 정리 > 읽지 말 것: Removed AGENTS_FULL line.
  - Logic 수정/계산 엔진 수정 > 읽지 말 것: Removed AGENTS_FULL line.
  - 단순 docs 문구 수정 > 읽지 말 것: Removed AGENTS_FULL line.
  - Agent rule/router 수정 > 읽지 말 것: Removed AGENTS_FULL line.
  - Packaging/배포 빌드 > 조건부로 읽을 문서 + 읽지 말 것: Removed both AGENTS_FULL lines.
- `docs/PACKAGING.md`
  - Line 5: Replaced "`docs/archive/AGENTS_FULL.md`에 남아 있던 packaging 상세 규칙의 owner 문서다" with "기존 packaging 상세 규칙은 `AGENT_TASK_ROUTER.md` §10 Packaging / 배포 빌드와 `project_log.md`에서 관리한다."

---

## Verification

- `grep -rn "AGENTS_FULL\|docs/archive/AGENTS_FULL.md" AGENTS.md AGENT_TASK_ROUTER.md docs/PACKAGING.md` → no matches.
- `git diff --check` → clean.
- `git diff --name-only` → `AGENTS.md`, `AGENT_TASK_ROUTER.md`, `docs/PACKAGING.md`.
- `project_memory_seed.md` and `project_log.md` were not modified.

---

## Scope Compliance

- Did not modify archived reports, `project_memory_seed.md`, `project_log.md`, code, tests, or config.
- Did not split `AGENT_TASK_ROUTER.md`.

---

## Commit / Push

- Source commit: `a0700b0` — `docs: remove stale AGENTS_FULL references from active workflow documents`
- Report commit: `report: 149 cleanup-agents-full-stale-references`
- Pushed to `work/ui-ux-ssot-adoption`

---

## Project Memory Delta

```yaml
- type: procedure
  topic: AGENTS_FULL stale reference removal
  content: AGENTS_FULL.md is no longer referenced as an active conditional read source in AGENTS.md, AGENT_TASK_ROUTER.md, or docs/PACKAGING.md. Detailed background checks now route through active owner docs and ACTIVE_DOCUMENTS.md instead.
  keywords:
    - AGENTS_FULL
    - stale-reference
    - workflow-cleanup
    - active-docs
    - AGENT_TASK_ROUTER
  assertionStatus: verified
  source: result_reports/active/149_cleanup-agents-full-stale-references.md
```
