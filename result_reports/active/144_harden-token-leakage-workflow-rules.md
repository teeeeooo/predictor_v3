# Harden Token Leakage Workflow Rules

**Goal:** Add low-risk read-side and output-side hardening rules to `AGENT_TASK_ROUTER.md` based on the token leakage audit.

**Scope:**
- Task 1: Allow group summaries in terminal `modified:` line for bulk file changes, with details kept in the report.
- Task 2: Add concrete `wc -l` / `du -sh` pre-check and `rg -n "^## "` navigation commands before reading large docs (`project_log.md`, `project_memory_seed.md`, archive).
- Task 3: Add a `rg`-pattern-based Quick Route Index at the top of `AGENT_TASK_ROUTER.md`.

**Non-goals:** No code, test, config, seed, `project_log.md`, summary, or archive changes. No router file split.

---

## Changed Files

- `AGENT_TASK_ROUTER.md`
  - Added `### Quick Route Index` (heading + `rg` pattern table, no line numbers) immediately under `## Task Routing Rules`.
  - Expanded Shared Guardrails line 26: added `wc -l <file>` / `du -sh <dir>` pre-check before `rg`/`grep -n` / `sed -n` reads.
  - Expanded `modified:` writing rules in Result Report Workflow: added group summary examples and the requirement to keep detailed paths in the report's Changed Files / Archive Candidates / Verification sections.
  - Expanded Project Memory Recall Gate: added `wc -l` pre-check for `project_memory_seed.md` and a guard that `result_reports/archive/` is checked by `find`/filename/heading only by default.
  - Expanded Commit / Git 정리 conditional read: added `rg -n "^## " project_log.md | tail -n 5` navigation example.
  - Expanded Documentation Sync & Lifecycle Gate `project_log.md` section: added the same concrete heading navigation command.

---

## Verification

- `git diff --check` → clean (no whitespace errors).
- `git diff --name-only` → `AGENT_TASK_ROUTER.md` only.
- `grep` verification confirmed all added keywords (`Quick Route Index`, `wc -l`, `du -sh`, `rg -n "^## "`, `modified:`, `details in report`, `active→archive`, `result_reports/archive`) appear in the file.
- No existing rule priority or meaning was changed.

---

## Known Risks

- The Quick Route Index uses `rg` patterns. If `rg` is unavailable, `grep -n` can be substituted. This is already covered by existing fallback language in Shared Guardrails.
- Group summary examples use bash brace expansion (`{133..139}`). This is terminal shorthand and does not affect report accuracy, since detailed paths are still required inside the report.

---

## Scope Compliance

- Did not modify `AGENTS.md`, `project_log.md`, `project_memory_seed.md`, existing reports/summaries/archives, code, tests, or config.
- Did not split `AGENT_TASK_ROUTER.md`.
- Did not introduce MCP/backend integration.

---

## Commit / Push

- Source commit: `3c31fc2` — `router: add quick route index, file-size pre-check, and modified group summary rules`
- Report commit: `report: 144 harden-token-leakage-workflow-rules`
- Pushed to `work/ui-ux-ssot-adoption`

---

## Project Memory Delta

```yaml
- type: procedure
  topic: agent workflow token leakage hardening
  content: AGENT_TASK_ROUTER.md now requires wc -l/du -sh size checks before reading large documents, rg-based heading navigation for project_log.md, find/heading-only checks for result_reports/archive by default, and allows group summaries in terminal modified lines when bulk file changes occur, provided detailed paths remain in the report.
  keywords:
    - token-leakage
    - workflow-hardening
    - agent-rules
    - AGENT_TASK_ROUTER
    - over-read-prevention
  assertionStatus: verified
  source: result_reports/active/144_harden-token-leakage-workflow-rules.md
```
