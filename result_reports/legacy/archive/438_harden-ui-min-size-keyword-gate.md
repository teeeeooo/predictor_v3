# 438 Harden UI Min-Size Keyword Gate

## Goal

Close the Phase 1 UI literal detector gap for numeric-pair `min_size` keyword
arguments.

## Scope

- Detect calls such as `Dialog(parent, min_size=(1180, 420))` on newly staged
  production UI lines.
- Add one focused regression case and align the owner policy wording.

## Non-goals

- No new literal category, legacy migration, UI implementation, hook process,
  common framework, AHRI sizing, or unrelated workflow change.

## Changed Files

- `tools/agent_change_gate_ui_literals.py`
- `tests/test_tools_check_ui_magic_literals.py`
- `docs/agent_workflows/AGENT_CHANGE_GATES.md`
- `result_reports/active/438_harden-ui-min-size-keyword-gate.md`

## Result

The AST keyword branch now recognizes `min_size` only when its value is a
two-element numeric tuple. Existing assignment/property detection and staged-
line grandfathering remain unchanged.

## Verification

- `python3 -B -m pytest tests/test_tools_check_ui_magic_literals.py` — 12 passed.
- `git diff --check` — passed.
- `python3 -B tools/check_agent_change_gate.py --cached` — passed.

## Change Gate

```yaml
change_gate:
  new_source: none
  hotspot_delta: none
  code_map_check: not_required
  ui_literal_exemption: none
  report_exemption: none
  read_ledger: included
```

Read Ledger:

- `tools/agent_change_gate_ui_literals.py`: keyword and tuple helper ranges;
  reason: identified Phase 1 gap.
- `tests/test_tools_check_ui_magic_literals.py`: Phase 1 parameterized cases;
  reason: focused regression parity.
- `docs/agent_workflows/AGENT_CHANGE_GATES.md`: UI literal policy list only;
  reason: exact enforced surface wording.
- broad read: none
- repeated read: none

## Next Action

Common visible-content notebook measurement design.
