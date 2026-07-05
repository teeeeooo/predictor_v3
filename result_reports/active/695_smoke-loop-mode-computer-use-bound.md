# Smoke Loop Mode Computer Use Bound

## Goal

Align `SMOKE_LOOP_MODE.md` with the new bounded Computer Use / GUI smoke
discipline added to the UI workflow.

## Scope

- Added smoke-loop guidance to run focused owner tests before GUI actions when
  practical.
- Limited Computer Use / onscreen smoke loops to one bounded state read and the
  minimum keyboard/click action needed.
- Clarified that smoke-discovered source bugs should get a focused guard before
  one bounded re-smoke.

## Non-goals

- No source code changes.
- No test changes.
- No broad workflow rewrite.

## Validation

- `git diff --check`: OK
- `git status --short`: expected docs/report changes only before commit

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
- `docs/agent_workflows/SMOKE_LOOP_MODE.md`: Rules section.
- `ACTIVE_DOCUMENTS.md`: confirmed owner role from search output.

## Next Action

Use `SMOKE_LOOP_MODE.md` together with `UI_SURFACE_WORKFLOW.md` for future
manual UI smoke-loop micro-fixes.

## Commit / Push

Final commit/push result will be reported in terminal output.
