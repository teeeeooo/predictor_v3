```yaml
record:
  date: 2026-07-11
  topic: standard-calculation-capability-correction
  tags: calculator, capability, architecture, audit-correction
  memory_review: no-change
  memory_reason: The active architecture owner and corrected source encode the durable invariant.
```

# Change Reason

Audit of the initial capability migration found missing operation/profile
compatibility validation, public direct-execution seams, stale injection tests,
and evidence that did not match the committed tree.

# Contract / Behavior Changed

Built-in handlers now validate the resolved profile's calculator owner, metric,
mode, and standard before construction. Unknown/disabled profile errors remain
owned by the existing resolver. Public direct calculator execution helpers and
calculator/factory-based application execution seams were removed; application
tests inject capability executors or independent handlers.

# Evidence And Verification

- Incompatible profiles fail before calculator construction; unknown/disabled
  profile resolver errors, raw-result identity, and engine exceptions are preserved.
- Production dependency guards cover Calculator application/adapters/UI and
  Predict bypasses while excluding formula/golden engine tests.
- Final committed-tree candidate: `1629 passed, 2 xfailed`.
- Structure/dependency gates and `git diff --check` passed.
- External calculator and manual GUI verification were not run; the complete
  automated application/UI/golden suite is the acceptance evidence.

# Changed Files

- `core/calculators/capability/`
- Calculator application/adapters and their fake-executor tests
- `tests/test_standard_calculation_capability.py`
- `docs/WORK_PLAN.md`

# Known Risks

EN14825 and AHRI SEER2 retain construction-only profile/config readers for
presentation defaults, outside this correction's metadata-boundary scope. They
cannot execute calculations outside the capability gateway.
