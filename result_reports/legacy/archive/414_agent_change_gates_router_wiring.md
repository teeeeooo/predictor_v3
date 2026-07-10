# 414 Agent change gates router wiring

## Goal

Make the new agent change-gate owner discoverable without duplicating its
policy into entrypoint or routing documents.

## Scope

- Added a concise owner link and pending-automation notice to `AGENTS.md`.
- Added shared, coding, and UI route links to `AGENT_TASK_ROUTER.md`.
- Registered the owner in `ACTIVE_DOCUMENTS.md`.
- Marked router links implemented in the owner workflow.
- Added the process-rule milestone decision to `project_log.md`.

## Changed Files

- `AGENTS.md`
- `AGENT_TASK_ROUTER.md`
- `ACTIVE_DOCUMENTS.md`
- `docs/agent_workflows/AGENT_CHANGE_GATES.md`
- `project_log.md`
- `result_reports/active/414_agent_change_gates_router_wiring.md`

## Verification

- Owner links and implementation-status markers located successfully.
- `git diff --check`: OK.
- No code-map regeneration: docs/routing-only change.

## Known Risks

- The staged gate tool and hooks remain intentionally unimplemented.
- Routing activates policy discovery but does not claim automated enforcement.

## Change Gate

```yaml
change_gate:
  new_source: none
  hotspot_delta: none
  code_map_check: not_required
  report_exemption: none
  read_ledger: included
```

Read Ledger:

- `AGENTS.md`: lines 18-40 and 53-80; reason: routing and new-code gate link.
- `AGENT_TASK_ROUTER.md`: lines 36-70, 184-205, and 259-282; reason: shared,
  coding, and UI routes.
- `ACTIVE_DOCUMENTS.md`: lines 22-46; reason: workflow owner inventory.
- `docs/agent_workflows/AGENT_CHANGE_GATES.md`: lines 20-52 and 285-303;
  reason: applicability and implementation status.
- `docs/agent_workflows/PROJECT_LOG_AND_MEMORY.md`: lines 10-31; reason:
  milestone-log update judgment.
- `project_log.md`: lines 538-610; reason: recent related process decisions.
- broad read: none
- repeated read: none

## Commit / Push

- Validation passed; routing docs and report are committed and pushed together.

## Next Action

Implement and test `tools/check_agent_change_gate.py --cached` in a separate
slice.
