```yaml
record:
  date: 2026-07-13
  topic: all-standards-final-audit-correction
  tags: calculator, iso16358, ks-c9306, ahri210240, selector, schema, correction
  memory_review: updated
  memory_reason: Final supported selector, schema, alias, and retired-surface boundaries are durable calculator contracts.
change_gate:
  new_source: none
  hotspot_delta: none
  ui_literal_exemption: none
  reuse_commonization: local-with-reason
```

# Change Reason

The final refactor audit found AHRI v2-only config/facade fields and explicit
ISO, KS, and AHRI selectors that could still enter an alternate calculation.
This record supersedes the remaining active-boundary statements in
`2026-07-13-silent-fallback-retirement.md` without mutating that append-only
record.

# Contract / Behavior Changed

AHRI HSPF2 removes legacy `bin_data`, test-point temperatures, constants,
facade bin attributes, and unused defaults. Variable-capacity public aliases
are exactly `A_Full -> A2`; H1/H2/H3 full, H21, and AFull aliases were v2-only
or product-local and are removed from this mapping. Dual/triple aliases remain
owned by their product resolvers. Derived H12 accepts normalized split or
packaged unit types and rejects unknown, null, empty, or conflicting selectors.

ISO CSPF validates explicit building-load and power-interpolation selectors,
while omitted keys retain measured and capacity-linear defaults. KS CSPF
requires its point/derived schema, measured/declared load selector, and
`ks_intersection`. KS HSPF requires the supported profile, non-empty required
points and bin table, typed derived/correction mappings, and the supported
rated-cooling-capacity config load line before calculation.

Standard-defined measured/default/derived points, optional-test resolution,
interpolation/extrapolation, auxiliary heat, H12/H22 formula fallbacks, active
product defaults, result schemas, rounding, capabilities, and golden expected
values remain unchanged. Unsupported legacy/schema/selector inputs now fail
intentionally.

# Evidence And Verification

Focused standard, golden, contract, and negative-selector coverage passed 192
tests. Calculator/application/batch/export-related local pytest passed 1,013
tests with 833 deselected and two expected xfails. Repository-wide local pytest
passed 1,846 tests with two expected xfails. No GitHub CI evidence was used.
Changed-owner compilation, structure, staged objective, and whitespace evidence
is completed in the same final commit workflow.

# Changed Files

AHRI HSPF2 context/point/facade/config, ISO context, KS CSPF/HSPF owners,
contract/validation/guard tests, active standard/design docs, memory seed,
report index, and this correction record.

# Known Risks

Callers that relied on retired facade fields, removed variable alias names, or
invalid/missing KS schemas now receive explicit errors. This is the intended
compatibility break. Historical archives and superseded records remain evidence,
not active support contracts.
