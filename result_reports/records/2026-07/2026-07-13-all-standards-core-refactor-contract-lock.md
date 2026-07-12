```yaml
record:
  date: 2026-07-13
  topic: all-standards-core-refactor-contract-lock
  tags: calculator, en14825, iso16358, ks-c9306, brazil, architecture, refactor
  memory_review: no-change
  memory_reason: The current memory already preserves separate standard ownership and stable contract boundaries; this R0 record adds a bounded implementation baseline.
```

# Change Reason

All active non-AHRI Calculator standard cores require responsibility extraction
without changing formulas, routes, public APIs, config meaning, or results.

# Contract / Behavior Changed

No runtime behavior changed. The approved target is stable facades over
standard-local context, point, performance, seasonal, and result owners. Brazil
is already compliant and AS/NZS remains an inactive compatibility path.

# Evidence And Verification

Latest-main baseline passed 1,215 tests with two expected xfails. Seven R0
contract tests lock public signatures, caller-visible config attributes, and
ordered deep results across EN SEER/SCOP branches, active ISO profiles, KS
CSPF/HSPF, and Brazil compliance. Existing official/golden tests remain the
accuracy authority.

# Changed Files

The governing design, design index, standard-refactor contract test package,
this record, and the result index establish the implementation baseline.

# Known Risks

Ordered fingerprints are intentionally sensitive to nested mapping order and
floating-point drift. They must not be updated merely to make a refactor pass.
