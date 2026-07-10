# UI Computer Use Smoke Token Discipline

## Goal

Capture the Arc 14B-2F token-efficiency lesson so future UI / Computer Use
smoke checks stay bounded and run after focused automated guards.

## Scope

- Added a small router reminder that UI / Computer Use smoke follows the UI
  workflow bounded-smoke order.
- Added UI workflow validation guidance for running focused tests first,
  limiting accessibility-tree reads, and rerunning one bounded smoke after a
  source fix.

## Non-goals

- No code changes.
- No test changes.
- No broad workflow rewrite.
- No weakening of required smoke, validation, report, or change-gate rules.

## Changed Files

- `AGENT_TASK_ROUTER.md`
- `docs/agent_workflows/UI_SURFACE_WORKFLOW.md`
- `result_reports/active/694_ui-computer-use-smoke-token-discipline.md`

## Validation

- `git diff --check`: OK
- `git status --short`: expected docs/report changes only before commit
- `python3 -B tools/check_code_structure.py`: not run; docs/report-only change

## Decision

Computer Use smoke remains available when it is the right acceptance evidence,
but the workflow now nudges agents to:

- lock behavior with focused automated checks first;
- run GUI / Computer Use smoke last;
- prefer one state read and the minimum required input/click action;
- convert smoke-discovered source bugs into focused guards before rerunning
  one bounded smoke pass.

## Structure

```yaml
change_gate:
  new_source: none
  hotspot_delta: none
  code_map_check: not_required
  ui_literal_exemption: none
  reuse_commonization: not_required
  report_exemption: none
  read_ledger: included
```

Read Ledger:
- `AGENT_TASK_ROUTER.md`: Smoke / Validation, UI, Agent rule/router sections.
- `docs/agent_workflows/UI_SURFACE_WORKFLOW.md`: Validation section.

## Next Action

Use the bounded-smoke order in the next UI / Computer Use task.

## Commit / Push

Final commit/push result will be reported in terminal output.

## Project Memory Delta

- Future UI smoke should avoid repeated Computer Use AX tree reads unless they
  are the specific acceptance evidence.
