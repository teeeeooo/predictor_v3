# 415 Agent change gate cached tool

## Goal

Turn the documented staged-change policy into a deterministic local checker
without adding hook or CI behavior in the same slice.

## Scope

- Added a Git-index adapter that reads staged names and index blobs.
- Added closed-schema parsers for report evidence and local task manifests.
- Added staged report association, literal allowlist, source size, class-count,
  hotspot-growth, formatting-only exemption, and code-map judgment checks.
- Added a thin `--cached` CLI and focused temporary-repository tests.
- Updated the owner workflow implementation status and regenerated the code map.

## Changed Files

- `tools/agent_change_gate_git.py`
- `tools/agent_change_gate_models.py`
- `tools/agent_change_gate.py`
- `tools/check_agent_change_gate.py`
- `tests/test_tools_check_agent_change_gate.py`
- `docs/agent_workflows/AGENT_CHANGE_GATES.md`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `result_reports/active/415_agent_change_gate_cached_tool.md`

## Verification

- Focused gate tests: 8 passed.
- Python compile check: OK.
- Code structure guard: OK with two pre-existing calculator UI LOC warnings.
- Code-map regeneration: OK.
- `git diff --check`: OK.
- Staged self-check with `tools/check_agent_change_gate.py --cached`: OK.

## Known Risks

- The checker is not invoked automatically until pre-commit and commit-msg
  hooks are added.
- Branch-diff and shallow-clone CI behavior remain outside this slice.
- The manifest parser intentionally accepts only the documented minimal schema;
  it is not a general YAML parser.

## Change Gate

```yaml
change_gate:
  new_source: split
  hotspot_delta: none
  code_map_check: regenerated
  report_exemption: none
  read_ledger: included
```

Read Ledger:

- `tools/check_code_structure.py`: lines 115-145, 188-218, 385-410, and
  683-714; reason: existing CLI, finding, LOC, and class-count conventions.
- `tests/test_code_structure_guard.py`: lines 1-90; reason: tools test style.
- `tests/test_code_checker_reference_map.py`: lines 1-90; reason: tools
  import and temporary-repository test style.
- `docs/agent_workflows/AGENT_CHANGE_GATES.md`: lines 146-265 and 285-303;
  reason: staged association, manifest, gate checks, and implementation status.
- `.gitignore`: current short file; reason: local manifest placement judgment.
- `result_reports/active/414_agent_change_gates_router_wiring.md`: lines 1-76;
  reason: previous slice boundary and report structure.
- broad read: none
- repeated read: none

## Next Action

Add pre-commit and commit-msg hooks around the stable cached checker.
