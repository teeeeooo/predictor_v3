# Workflow Token Leakage Audit

**Goal:** Identify points in the current agent workflow where token overuse may occur, especially around document reading habits, duplicate rules, and lifecycle artifacts.

**Scope:** Audit `AGENTS.md`, `AGENT_TASK_ROUTER.md`, `ACTIVE_DOCUMENTS.md`, `project_log.md`, `result_reports/memory/project_memory_seed.md`, active reports, and summaries for token leakage patterns.

**Non-goals:** No code, test, config, or existing document body is modified. No archive/summary lifecycle maintenance is performed. No backend integration is proposed.

---

## Likely Token Leakage Sources

### 1. `AGENT_TASK_ROUTER.md` as a single 642-line file
- The document contains all task routes, guardrails, result report workflow, lifecycle rules, and documentation sync gates in one file.
- The routing rule says "해당 유형에 필요한 문서만 읽는다" and "해당 섹션만 확인한다", but because it is a single flat Markdown file, an agent must either read the whole file or perform precise `grep`/`rg` navigation.
- **Leakage risk:** An agent that reads the file sequentially from the top will ingest ~170 lines of Result Report Workflow, ~90 lines of Lifecycle check rules, and ~370 lines of task-specific routes even when only one route is needed.
- **Estimated tokens per unnecessary full read:** ~10–15k tokens (Korean text, dense formatting).

### 2. `project_log.md` append-only growth (1,361 lines)
- The policy correctly restricts reading to "최근 2~3개 로그만 확인" when appending.
- However, the file has grown to 1,361 lines. To find the latest 2–3 headings, an agent must scan or skip past 1,300+ lines of historical logs.
- **Leakage risk:** If an agent uses `read` without `offset`, or if `grep`/`sed` navigation is imprecise, the entire file can be ingested habitually.
- **Estimated tokens per accidental full read:** ~20–30k tokens.

### 3. `result_reports/archive/` size (1.2 MB, 132 files)
- The archive directory contains 132 files and 1.2 MB of content.
- The guardrail says "seed 확인을 이유로 archive/report 전문을 대량으로 읽지 않는다."
- **Leakage risk:** This is a catastrophic token sink if any tool call or script accidentally globs `result_reports/**/*.md` or lists archive contents with content.
- **Mitigation:** The directory is excluded from `ACTIVE_DOCUMENTS.md` scope, but there is no hard guard at the tool-call level.

### 4. `project_memory_seed.md` monolithic growth (395 lines, 32 entries)
- The seed has good search-first instructions (`rg -n` then `sed -n`).
- But it is a single file with 32 YAML entries. As summaries continue to be produced, this file will grow linearly.
- **Leakage risk:** Over time, even a "relevant entry" read may require parsing through 50–100 entries. If an agent ever falls back to "read the whole file", the cost grows with each new summary cycle.

### 5. Full Report Mode template verbosity
- Full report requires 10+ mandatory sections (Goal, Scope, Non-goals, Verification, Task Results, Test Results, Changed Files, Known Failures/Risks, Next Suggested Action, Scope Compliance, Commit/Push, Project Memory Delta).
- **Leakage risk:** This is an *output-side* token cost. Every full-report task consumes tokens to generate these sections, even when the actual code change is small. While this does not affect *input* token reading, it increases the total session cost and may incentivize agents to over-explain.

---

## Safe Existing Guardrails

| Guardrail | Effectiveness |
|-----------|---------------|
| `AGENTS.md` kept small (95 lines) | High — lite entrypoint works as intended |
| "기본 작업 시작 시 `AGENTS.md`만 필수로 읽는다" | High — prevents mandatory reading of large docs |
| Memory seed search-first (`rg -n`, `sed -n`) | High — prevents full seed reads when followed |
| Routine lifecycle check = metadata-only | High — prevents reading active report bodies |
| No-report / terminal-only mode | High — skips report generation entirely for simple queries |
| Compact report mode | Medium-High — reduces output bloat, but the template is still defined inside the large router file |
| Archive excluded from `ACTIVE_DOCUMENTS.md` | Medium — reduces accidental active references |
| `project_log.md` — "report 본문을 복사하지 않는다" | High — prevents log bloat from duplication |

---

## Over-read Risks

### Risk A: `"해당 섹션만 확인한다"` vs. single-file reality
- `AGENT_TASK_ROUTER.md` has no per-section file split. The instruction to read only the relevant section assumes the agent can navigate by heading. In practice, LLM-based agents often `read` the whole file to "be safe."
- **Severity:** Medium. Happens on most non-trivial tasks.

