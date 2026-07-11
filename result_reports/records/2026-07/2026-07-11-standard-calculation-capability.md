```yaml
record:
  date: 2026-07-11
  topic: standard-calculation-capability
  tags: calculator, capability, architecture, migration
  memory_review: no-change
  memory_reason: The active architecture owner now contains the durable capability contract.
```

# Change Reason

Production standard calculation orchestration was distributed across Calculator
application usecases and outbound adapters, preventing other callers from sharing
one execution owner.

# Contract / Behavior Changed

`core.calculators.capability` now owns operation resolution, typed request checks,
built-in composition, calculator construction, and method orchestration. Existing
raw results, diagnostics, formulas, and validation exceptions remain unchanged.
Single and batch paths use the same capability operations.

# Evidence And Verification

- Capability registry/error/result-identity/exception/dependency tests passed.
- 42 focused capability and application boundary tests passed.
- 85 golden, smoke, and single/batch UI regression tests passed.
- Direct engine/dispatcher search found no application/UI/Predict execution bypass.
- Structure gate and `git diff --check` completed.

# Changed Files

- `core/calculators/capability/`
- Calculator application usecases/adapters
- `tests/test_standard_calculation_capability.py`
- `docs/architecture/project_architecture.md`

# Known Risks

EN14825 and AHRI SEER2 adapters retain existing construction-only factories for
presentation configuration reads. Calculation execution is capability-owned; a
future metadata boundary can remove this compatibility dependency.
