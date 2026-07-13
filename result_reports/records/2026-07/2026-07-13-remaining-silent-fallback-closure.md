```yaml
record:
  date: 2026-07-13
  topic: remaining-silent-fallback-closure
  tags: calculator, iso16358, ks-c9306, ahri210240, validation, correction
  memory_review: updated
  memory_reason: Post-construction selectors, point-key allowlists, and complete KS config schemas are durable calculator input contracts.
change_gate:
  new_source: none
  hotspot_delta: none
  ui_literal_exemption: none
  reuse_commonization: local-with-reason
```

# Change Reason

The remaining audit found validation gaps after facade reassignment, during
AHRI variable point normalization, and inside KS derived/bin/load-line schema
handling. This record supersedes the relevant validation details in
`2026-07-13-all-standards-final-audit-correction.md` without mutating that
append-only record.

# Contract / Behavior Changed

ISO facade selector reassignment now calls the same context allowlist used at
config load. AHRI variable-capacity normalization rejects keys outside the
canonical schema and active `A_Full -> A2` alias before H12/H22 fallback.

Every KS CSPF default rule now requires source, capacity factor, and power
factor; sources cannot self-reference and factors must be finite positive
non-bool numbers. KS HSPF requires dict rows with unique finite numeric `tj`
and canonical `nj`, permits explicit zero hours, and rejects negative hours.
Its config load line requires finite numeric temperatures, distinct endpoints,
and a positive factor before any user slope/intercept override is considered.
All active KS documents now define `BL_h(0°C) = rated_cooling_capacity × 0.82`.

Official H12/H22 fallback, optional/derived points, interpolation,
extrapolation, auxiliary heat, rounding, result schemas, routes, and golden
expected values remain unchanged.

# Evidence And Verification

Focused negative and active-golden coverage passed 192 tests. Local
Calculator/application/batch/export-related pytest passed 1,039 tests with 834
deselected and two expected xfails. Repository-wide local pytest passed 1,873
tests with two expected xfails. No GitHub CI evidence was used. Changed-owner
compilation, structure, staged objective, and whitespace gates complete in the
same commit workflow.

# Changed Files

ISO context/facade, AHRI point normalization, KS CSPF/HSPF validation owners,
active KS rule/owner docs, runtime guard tests, all-standards design, memory
seed, report index, and this correction record.

# Known Risks

Previously ignored unknown AHRI keys, malformed KS config rows/factors, and
invalid post-construction ISO selectors now raise explicit errors. This is the
intentional compatibility break. KS `hours` is not accepted because no active
KS contract uses it; other standards retain their own hour schemas.