### Risk B: `project_log.md` — "최근 2~3개" requires context
- An agent must know *where* the latest entries are. Without a helper script or index, the agent must `grep` for date headings and then `read` with `offset`. This is more steps than a simple `read`, creating friction that may push agents toward just reading the file.
- **Severity:** Medium. The file is already 1,361 lines.

### Risk C: `ACTIVE_DOCUMENTS.md` referenced in two places
- `AGENTS.md` says: "문서 업데이트 범위가 둘 이상이면 먼저 `ACTIVE_DOCUMENTS.md`에서..."
- `AGENT_TASK_ROUTER.md` says the same thing in the Documentation Sync gate.
- An agent doing a doc update may read both references and then read `ACTIVE_DOCUMENTS.md` twice, or read it once plus the surrounding routing text twice.
- **Severity:** Low. The file is only 131 lines, but the duplication creates confirmation bias to read it.

### Risk D: Lifecycle rules interleaved with task routes
- The Result Report Workflow (lines 92–260) and Lifecycle check (lines 224–254) are inside the same file as task routes. An agent looking up "how do I write a report?" must navigate through or read task routes it doesn't need.
- **Severity:** Low-Medium.

---

## Duplicate Rule Risks

The following rules appear in **both** `AGENTS.md` and `AGENT_TASK_ROUTER.md` Shared Guardrails. This duplication is intentional (lite entrypoint vs. detailed owner), but it doubles the token exposure when both files are read:

1. Train/Predict separation (`app_train.py` / `app_predict.py`)
2. `core/predictor.py` import restrictions (`optuna`, `sklearn`, `shap`, `matplotlib`)
3. `COLUMNS` → `core/constants.py`, `MODEL_REGISTRY` → `core/models.py`
4. Pure Python calculator (no `numpy` / `pandas`)
5. `calculate_hspf2_v2()` / `calculate_hspf2()` modification restriction
6. `model.fit()` `.values` restriction + Cooling/Heating model separation
7. UI table pattern (`QTableView` + `QAbstractTableModel` + `QStyledItemDelegate`)
8. `QTableWidget` / `setCellWidget` ban
9. Excel-like behavior requirements (Ctrl+C TSV, etc.)
10. 함수명/JSON key/public API/diagnostics schema 변경 금지
11. region config / HW candidate / ML feature / calculator result schema mixing ban
12. `ACTIVE_DOCUMENTS.md` check for multi-doc updates
13. `docs/archive/AGENTS_FULL.md` conditional read
14. `data/region_configs/*.json` → `REGION_CONFIG_RULES.md` check
15. `*_notes.md` → `DOCS_GUIDELINES.md` / `STANDARD_DOC_TEMPLATE.md` check

**Assessment:** The duplication is architecturally justified (entrypoint vs. owner), but for tasks that legitimately need both files, ~15 rules are read twice. There is no deduplication mechanism.

---

## Immediate Low-risk Fix Candidates

### Fix 1: Add `wc -l` / directory-size helper to `AGENTS.md` or `AGENT_TASK_ROUTER.md`
- **What:** In the memory seed / project_log / archive reading instructions, add a one-line reminder: "먼저 `wc -l <file>` 또는 `du -sh <dir>`로 규모를 확인하고 제한 범위만 읽는다."
- **Why:** The current instructions say "제한적으로 확인한다" but do not explicitly tell the agent to check file size first. Adding `wc -l` as a mandatory pre-step reduces accidental full reads.
- **Risk:** Very low. Purely additive wording.
- **Tokens saved:** Prevents accidental full reads of 1,361-line `project_log.md` or 395-line `project_memory_seed.md`.

### Fix 2: Split `AGENT_TASK_ROUTER.md` table of contents into a quick-reference index
- **What:** Add a 10–15 line "Quick Route Index" at the top of `AGENT_TASK_ROUTER.md` mapping task types to line ranges or headings.
- **Why:** Currently the agent must `grep` for headings or read sequentially. A visible index reduces the need to scan the whole file.
- **Risk:** Very low. Does not change any rule text.
- **Tokens saved:** Reduces navigation reads by ~50% for targeted tasks.

