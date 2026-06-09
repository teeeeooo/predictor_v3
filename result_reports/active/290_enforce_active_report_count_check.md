# 290 Enforce Active Report Count Check in Agent Output Workflow

## Goal

Ensure report-backed tasks check the active report count before final output and commit/push, exposing the existing RESULT_REPORT_WORKFLOW.md rule through AGENTS.md and AGENT_TASK_ROUTER.md.

## Scope

- `AGENTS.md`: Output section adds a short active-count-check line for report-backed commit/push tasks.
- `AGENT_TASK_ROUTER.md`: Result Report Workflow adds an active report count command example; Commit/Git section adds the check as a step.
- `docs/agent_workflows/RESULT_REPORT_WORKFLOW.md`: Adds the active report count command example next to the existing >10 threshold rule.

## Rule Gap

- `RESULT_REPORT_WORKFLOW.md` already had a clear rule: before commit/push of a report-backed task, check `result_reports/active/` count; if >10, do not auto-run lifecycle maintenance, and add a pending note.
- `AGENTS.md` Output did not reference this check directly.
- `AGENT_TASK_ROUTER.md` referenced the rule but did not include a concrete command or enforce it as a Commit step.
- In 288/289, the check was skipped because the prompt did not include the command, the agent did not read `RESULT_REPORT_WORKFLOW.md`, and the existing router wording was too indirect.

## Changes

### AGENTS.md

Added after the terminal output shape:

> report-backed 작업에서 commit/push를 수행할 때는 최종 보고 전 `result_reports/active/` 파일 수를 확인한다. 기준과 행동은 `docs/agent_workflows/RESULT_REPORT_WORKFLOW.md` Commit/Push를 따른다.

### AGENT_TASK_ROUTER.md

Result Report Workflow:

> active report 수 확인: `find result_reports/active -maxdepth 1 -type f -name '*.md' | wc -l`

Commit / Git 정리:

Added step 4:

> report-backed task이면 최종 보고/커밋 전 active report count 확인 (`find result_reports/active -maxdepth 1 -type f -name '*.md' | wc -l`)

### RESULT_REPORT_WORKFLOW.md

Added after the >10 threshold rule:

> Active report count command: `find result_reports/active -maxdepth 1 -type f -name '*.md' | wc -l`

## Excluded Scope

- No active report summary/archive cleanup performed.
- No code or test changes.
- No docs/REFACTOR_PLAN.md change.
- No result_reports/active file moves.

## Validation

| Check | Command | Result |
|-------|---------|--------|
| Git diff check | `git diff --check` | Clean |
| Git status | `git status --short` | 3 files modified |

## Active Report Count

Current active report count: **29** (>10 threshold).

Lifecycle maintenance is pending and should be handled as a separate follow-up.

## Next

- Post-focus-preservation Windows smoke for invalid text undo (from 288/289).
- Active report lifecycle cleanup follow-up when count remains >10.
