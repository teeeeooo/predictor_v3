# Add Memory Seed Maintenance Policy

**Goal:** Add a `Memory Seed Maintenance Policy` to `AGENT_TASK_ROUTER.md` and update `result_reports/memory/project_memory_seed.md` Next Maintenance Rule to align with it.

**Scope:**
- Task 1: Add Memory Seed Maintenance Policy to `AGENT_TASK_ROUTER.md` — covers importance/supersession/resolutionStatus adjustment rules, stale marking, threshold-based audit, and minimal update principle.
- Task 2: Update `project_memory_seed.md` Next Maintenance Rule to reflect Project Memory Seed Sync Judgment-based updates, stale/superseded marking, and 50/75 entry thresholds.
- Task 3: Evaluated `project_log.md` — existing 2026-05-23 entry already covers summary-level seed entry concept; no update needed.
- Task 4: Compact report.

**Non-goals:** No code, test, config, existing report/summary/archive changes, seed entry body rewrites.

---

## Changed Files

- `AGENT_TASK_ROUTER.md`
  - Added `#### Memory Seed Maintenance Policy` under Project Memory Delta section.
  - Covers: importance/supersession/resolutionStatus adjustment only during summary lifecycle or memory maintenance; importance levels (low/normal/high/critical); stale/superseded/resolved/rejected marking instead of deletion; supersedes usage; importance promotion for frequently reused entries; 50-entry audit threshold and 75-entry mandatory maintenance threshold; minimal update principle.
- `result_reports/memory/project_memory_seed.md`
  - Updated `Next Maintenance Rule` section: now references `Project Memory Seed Sync Judgment`; allows 1–2 summary-level entry additions; uses supersedes/resolutionStatus for replaced entries; stale/superseded/retired marking instead of deletion; 50/75 entry thresholds.
  - Fixed `Known Gaps` line to generalize "through reports `139`" → "through the listed summaries".

---

## Verification

- `git diff --check` → clean.
- `git diff --name-only` → `AGENT_TASK_ROUTER.md`, `result_reports/memory/project_memory_seed.md`.
- `grep` confirmed all new policy keywords present in both files.
- `project_log.md` was read for latest entry only (lines 13–27) and determined already covered.

---

## Known Risks

- The 50/75 entry thresholds are soft operational limits, not hard-enforced guards. Future memory maintenance tasks will need to count entries manually.

---

## Scope Compliance

- Did not modify `AGENTS.md`, existing reports/summaries/archives, code, tests, or config.
- Did not split `AGENT_TASK_ROUTER.md`.
- Did not rewrite seed entry bodies.

---

## Commit / Push

- Source commit: `03b4c6c` — `router+seed: add memory seed maintenance policy and update Next Maintenance Rule`
- Report commit: `report: 147 add-memory-seed-maintenance-policy`
- Pushed to `work/ui-ux-ssot-adoption`

---

## Project Memory Delta

```yaml
- type: procedure
  topic: memory seed maintenance policy
  content: AGENT_TASK_ROUTER.md now defines a Memory Seed Maintenance Policy limiting seed edits to summary lifecycle or explicit memory maintenance, specifying importance levels, stale/superseded marking instead of deletion, supersedes usage, and 50/75 entry thresholds for audit triggers. result_reports/memory/project_memory_seed.md Next Maintenance Rule is aligned with this policy.
  keywords:
    - memory-seed
    - maintenance-policy
    - token-leakage
    - AGENT_TASK_ROUTER
    - project-memory-seed
  assertionStatus: verified
  source: result_reports/active/147_add-memory-seed-maintenance-policy.md
```
