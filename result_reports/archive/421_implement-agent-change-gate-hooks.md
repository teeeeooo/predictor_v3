# 421 Implement Agent Change Gate Hooks

## Goal

Connect the implemented cached agent change gate to the local Git commit flow
without expanding its staged-diff policy.

## Scope

- Add fast repository-rooted `pre-commit` checks.
- Add commit-message exemption trailer validation.
- Add focused hook tests using a temporary Git repository where appropriate.
- Document opt-in hook activation and return the next action to the EN14825
  product slice.

## Changed Files

- `.githooks/pre-commit`
- `.githooks/commit-msg`
- `tests/test_githooks.py`
- `docs/agent_workflows/AGENT_CHANGE_GATES.md`
- `result_reports/active/421_implement-agent-change-gate-hooks.md`

## Results

- `pre-commit` resolves the repository root, runs
  `git diff --cached --check`, and then invokes the cached checker.
- `commit-msg` passes when the exemption trailer is absent, accepts one
  well-formed allowlisted value, and rejects malformed, unsupported, or
  duplicate trailers.
- Hook activation remains an explicit per-clone command:
  `git config core.hooksPath .githooks`.
- No Git configuration was changed by this task.

## Verification

- `python3 -B -m pytest tests/test_githooks.py tests/test_tools_check_agent_change_gate.py`
- `python3 -B tools/check_agent_change_gate.py --cached`
- `git diff --check`
- `git status --short`

## Known Risks

- Hooks remain bypassable until each clone opts into `.githooks`; CI and
  pre-push enforcement remain separate, unimplemented slices.
- The final cached-checker invocation sees only staged content. Because this
  task does not stage user files, focused tests provide the behavioral evidence
  for the new unstaged hook changes.

## Change Gate

```yaml
change_gate:
  new_source: small
  hotspot_delta: none
  code_map_check: not_required
  report_exemption: none
  read_ledger: included
```

Read Ledger:

- `docs/agent_workflows/AGENT_CHANGE_GATES.md`: lines 211-305; reason: commit
  trailer, hook policy, and implementation status owners.
- `tools/check_agent_change_gate.py`: lines 1-36; reason: cached CLI invocation
  and exit-code contract.
- `tools/agent_change_gate_models.py`: lines 1-18 and 57-70; reason: current
  report exemption allowlist.
- `tests/test_tools_check_agent_change_gate.py`: lines 1-58 and 135-215;
  reason: subprocess and temporary Git repository test conventions.
- `result_reports/active/417_agent_change_gate_manifest_index_hardening.md`:
  lines 37-68; reason: previous slice boundary and next action.
- broad read: none
- repeated read: none

## Next Action

EN14825 SCOP batch parent section wiring.

## Commit / Push

- The hook, test, policy, and report changes are committed together.
- The final pushed commit hash and push result are reported in the terminal
  response to avoid a self-referential report update loop.
