# 460 Enforce Profile Lifecycle Owner Gate

## Goal

Prevent migrated calculator profile tabs from reintroducing direct lifecycle
primitive assembly and formally register the common lifecycle package.

## Result

- Registered `apps/calculator/ui/lifecycle/` in the calculator UI package owner
  registry.
- Added a focused AST structure rule for production `tabs/*.py`.
- The rule rejects direct calls to `TkVisibleContentMeasurement`,
  `TkContentHuggingShell`, `DynamicContentRefitScheduler`, and
  `register_content`.
- The lifecycle controller package and tests remain allowed; view event binding
  and common controller construction are not over-blocked.
- Workflow owners now point calculator profile lifecycle assembly to the common
  package and record the hard-rule status.

## Verification

- `python3 -B -m pytest tests/test_code_structure_guard.py` — 36 passed.
- `python3 -B tools/check_code_structure.py` — no errors; three existing source
  soft warnings plus code-map freshness reminder only.
- Code-map check was stale after tool/source commits; regenerated once.
- `git diff --check` — passed.
- `python3 -B tools/check_agent_change_gate.py --cached` — passed.

## Hard Rule

Scope: direct call expressions in production
`apps/calculator/ui/tabs/*.py`. Allowed owner:
`apps/calculator/ui/lifecycle/`. Tests are outside the production scan.

The rule is intentionally syntactic and conservative. It does not attempt to
infer arbitrary settle-cycle literals; named controller triggers and injected
policy remain the documented owner contract.

## Changed Files

- `tools/check_code_structure.py`
- `tests/test_code_structure_guard.py`
- `docs/agent_workflows/AGENT_CHANGE_GATES.md`
- `docs/agent_workflows/UI_SURFACE_WORKFLOW.md`
- `docs/WORK_PLAN.md`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `result_reports/active/460_enforce-profile-lifecycle-owner-gate.md`

## Change Gate

```yaml
change_gate:
  new_source: none
  hotspot_delta: accepted-for-slice
  code_map_check: regenerated
  ui_literal_exemption: none
  report_exemption: none
  read_ledger: included
```

Hotspot reason: the existing structure checker is the canonical owner for
persistent source architecture invariants; the added rule is isolated as one
pure AST helper plus orchestration call.

Read Ledger:

- lifecycle design hard-gate section; reason: approved enforcement contract.
- structure checker package registry, UI scan orchestration, and focused tests;
  reason: minimal owner integration.
- change gate and UI workflow implementation-status/window ranges; reason:
  compact policy synchronization.
- broad read: none
- repeated read: none

## Next Action

AHRI SEER2 detail view implementation.
