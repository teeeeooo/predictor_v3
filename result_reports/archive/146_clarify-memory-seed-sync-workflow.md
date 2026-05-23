# Clarify Memory Seed Sync Workflow

**Goal:** Clarify when `project_memory_seed.md` can be modified and add the `Project Memory Seed Sync Judgment` concept to `AGENT_TASK_ROUTER.md`.

**Scope:**
- Task 1: Update `AGENT_TASK_ROUTER.md` — clarify that seed editing is forbidden during regular source/code/doc work, but allowed during summary lifecycle / explicit memory maintenance with a `Project Memory Seed Sync Judgment` (max 1–2 summary-level entries).
- Task 2: Evaluate `project_log.md` update need. Existing 2026-05-23 entry already covers the summary-level seed entry concept; no modification needed.
- Task 3: Compact report.

**Non-goals:** No code, test, config, seed, summary, or archive changes.

---

## Changed Files

- `AGENT_TASK_ROUTER.md`
  - Project Memory Delta section: replaced "memory seed/index 작성은 lifecycle summary/archive와 섞지 않고 별도 문서 작업으로 수행한다" with "memory seed/index 작성은 일반 source/code/doc 작업과 섞지 않는다" and added explicit `Project Memory Seed Sync Judgment` rules.
  - Lifecycle check headings: added `Project Memory Seed Sync Judgment` alongside `Project Log Sync Judgment`.
  - Lifecycle maintenance steps: added seed sync judgment logic immediately after project_log judgment and before project_log append.

---

## Verification

- `git diff --check` → clean.
- `git diff --name-only` → `AGENT_TASK_ROUTER.md` only.
- `grep` confirmed all new keywords (`Project Memory Seed Sync Judgment`, `update needed`, `not needed`, `summary-level`, `memory maintenance`) appear in `AGENT_TASK_ROUTER.md`.
- `project_log.md` was read for latest entry only (lines 13–27) and determined already covered.

---

## Known Risks

- `Project Memory Seed Sync Judgment` is a new operational concept. If an agent encounters it for the first time, it may need to re-read the router section. This is expected and low-risk.

---

## Scope Compliance

- Did not modify `AGENTS.md`, `project_memory_seed.md`, existing reports/summaries/archives, code, tests, or config.
- Did not split `AGENT_TASK_ROUTER.md`.

---

## Commit / Push

- Source commit: `e05d1ac` — `router: clarify memory seed modification conditions and add Project Memory Seed Sync Judgment`
- Report commit: `report: 146 clarify-memory-seed-sync-workflow`
- Pushed to `work/ui-ux-ssot-adoption`

---

## Project Memory Delta

```yaml
- type: procedure
  topic: memory seed synchronization workflow
  content: AGENT_TASK_ROUTER.md now requires a Project Memory Seed Sync Judgment during summary lifecycle or explicit memory maintenance. Seed may only be updated with 1~2 summary-level entries when judged update needed; regular source/code/doc work must not modify the seed.
  keywords:
    - memory-seed
    - project-memory-delta
    - lifecycle-maintenance
    - AGENT_TASK_ROUTER
    - sync-judgment
  assertionStatus: verified
  source: result_reports/active/146_clarify-memory-seed-sync-workflow.md
```
