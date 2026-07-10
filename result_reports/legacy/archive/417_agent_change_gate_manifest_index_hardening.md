# 417 Agent Change Gate Manifest and Index Hardening

## Goal

Close two cached-checker gaps before hook integration: silently ignored
manifest fields and missing source index-blob test evidence.

## Scope

- Made the local manifest parser reject unknown, duplicate, misplaced, and
  incorrectly indented fields.
- Kept the schema intentionally limited to the documented top-level and
  `report_exemption` keys.
- Enforced literal lowercase `approved_by_user: true`.
- Added focused parser failures and a partial-stage source test where the index
  contains 240 LOC while the working tree contains 360 LOC.
- Updated the owner workflow wording; hook and CI behavior remain unchanged.

## Changed Files

- `tools/agent_change_gate_models.py`
- `tests/test_tools_check_agent_change_gate.py`
- `docs/agent_workflows/AGENT_CHANGE_GATES.md`
- `result_reports/active/417_agent_change_gate_manifest_index_hardening.md`

## Verification

- Focused gate tests: 13 passed.
- Python compile check: OK.
- Code structure guard: OK with existing EN14825 UI LOC warnings and the
  existing code-map metadata freshness reminder.
- Code-map `--check`: inspected; regeneration skipped because no source symbol,
  import, or LOC inventory boundary changed.
- Staged cached-gate self-check: OK.
- `git diff --check`: OK.

## Known Risks

- The parser is intentionally not general YAML; extending the manifest requires
  an explicit schema and parser update.
- Hook and branch-diff enforcement remain later slices.

## Change Gate

```yaml
change_gate:
  new_source: none
  hotspot_delta: none
  code_map_check: checked
  report_exemption: none
  read_ledger: included
```

Read Ledger:

- `tools/agent_change_gate_models.py`: lines 75-135; reason: manifest parser
  state and validation boundary.
- `tests/test_tools_check_agent_change_gate.py`: lines 45-205; reason: parser,
  index-blob, and temporary Git repository test conventions.
- `docs/agent_workflows/AGENT_CHANGE_GATES.md`: lines 172-210 and 240-258;
  reason: manifest schema and cached-check policy.
- broad read: none
- repeated read: none

## Next Action

Add pre-commit and commit-msg hooks around the hardened cached checker.

## Commit / Push

- Final commit hash and push status are reported in terminal output.
