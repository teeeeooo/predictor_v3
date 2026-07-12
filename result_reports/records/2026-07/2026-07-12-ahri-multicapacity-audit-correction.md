record:
  date: 2026-07-12
  topic: ahri-multicapacity-audit-correction
  tags: ahri210240, seer2, hspf2, fixture, audit, cutout, m1, regime
  memory_review: updated
  memory_reason: Record the corrected raw-field schema, k1/k2 curve-group boundary, dual-stage regime reclassification, and cutout evidence needed for future AHRI golden work.

# Change Reason

Correct the first multi-capacity fixture acceptance slice without changing
production formulas, calculator capabilities, application code, or UI. The
correction makes normalized expected data an integrity projection of the raw
input/M/M1 CSVs and adds a separate Dual Stage HSPF2 cutout/fractional case.

# Contract / Behavior Changed

- Fixture schema and manifest are version 2 and identify the official oracle as
  AHRI 210/240 (2023) Appendix M and Appendix M1 evidence.
- `input_fields` now preserves every input header, including booleans and
  blanks. Each M/M1 `raw_fields` projection preserves every downloaded result
  header/value, so missing expected raw fields fail integrity checks.
- `performance_curve_groups` keeps raw k1/k2/k3 groups separate from
  `activated_operating_cases`. Dual-stage regimes are derived from raw
  building load versus low/high capacity; HSPF adds high-stage plus auxiliary
  resistance. Northern raw `case_name` values remain unchanged, including raw
  zero labels.
- Seasonal aggregates, building loads, resistance/auxiliary fields, cutout
  delta families, DHR, bin raw values, and case names are now explicit
  normalized projections with candidate interpretation metadata where the raw
  header has no official semantic label.
- Added `dual_stage_hspf2_cutout_synthetic_01` with H4/H21, T_off=35,
  T_on=45, valid M/M1 results, and cutOut_delta values of 1, 0.5, and 0.

# Evidence And Verification

- Chrome reached the HSPF Dual Stage calculator, applied the corrected 41-field
  input CSV, and calculated successfully: M HSPF `4.28`, M1 HSPF `3.89`.
- Cutout M and M1 each contain `cutOut_delta` distribution one=4,
  fractional=2, zero=12; the prime family matches the same distribution.
- Existing raw CSVs were not overwritten. Existing three fixture raw checksums
  remain represented in the corrected manifest/expected data; the new case has
  its own input/template/M/M1 checksums.
- Focused integrity suite passed: 36 tests. It covers manifest completeness,
  checksums, full input/raw result projections, headline rounding, DHR,
  seasonal sums, bin/building-load/cutout/resistance/case-name evidence,
  regime reclassification, positive test points, and oracle-boundary metadata.
- No production calculator, formula, public API, UI, or Shiny/REST assumption
  was changed. Raw evidence is not a certification claim.

# Changed Files

- `tests/test_ahri210240_official_calculator_fixture_integrity.py`
- `tests/fixtures/ahri210240/official_calculator/manifest.json`
- Four fixture `expected.json` and `provenance.md` files under
  `tests/fixtures/ahri210240/official_calculator/`
- New `dual_stage_hspf2/dual_stage_hspf2_cutout_synthetic_01/` fixture
- `result_reports/REPORT_INDEX.md`
- `result_reports/memory/project_memory_seed.md`

# Known Risks

- The calculator version and explicit bin temperature/hour columns remain
  unavailable in downloaded evidence.
- AHRI 210/240-2026 final-formula compatibility is deliberately unresolved;
  these fixtures are direct golden candidates only after a standards audit
  confirms the 2023/2026 scope.
- Raw headers without official meaning are retained as raw fields and
  normalized candidate aggregates, not treated as certified semantics.
