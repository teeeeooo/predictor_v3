# 275 Code Quality Guardrail Backlog Milestone Registration

## Goal

Register remaining code quality guardrail candidates as a tracked backlog so
they are not forgotten after the 270~274 code_checker and workflow integration
work.

## Scope

- Add "Code quality guardrail backlog" section to `docs/REFACTOR_PLAN.md`.
- Add short checkpoint reminder to `docs/WORK_PLAN.md` Deferred / Hold.
- Add durable decision to `project_log.md`.

## Excluded Scope

- No code changes.
- No test changes.
- No tools changes.
- No new design documents.

## Target Doc Decision (Task 1)

- **Detailed backlog**: `docs/REFACTOR_PLAN.md` (owner for refactor candidates)
- **Reminder/checkpoint**: `docs/WORK_PLAN.md` (execution board)
- **Durable decision**: `project_log.md`
- **No change**: `ACTIVE_DOCUMENTS.md`, `PROJECT_CHARTER.md`, `AGENTS.md`,
  `AGENT_TASK_ROUTER.md`, `DIFF_READ_BUDGET.md`

## REFACTOR_PLAN Update (Task 2)

Added `### 6. Code quality guardrail backlog` to `docs/REFACTOR_PLAN.md`:

**Warning-first candidates** (introduce one at a time):
- broad `except` / `pass` / silent fallback smell warning
- re-export / compatibility wrapper inventory
- complexity / max-depth / long-function warning
- import cycle detector
- fan-in / fan-out summary

**Later candidates**:
- strict type checker adoption (mypy / pyright)
- mock boundary audit for headless-vs-GUI tests

**Policy**:
- Do not implement all gates at once.
- Owner per check type: `tools/code_checker/` for semantic map-based checks,
  `tools/check_code_structure.py` for structural AST checks.
- Revisit after ui_tk cleanup and controller switch are complete.

## WORK_PLAN Reminder (Task 3)

Added to `Deferred / Hold`:
- "Code quality guardrail backlog is tracked in `docs/REFACTOR_PLAN.md`;
  revisit after ui_tk cleanup / controller switch slices expose real checker needs."

## project_log Decision (Task 4)

Added durable decision:
- REFACTOR_PLAN.md owns detailed guardrail backlog.
- WORK_PLAN.md keeps a short checkpoint.
- Guardrails introduced incrementally, warning-first, not as immediate hard gates.
- Owner: semantic check → `tools/code_checker/`, structural check → `tools/check_code_structure.py`.
- Revisit after ui_tk cleanup and controller switch.

## Validation

| Check | Command | Result |
|-------|---------|--------|
| Git diff check | `git diff --check` | Clean |
| Git status | `git status --short` | Only expected files modified |

## Modified Files

- `docs/REFACTOR_PLAN.md`
- `docs/WORK_PLAN.md`
- `project_log.md`

## Next

- Extract section-level result formatting helpers (274 preflight recommendation).