### Fix 3: Add `tail -n` / `grep` helper for `project_log.md` latest entries
- **What:** Change the instruction from "최근 2~3개 로그만 확인한다" to a concrete tool call: "`grep -n '^## ' project_log.md | tail -n 3`로 최신 heading 위치를 확인한 뒤 `read` offset로 제한한다."
- **Why:** The current rule is vague. Concrete tooling reduces the friction that pushes agents toward reading the whole file.
- **Risk:** Very low. Wording clarification only.
- **Tokens saved:** Prevents full reads of 1,361-line file.

---

## Do-not-touch / Keep as-is

| Item | Reason |
|------|--------|
| `AGENTS.md` content | It is intentionally small and serves as the lite entrypoint. Expanding it would defeat its purpose. |
| `AGENTS.md` → `AGENT_TASK_ROUTER.md` routing split | This is a correct architectural boundary. Merging them would create a single massive mandatory-read file. |
| Rule duplication between `AGENTS.md` and `AGENT_TASK_ROUTER.md` | Justified — lite entrypoint needs standalone guardrails even if the router is not read. |
| `project_memory_seed.md` single-file staging | Backend-neutral staging is correct; splitting into per-summary seeds would complicate the search workflow without clear token savings. |
| Archive / summary / active directory structure | The lifecycle separation is correct. Moving files would not reduce token leakage. |
| `Project Memory Delta` schema | The YAML list format and backend-neutral design are correct. Changing the schema would be high-impact. |
| Full report mode template | Full mode is needed for complex changes. Compact mode already addresses simple changes. |
| `project_log.md` append-only policy | Correct for audit trail. The growth issue is a read-side problem, not a write-side problem. |

---

## Recommended Next 3 Tasks

All three tasks are low-risk, report-only or wording-only, and have similar impact scope (read-side workflow optimization without structural change).

### Task A: Add file-size pre-check reminder to document reading rules
- **Scope:** `AGENTS.md` and/or `AGENT_TASK_ROUTER.md` — add `wc -l` / `du -sh` pre-check reminder to `project_log.md`, `project_memory_seed.md`, and archive reading instructions.
- **Impact:** Prevents accidental full-file reads.
- **Verification:** `grep` for `wc -l` in the updated files.

### Task B: Add concrete `project_log.md` navigation command to the router
- **Scope:** `AGENT_TASK_ROUTER.md` — replace "최근 2~3개 로그만 확인한다" with a concrete `grep | tail` + `read offset` recipe.
- **Impact:** Removes ambiguity that causes over-read.
- **Verification:** `grep` for `tail -n` or `grep -n '^## '` in the router file.

### Task C: Add a quick route index to `AGENT_TASK_ROUTER.md`
- **Scope:** `AGENT_TASK_ROUTER.md` — add a 10–15 line heading→line-number or heading→task-type index at the top.
- **Impact:** Reduces need to scan the full 642-line file.
- **Verification:** Read the first 20 lines and confirm the index exists.

---

## Verification

- Existing documents were **not modified** during this audit.
- Archive report bodies were **not read**.
- `result_reports/archive/` was only queried for file count and total size (`du -sh`, `find | wc -l`).
- `project_memory_seed.md` was read only for the header, purpose, scope, and entry count (first 40 lines). Entry content was not read in depth.
- `project_log.md` was read only for the policy header (first 15 lines) and latest 2 headings (next ~50 lines). Historical log bodies were not read.
- `AGENT_TASK_ROUTER.md` was read for the header, Shared Guardrails, Project Memory Recall Gate, Result Report Workflow, Documentation Sync & Lifecycle Gate, and the first task route section. Remaining task routes (lines 270–642) were not read.

---

## Known Risks

- If `project_log.md` continues to grow at the current rate (~200–300 lines per week), the "최근 2~3개" navigation cost will increase. A future high-impact but low-risk fix could be to split `project_log.md` into monthly or quarterly files, but this was deliberately excluded from the immediate fix candidates because it touches the write-side lifecycle.
- If `project_memory_seed.md` reaches 100+ entries, even keyword-based reads may require scanning more context. Consider a future `grep`-first reminder reinforcement.

---

## Project Memory Delta

```yaml
- type: open_question
  topic: agent workflow token leakage
  content: Can the current agent workflow's read-side token costs be further reduced without splitting the canonical `AGENTS.md` / `AGENT_TASK_ROUTER.md` boundary, by adding concrete `wc -l`, `grep | tail`, and offset-based `read` instructions to the existing rules?
  keywords:
    - token-leakage
    - workflow-audit
    - agent-rules
    - over-read-risk
    - document-size-guard
  assertionStatus: inferred
  source: result_reports/active/143_audit-workflow-token-leakage.md
```
