```yaml
record:
  date: 2026-07-12
  topic: ahri-multicapacity-implementation
  tags: ahri210240, seer2, hspf2, dual-stage, triple-capacity, tkinter
  memory_review: no-change
  memory_reason: The existing AHRI standards-audit and sibling-engine memory entry already owns the formula, facade, and immutable-evidence boundaries; this record captures the corrected implementation-specific regression triggers.
change_gate:
  new_source: product-specific sibling engines
  hotspot_delta: bounded-by-new-owners
  ui_literal_exemption: none
  reuse_commonization: shared-multicapacity-primitives
```

# Change Reason

Implement the approved AHRI 210/240-2026 multi-capacity design across stable
calculator facades, capability routing, Calculator application adapters, Tkinter
Single/Batch surfaces, result/export contracts, and focused formula evidence.
Resolve the blocking findings from the PR #11 audits without changing the
approved owner direction or the existing variable-capacity calculation path.

# Contract / Behavior Changed

- Existing capability IDs remain `ahri210240.seer2` and `ahri210240.hspf2`.
- Requests carry an explicit product classification while omitted values preserve
  the current variable-capacity behavior.
- New dual-stage SEER2, dual-stage HSPF2, and triple-capacity northern HSPF2
  engines are product-specific siblings of the existing variable engines.
- New multi-capacity ratings expose raw and nearest-0.05 published values.
- Dual-stage HSPF2 resolves an untested H2Low directly with AHRI 210/240-2026
  Equations 11.44 and 11.50; metadata records `eq_11_44_11_50`.
- Triple-capacity Northern HSPF2 gives tested H3Low precedence when H3Low is
  applicable: H2Low is resolved by Equations 11.253 and 11.254 and supplied
  H2Low data cannot bypass the correction.
- H3Low requiredness follows AHRI Table 7 footnote 7 with an inclusive 37°F
  boundary. Dual-stage requires H3Low when Low-stage lockout is disabled or its
  lockout temperature is at or below 37°F. Triple Northern requires H3Low when
  the Low-stage minimum is at or below 37°F.
- When the Low stage is not permitted at or below 37°F, H3Low is excluded from
  Single/Batch requests, inactive low curves are not evaluated, and H3Low/H2Low
  are recorded as not applicable rather than populated with fabricated values.
- Single and Batch derive the same H3Low active-input schema from the lockout or
  stage-range inputs; required missing H3Low capacity and power produce exact
  field errors.
- Multi-capacity HSPF2 keeps fractional-bin normalized aggregates under explicit
  `normalized_*` keys and returns actual Region IV seasonal Btu/Wh totals by
  multiplying them by `heating_load_hours = 1701`; Single, Batch, detail, copy,
  and CSV presentation use the seasonal totals.
- Multi-capacity HSPF2 resistance energy uses 3.412 Btu/Wh and records compressor
  and resistance energy separately.
- Triple Northern Cases 4 through 7 have deterministic equation-level guards for
  selected case, stage fractions, availability delta, compressor energy,
  resistance energy, bin energy, and seasonal contribution.
- Compressor-availability detail uses the stage selected by the operating case:
  Low for Cases 1/4/6, Full for Cases 2/7, Boost for Cases 3/5/8, and unavailable
  for resistance-only operation.
- Dual-stage SEER2 option parsing is application-owned. Invalid Cd or lockout
  values produce field-specific input errors and highlight the exact option cell.
- The 2026 expected overlay is schema-checked and numerically recomputed for Dual
  SEER2, Dual HSPF2, cut-out HSPF2, Triple candidate values, 3.412 conversion,
  corrected H2Low, seasonal totals, and nearest-0.05 publication.

# Evidence And Verification

- GitHub Actions run `29195661699` passed on commit
  `abcf16f0d9f19ce60869422bc1f6da788ef467fd`.
- 82 focused formula, capability, application-adapter, Tk Single/Batch,
  conditional-input, detail-schema, state, validation, overlay, and export guards
  passed under Xvfb.
- The selected Calculator regression set executed 976 tests. 975 passed on the PR;
  the only failure was
  `test_calculator_tk_app_builds_widget_tree`, whose legacy Xvfb width assertion
  fails identically on unchanged `main`. CI reproduces and verifies that baseline
  failure before accepting the regression step.
- Python compilation of changed calculator/application/UI owners passed.
- `tools/check_agent_change_gate.py --cached` passed against the staged PR delta.
- `tools/check_code_structure.py` passed.
- Raw official AHRI Analytics evidence remains immutable; corrected or derived
  values live only in the separate 2026 overlay.

# Known Risks / Remaining Manual Evidence

Native Windows/macOS visual smoke is not available through the GitHub connector.
The requested five-path native GUI smoke therefore remains pending and must not be
reported as completed. PR #11 is ready for final merge audit, but main integration
remains blocked until the reviewer accepts the automated evidence and any required
native smoke is completed.
