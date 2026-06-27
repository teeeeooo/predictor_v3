# 482 Fix UI Literal Sentinel Warning

## Goal

Fix the Phase 2 UI literal warning path so runtime sentinel values such as
`width=0`, `width=1`, `height=0`, and `height=1` do not emit warnings.

## Changed Files

- `tools/agent_change_gate_ui_literals.py`
- `tests/test_tools_check_ui_magic_literals.py`
- `result_reports/active/482_fix-ui-literal-sentinel-warning.md`

## Changes

- Added a small sentinel helper that checks the numeric `ast.Constant.value`
  instead of comparing an AST node object directly with `{0, 1}`.
- Added a focused staged-index test proving `width=0`, `height=1`, `padx=0`,
  and `pady=1` are warning-free.
- Preserved existing Phase 1 hard errors and Phase 2 warning behavior for
  non-sentinel values.

## Verification

- `python3 -B -m pytest tests/test_tools_check_ui_magic_literals.py` — passed,
  15 tests.
- Final `python3 -B tools/check_agent_change_gate.py --cached` and
  `git diff --check` are run at slice closeout.
- `code_map_check`: checked; map freshness is already stale from prior commits
  and this small gate helper change does not regenerate it in Slice 1.

## Excluded Scope

- No production app/core/calculator logic changed.
- No schema, public API, fixture, golden, or broad duplicate detector changed.
- No report lifecycle cleanup was performed.

## Reuse / Commonization Decision

`tools/agent_change_gate_ui_literals.py` is the existing owner for Phase 1 and
Phase 2 UI literal staged-line checks. The fix reuses that owner and adds only a
small local sentinel predicate because the rule is scanner-specific and has no
second consumer.

## Change Gate

```yaml
change_gate:
  new_source: none
  hotspot_delta: none
  code_map_check: checked
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
  report_exemption: none
  read_ledger: included
```

Read Ledger:

- `tools/agent_change_gate_ui_literals.py`: Phase 2 keyword range, reason:
  locate sentinel comparison bug in the existing scanner owner.
- `tests/test_tools_check_ui_magic_literals.py`: Phase 2 warning tests, reason:
  add sentinel regression coverage without broad test search.
- broad read: none.
- repeated read: none.

## Next Action

Pure detail formatting coercion helper.
