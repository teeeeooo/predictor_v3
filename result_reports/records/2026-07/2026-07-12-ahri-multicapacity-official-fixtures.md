record:
  date: 2026-07-12
  topic: ahri-multicapacity-official-fixtures
  tags: ahri210240, seer2, hspf2, fixture, golden, chrome, provenance
  memory_review: updated
  memory_reason: Add durable pointers for the three official multi-capacity calculator evidence fixtures and their raw-result limitations.

# Change Reason

Collect reproducible synthetic cases from the AHRI Analytics official calculator
for future SEER2 Dual Stage, HSPF2 Dual Stage, and Triple Stage Northern HSPF2
engine work. The existing downloaded Northern `resultM` was not promoted by
itself; each accepted case now keeps its own input, M, and M1 evidence.

# Contract / Behavior Changed

- Added private official-calculator fixture directories under
  `tests/fixtures/ahri210240/official_calculator/`.
- Each case preserves the downloaded Input Template, completed input CSV, raw
  M/M1 CSVs, normalized `expected.json`, and `provenance.md`.
- Added a fixture-local integrity test only; no production calculator, UI,
  public API, JSON contract, or formula implementation changed.
- M and M1 remain separate expected result records. Screen values are kept next
  to raw CSV precision.

# Evidence And Verification

- Chrome reached all three official profiles and accepted the synthetic input
  through the calculator upload/replace flow.
- Screen headline values were recorded as: SEER2 M/M1 `12.45/12.45`, Dual
  Stage HSPF2 `9.47/8.57`, and Northern HSPF2 `10.65/10.05`.
- Northern HSPF2 was confirmed with DHR Minimum and DOE Region 4; H23, H21,
  and H31 were selected. The Dual Stage HSPF2 case used H21 and demand defrost
  with credit `1.03`.
- Raw outputs contain 66 columns for SEER2, 200/199 columns for HSPF2 M/M1,
  and 276/275 columns for Northern HSPF2 M/M1. Normalized expected data keeps
  stable headline, option, seasonal aggregate, and bin-trace fields rather
  than copying every raw column.
- `pytest -q tests/test_ahri210240_official_calculator_fixture_integrity.py`
  passed: 18 tests.
- Predictor calculations were intentionally not compared because the requested
  multi-capacity core paths are not implemented.

# Changed Files

- `tests/fixtures/ahri210240/official_calculator/manifest.json`
- Three case directories under `tests/fixtures/ahri210240/official_calculator/`
- `tests/test_ahri210240_official_calculator_fixture_integrity.py`
- `result_reports/REPORT_INDEX.md`
- `result_reports/memory/project_memory_seed.md`

# Known Risks

- The calculator did not display a version string; provenance records
  `not displayed` rather than guessing one.
- Raw M/M1 CSVs do not expose explicit bin-temperature or bin-hour columns.
  The fixture preserves raw bin keys and values but does not infer a standard
  temperature mapping.
- HSPF M1 raw output does not expose a separate DHR field. The input DHR/DOE
  selection is retained as the source of that option.
- The synthetic cases are official-calculator regression evidence, not
  certification-grade product data.
- Shiny session/WebSocket internals were not reverse-engineered and no
  unconfirmed REST endpoint was called.
