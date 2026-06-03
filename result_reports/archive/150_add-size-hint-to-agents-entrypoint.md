# Add Size Hint to AGENTS.md Entrypoint

**Goal:** Add an explicit size hint `(~95 lines)` to the `AGENTS.md` entrypoint description to reinforce the lite-entrypoint contract and reduce over-read temptation.

**Scope:** Single-line wording change in `AGENTS.md`.

**Non-goals:** No other document, code, test, or config changes.

---

## Changed Files

- `AGENTS.md`
  - Line 3: Changed "이 문서는 매 작업 시작 시 확인하는 **lite entrypoint**다." to "이 문서는 매 작업 시작 시 확인하는 **lite entrypoint**다 (~95 lines)."

---

## Verification

- `git diff --check` → clean.
- `git diff --name-only` → `AGENTS.md` only.
- No AGENTS_FULL stale references remain in `AGENTS.md`.

---

## Scope Compliance

- Did not modify `AGENT_TASK_ROUTER.md`, `project_log.md`, `project_memory_seed.md`, existing reports, code, tests, or config.

---

## Commit / Push

- Source commit: `0b4029f` — `docs: add size hint to AGENTS.md entrypoint description`
- Report commit: `report: 150 add-size-hint-to-agents-entrypoint`
- Pushed to `work/ui-ux-ssot-adoption`

---

## Project Memory Delta

```yaml
- type: procedure
  topic: AGENTS.md entrypoint size hint
  content: AGENTS.md now explicitly states its line count (~95 lines) in the entrypoint description to reinforce the lite-entrypoint contract and discourage over-read.
  keywords:
    - AGENTS.md
    - lite-entrypoint
    - token-leakage
    - size-hint
    - workflow-cleanup
  assertionStatus: verified
  source: result_reports/active/150_add-size-hint-to-agents-entrypoint.md
```
