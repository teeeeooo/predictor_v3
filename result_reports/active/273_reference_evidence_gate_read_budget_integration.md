# 273 Reference Evidence Gate Read-Budget Integration

## Goal

Integrate the code_checker reference map into the agent workflow as a
conditional pre-write evidence gate, without inflating token/read budgets.

## Scope

- Add Reference Evidence Gate section to
  `docs/agent_workflows/DIFF_READ_BUDGET.md`.
- Add minimal cross-references in `AGENT_TASK_ROUTER.md` (Shared Guardrails,
  Coding route, UI route).
- Update `docs/WORK_PLAN.md` next action.
- Update `project_log.md` with durable workflow decision.

## Excluded Scope

- `tools/code_checker/` logic changes.
- `docs/code_map/CODEBASE_REFERENCE_MAP.md` regeneration.
- `tests` changes.
- `.gitignore` changes.
- ui_tk cleanup or controller switch (not started).

## Why DIFF_READ_BUDGET.md Owns This

`DIFF_READ_BUDGET.md` already owns token/read discipline for document, diff,
and code inspection. The Reference Evidence Gate is fundamentally a read-budget
gate: it tells an agent when to run code_checker and how to read the map without
broad-read explosion. Keeping the gate in the read-budget owner prevents
duplication and keeps the router lean.

## Reference Evidence Gate Trigger Policy

**Default: OFF.** Run only when the task creates, moves, splits, replaces, or
commonizes code surfaces:

- new helper / adapter / controller / table surface / result formatter /
  workflow script
- file move / split / delete / replacement
- result / detail / export / table / window commonization
- new profile UI / calculator section
- adding responsibility to a known hotspot file

**Skip** for work that does not change structure or surface inventory:
- report closeout / lifecycle maintenance
- project_log / WORK_PLAN wording
- Windows smoke result reflection
- focused test expectation correction
- fixture / golden value-only update
- typo / formatting-only change

## Map Read / Regenerate / Commit Policy

- **Read**: targeted `rg` + 30–80 line `sed` range. No broad map reads.
- **Regenerate**: only after structural code changes (new/moved/removed files or
  symbols).
- **Commit**: only after significant architecture or surface changes. No
  map-only noise commits.
- **Caveat**: map is evidence, not source of truth.

## Router Cross-Reference

- **Shared Guardrails**: added one-line conditional note linking to
  DIFF_READ_BUDGET.md Reference Evidence Gate for structure-impacting work.
- **Section 3 (Coding)**: step 5 added — new helper/adapter/surface or
  file split/move triggers the gate.
- **Section 8 (UI)**: step 5 added — new table/window/detail/export surface
  or helper/commonization triggers the gate.

No long trigger lists were duplicated in the router.

## WORK_PLAN / project_log Updates

- `docs/WORK_PLAN.md`: next action updated from "Reference evidence gate hook
  policy adoption" to "ui_tk cleanup preflight or main table migration
  candidate check using Reference Evidence Gate."
- `project_log.md`: durable decision recorded — code_checker default OFF,
  conditional ON for structure-impacting work; DIFF_READ_BUDGET.md owns the
  gate.

## Validation

| Check | Command | Result |
|-------|---------|--------|
| Git diff check | `git diff --check` | Clean |
| Git status | `git status --short` | Only expected files modified |

No pytest, py_compile, structure guard, or map regeneration were run (this is
a documentation/workflow-only change).

## Modified Files

- `docs/agent_workflows/DIFF_READ_BUDGET.md`
- `AGENT_TASK_ROUTER.md`
- `docs/WORK_PLAN.md`
- `project_log.md`

## Next

- ui_tk cleanup preflight or main table migration candidate check using
  Reference Evidence Gate.
