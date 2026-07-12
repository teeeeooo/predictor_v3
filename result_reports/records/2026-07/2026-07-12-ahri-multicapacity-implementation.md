```yaml
record:
  date: 2026-07-12
  topic: ahri-multicapacity-implementation
  tags: ahri210240, seer2, hspf2, dual-stage, triple-capacity, tkinter
  memory_review: pending-closeout
change_gate:
  new_source: product-specific sibling engines
  hotspot_delta: bounded-by-new-owners
  reuse_commonization: shared-multicapacity-primitives
```

# Change Reason

Implement the approved AHRI 210/240-2026 multi-capacity design across stable
calculator facades, capability routing, Calculator application adapters, Tkinter
Single/Batch surfaces, result/export contracts, and focused formula evidence.

# Contract / Behavior Changed

- Existing capability IDs remain `ahri210240.seer2` and `ahri210240.hspf2`.
- Requests now carry an explicit product classification while omitted values keep
  the current variable-capacity behavior.
- New dual-stage SEER2, dual-stage HSPF2, and triple-capacity northern HSPF2
  engines are product-specific siblings of the existing variable engines.
- New multi-capacity ratings expose raw and nearest-0.05 published values.
- Multi-capacity HSPF2 resistance energy uses 3.412 Btu/Wh and records compressor
  and resistance energy separately.
- Product-aware UI and batch work preserve the active product snapshot and omit
  inactive hidden values from calculation requests.

# Evidence And Verification

Pending CI and focused validation on the implementation branch. The accepted
2026 overlay records direct or recalculated expected values without modifying
raw official AHRI Analytics evidence.

# Known Risks

Tkinter platform visual smoke is not available through the GitHub connector.
Automated surface, adapter, formula, routing, copy/export, and state-restoration
guards are the primary acceptance evidence; any skipped platform smoke remains
explicit at closeout.
