```yaml
record:
  date: 2026-07-12
  topic: ahri-multicapacity-implementation
  tags: ahri210240, seer2, hspf2, dual-stage, triple-capacity, tkinter
  memory_review: no-change
  memory_reason: The implementation realizes the already-recorded AHRI sibling-engine, stable-facade, and immutable-official-evidence boundaries; this record and the active design own the completed product-path details.
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

# Contract / Behavior Changed

- Existing capability IDs remain `ahri210240.seer2` and `ahri210240.hspf2`.
- Requests carry an explicit product classification while omitted values preserve
  the current variable-capacity behavior.
- New dual-stage SEER2, dual-stage HSPF2, and triple-capacity northern HSPF2
  engines are product-specific siblings of the existing variable engines.
- New multi-capacity ratings expose raw and nearest-0.05 published values.
- Multi-capacity HSPF2 resistance energy uses 3.412 Btu/Wh and records compressor
  and resistance energy separately.
- Single and Batch Calculator surfaces switch visible schemas by product, retain
  product-local drafts, clear stale result/detail state, and omit inactive hidden
  inputs from requests and exports.
- Triple-capacity Northern HSPF2 uses separate Low, Full, and Boost stage tables;
  product-specific detail schemas expose operating case, stage availability,
  compressor energy, and resistance energy without changing variable schemas.

# Evidence And Verification

- GitHub Actions run `29190948224` passed on commit
  `ba98a4d11b58abe2c38397c24746142e11bd499c`.
- 71 focused formula, capability, application-adapter, Tk Single/Batch,
  product-switch, detail-schema, snapshot, and export guards passed under Xvfb.
- Python compilation of changed calculator/application/UI owners passed.
- `tools/check_code_structure.py` passed.
- The accepted 2026 overlay records direct or recalculated expected values without
  modifying raw official AHRI Analytics evidence.

# Known Risks

A native Windows/macOS visual smoke was not available through the GitHub
connector. Automated behavior, sizing, product-switch, state restoration,
copy/export, formula, and structure evidence passed; native platform appearance
should receive one bounded review before main integration if required by release
acceptance.
