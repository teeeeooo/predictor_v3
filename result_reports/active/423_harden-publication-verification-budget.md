# 423 Harden Publication Verification Budget

## Goal

Make push completion evidence explicit and prevent redundant validation runs
through one owner workflow.

## Scope

- Define remote SHA publication verification.
- Define default one-run verification budgets and rerun conditions.
- Define the recommended final verification order.
- Link the staged gate document to the workflow owner without duplicating the
  policy.

## Changed Files

- `docs/agent_workflows/RESULT_REPORT_WORKFLOW.md`
- `docs/agent_workflows/AGENT_CHANGE_GATES.md`
- `result_reports/active/423_harden-publication-verification-budget.md`

## Results

- Push completion now requires `local_head`, remotely resolved `remote_main`,
  and an explicit `match: OK/NG` result.
- A local/remote SHA mismatch cannot be reported as a completed push.
- Applicable focused pytest, structure guard, code-map check, and cached gate
  commands now have a default one-run budget.
- Reruns are limited to failure or relevant source/test/report/gate evidence
  changes, and a final superset suppresses duplicate focused-suite execution.
- The workflow now sequences completion, hotspot review, focused validation,
  structure and code-map judgment, cached gate, then publication verification.

## Verification

- `git diff --check`
- `python3 -B tools/check_agent_change_gate.py --cached` against an isolated
  staged index containing the final three-file task scope.

No pytest, structure guard, or code-map check applies to this documentation-only
workflow policy change.

## Known Risks

- Remote SHA verification requires network access to the configured `origin`.
- The publication rule intentionally targets `origin/main`; publishing another
  branch requires a separately defined remote-branch evidence contract.

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

- `docs/agent_workflows/RESULT_REPORT_WORKFLOW.md`: lines 1-55 and 143-215;
  reason: report owner, terminal output, and commit/push workflow.
- `docs/agent_workflows/AGENT_CHANGE_GATES.md`: lines 224-305; reason: staged
  gate and hook policy link placement.
- broad read: none
- repeated read: none

## Project Log Judgment

No update. This is a procedural workflow hardening rule owned by the workflow
document and report, not a product milestone or architecture decision.

## Project Memory Delta

- type: procedure
  topic: publication-verification-and-validation-budget
  content: Push completion requires matching local and remote main SHAs, while
    applicable focused verification commands default to one run and rerun only
    after failure or relevant evidence changes.
  keywords:
    - publication-verification
    - verification-budget
    - rerun-policy
    - remote-sha
  assertionStatus: accepted
  source: result_reports/active/423_harden-publication-verification-budget.md

## Next Action

Apply the workflow to the next commit/push and return to EN14825 calculator
smoke / lifecycle closeout.

## Commit / Push

- The workflow documents and report are committed together.
- Final `local_head`, `remote_main`, and `match` publication evidence is
  reported in the terminal response to avoid a self-referential report update.
