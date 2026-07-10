# Cleanup Router Token Hardening Examples

**Goal:** Fix leftover wording from the previous token-leakage hardening pass in `AGENT_TASK_ROUTER.md`: qualify Quick Route Index `rg` patterns with the target filename, and localize the `modified:` group summary example.

**Scope:**
- Task 1: Append `AGENT_TASK_ROUTER.md` to all `rg` pattern examples in the Quick Route Index so they do not search the whole repo.
- Task 2: Replace the English shorthand `details in report` with the Korean expression `상세 경로는 report에 기록` in the `modified:` group summary example.

**Non-goals:** No code, test, config, seed, `project_log.md`, summary, or archive changes. No route meaning changes.

---

## Changed Files

- `AGENT_TASK_ROUTER.md`
  - Quick Route Index: added `AGENT_TASK_ROUTER.md` to all 15 `rg` pattern rows.
  - Result Report Workflow `modified:` group summary example: changed `details in report` → `상세 경로는 report에 기록`.

---

## Verification

- `git diff --check` → clean.
- `git diff --name-only` → `AGENT_TASK_ROUTER.md` only.
- `grep` verification confirmed all `rg` patterns now end with `AGENT_TASK_ROUTER.md` and `details in report` no longer appears in the file.

---

## Scope Compliance

- Did not modify `AGENTS.md`, `project_log.md`, `project_memory_seed.md`, existing reports/summaries/archives, code, tests, or config.
- Did not split `AGENT_TASK_ROUTER.md` or add line numbers.

---

## Commit / Push

- Source commit: `9800c31` — `router: qualify rg patterns with filename and localize modified group summary example`
- Report commit: `report: 145 cleanup-router-token-hardening-examples`
- Pushed to `work/ui-ux-ssot-adoption`

---

## Project Memory Delta

```yaml
- type: procedure
  topic: agent workflow token leakage hardening wording cleanup
  content: Quick Route Index rg patterns in AGENT_TASK_ROUTER.md now explicitly include the target filename to avoid repo-wide searches, and the modified group summary example uses Korean expression instead of English shorthand.
  keywords:
    - token-leakage
    - workflow-hardening
    - AGENT_TASK_ROUTER
    - wording-cleanup
    - quick-route-index
  assertionStatus: verified
  source: result_reports/active/145_cleanup-router-token-hardening-examples.md
```
