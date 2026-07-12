# AHRI 210/240-2026 Multi-capacity Implementation Notes

The active implementation is owned by
`docs/designs/2026-07-12-ahri-multicapacity-core-calculator-gui-design.md`.

Implemented product classifications:

- `variable_capacity` — preserved existing engine and public behavior;
- `dual_stage` — SEER2 and HSPF2 product-specific engines;
- `triple_capacity_northern` — HSPF2 product-specific engine.

Stable capability identifiers remain unchanged. New multi-capacity results expose
raw and nearest-0.05 published values separately. HSPF2 results also expose
compressor and supplemental resistance energy separately and use 3.412 Btu/Wh.

Official AHRI Analytics raw fixture files remain unchanged. Corrected 2026
expectations are stored in
`tests/fixtures/ahri210240/official_calculator/2026_expected_overlay.json`.
