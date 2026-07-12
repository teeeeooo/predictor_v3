```yaml
record:
  date: 2026-07-13
  topic: silent-fallback-retirement
  tags: calculator, en14825, iso16358, ks-c9306, ahri210240, fail-fast, correction
  memory_review: updated
  memory_reason: Supported standard/profile boundaries and the retired AHRI/ISO engines are long-lived calculator ownership decisions.
change_gate:
  new_source: none
  hotspot_delta: none
  ui_literal_exemption: none
  reuse_commonization: local-with-reason
```

# Change Reason

The all-standards extraction audit found caller-visible config state divergence
and unsupported profile, selector, cross-standard, and historical-engine inputs
that could silently return a plausible result.

# Contract / Behavior Changed

EN facade config attribute replacement now updates the shared context. ISO HSPF
accepts only `iso16358_2_hspf`; the generic simple and variable-bin engines are
removed. ISO CSPF profile climate and test-selection selectors are required
enums, while the profile-absent flat-config contract remains active. KS rejects
ISO `cspf_test_profile` schema. AHRI removes the HSPF2 v2 engine, facade method,
v2-only mapping and validation; active public aliases remain under
`normalize_public_test_points()` for the production variable-capacity path.

Standard-defined measured/default/derived points, optional-test formulas,
interpolation/extrapolation, auxiliary heat, product defaults, active capability
IDs, routes, result schemas, and golden expected values are unchanged.

# Evidence And Verification

Focused standard/refactor/fail-fast coverage passed 127 tests. Repository-wide
pytest passed 1,816 tests with two expected xfails. Changed owners compiled and
the active deep-result fingerprints passed. Runtime, AST, class-base, public
surface, and invalid-selector guards cover the retired boundaries. Structure
guard passed with ten pre-existing warnings and no new warning; staged
whitespace and objective gates passed. Cross-standard commonization remains
inappropriate because this correction strengthens separate standard owners.

# Changed Files

EN/ISO/KS/AHRI standard owners, AHRI alias config, focused contract and guard
tests, active ISO/AHRI workflow and owner docs, the all-standards design
correction, memory seed, report index, and this record.

# Known Risks

Unsupported legacy inputs now raise instead of calculating, which is the
intentional compatibility break. Historical archive and the superseded AHRI
design remain unchanged as evidence and must not be interpreted as active
support documentation.
