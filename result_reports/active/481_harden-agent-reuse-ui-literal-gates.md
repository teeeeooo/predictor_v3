# 481 Harden Agent Reuse And UI Literal Gates

## Goal

Harden project-wide agent workflow gates so repeated helper/policy candidates
and UI presentation literals are surfaced earlier without forcing broad
automatic refactors.

## Scope

- Added a calculator-neutral reuse/commonization decision to the structured
  report gate for report-backed structural source changes.
- Added warning-first Phase 2 UI literal detection for newly staged UI source
  lines.
- Updated workflow/router/report docs to describe the minimum report evidence.
- Added focused tool tests for missing decisions, docs-only exemption from the
  requirement, Phase 2 warnings, and existing Phase 1 hard failures.

## Non-goals

- No production app/core/calculator logic changed.
- No schema, public API, fixture, golden, broad duplicate detector, semantic
  linter, config migration, or report lifecycle cleanup was performed.
- The next implementation slice remains the pure detail formatting coercion
  helper.

## Task Results

- `change_gate` now includes `reuse_commonization` with allowed values:
  `not_required`, `checked`, `reused-existing-owner`, `local-with-reason`, and
  `design-deferred`.
- Structural source changes cannot use `reuse_commonization: not_required`.
  The checker validates only the field and allowed value; review remains
  responsible for judging the architecture decision.
- Phase 2 UI literal candidates now emit warnings for added numeric `width=`,
  `height=`, `padx=`, `pady=`, and simple named color literals. Phase 1 hard
  errors for table sizing, `min_size`, `geometry`, and hex colors remain
  unchanged.
- Router, UI workflow, agent change gate, and report workflow docs now describe
  sibling-surface/reuse evidence and no-reuse/design-deferred reasons.

## Verification

- `python3 -B -m pytest tests/test_tools_check_agent_change_gate.py tests/test_tools_check_ui_magic_literals.py` — passed, 29 tests.
- `python3 -B tools/check_code_structure.py` — passed hard rules; existing EN
  hotspot warnings and pre-existing code-map freshness warning remain.
- `python3 -B tools/code_checker/build_reference_map.py --check` — checked;
  stale status is pre-existing from map commit `7a07288` versus current HEAD and
  this slice does not regenerate the map.
- Final `git diff --check`, cached gate, and status are recorded at closeout.

## Changed Files

- `AGENT_TASK_ROUTER.md`
- `docs/WORK_PLAN.md`
- `docs/agent_workflows/AGENT_CHANGE_GATES.md`
- `docs/agent_workflows/RESULT_REPORT_WORKFLOW.md`
- `docs/agent_workflows/UI_SURFACE_WORKFLOW.md`
- `tools/agent_change_gate.py`
- `tools/agent_change_gate_models.py`
- `tools/agent_change_gate_ui_literals.py`
- `tests/test_tools_check_agent_change_gate.py`
- `tests/test_tools_check_ui_magic_literals.py`
- `result_reports/active/481_harden-agent-reuse-ui-literal-gates.md`

## Reuse / Commonization Decision

Existing gate owners were reused: `agent_change_gate_models.py` owns structured
schema values, `agent_change_gate.py` owns staged policy evaluation, and
`agent_change_gate_ui_literals.py` owns UI literal scanning. No new checker
module or duplicate semantic linter was introduced. Phase 2 remains local to
the existing UI literal owner because it extends the same staged-line scanner.

## Known Risks

- Phase 2 warnings are intentionally heuristic and do not attempt all-numeric
  or semantic duplicate detection.
- Code-map freshness remains stale from prior docs/audit commits; regeneration
  is left to a source-structure slice that explicitly owns map updates.
- Report reviewers still need to judge whether a `reuse_commonization` decision
  is architecturally sound.

## Change Gate

```yaml
change_gate:
  new_source: none
  hotspot_delta: none
  code_map_check: checked
  ui_literal_exemption: none
  reuse_commonization: checked
  report_exemption: none
  read_ledger: included
```

Read Ledger:

- `docs/agent_workflows/AGENT_CHANGE_GATES.md`: structured gate and staged gate
  sections, reason: add reuse/commonization policy and Phase 2 warning contract.
- `docs/agent_workflows/UI_SURFACE_WORKFLOW.md`: preflight/result/export
  sections, reason: add sibling-surface and repeated policy evidence.
- `docs/agent_workflows/RESULT_REPORT_WORKFLOW.md`: report content section,
  reason: define minimum report evidence.
- `tools/agent_change_gate.py`, `tools/agent_change_gate_models.py`,
  `tools/agent_change_gate_ui_literals.py`: focused owner ranges, reason:
  extend existing gate owners without a new broad detector.
- focused agent-change-gate tests: parser/evaluation/UI literal ranges, reason:
  guard required block and warning-first behavior.
- broad read: none.
- repeated read: none.

## Next Suggested Action

Implement pure detail formatting coercion helper.
