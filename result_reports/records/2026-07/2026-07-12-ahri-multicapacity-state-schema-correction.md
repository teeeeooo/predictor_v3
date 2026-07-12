record:
  date: 2026-07-12
  topic: ahri-multicapacity-state-schema-correction
  tags: ahri210240, seer2, hspf2, fixture, schema, availability, auxiliary, case-name
  memory_review: updated
  memory_reason: Lock the final separation between Dual-stage load regimes, compressor availability, auxiliary heat state, and Northern official case names.

# Change Reason

Close the remaining semantic ambiguity in the AHRI multi-capacity fixture
schema. This is a fixture-local follow-up to the prior audit correction; no
production calculator, formula, capability, profile, application, or UI code
changes.

# Contract / Behavior Changed

- Dual-stage fixtures no longer use `activated_operating_cases` or
  `regime_distribution` for load/capacity comparisons.
- Dual-stage results now separate `load_capacity_regime_by_bin` and
  `load_capacity_regime_distribution` from
  `compressor_availability_by_bin`/`compressor_availability_distribution` and
  `auxiliary_heat_by_bin`/`auxiliary_heat_distribution`.
- The load-capacity projection contains only the three raw load/capacity
  regimes. Auxiliary resistance is independently classified as inactive or
  active and is never folded into a high-stage regime name.
- SEER2 records availability and auxiliary sections as `not_exposed` when the
  corresponding raw fields are absent.
- Triple Northern retains `activated_operating_cases` only for its raw official
  `case_name` projection and uses `operating_case_distribution` separately.
- `lockOutLowCapacityOps` is present only in `ui_options`; it is absent from
  `input_test_points` in every provenance file.
- Schema version remains 2 because this is a fixture-local semantic correction
  and no external fixture consumer is registered.

# Evidence And Verification

- The integrity helper recomputes load regime, availability, and auxiliary
  state from raw M/M1 fields before comparing expected projections.
- The cutout fixture has an explicit raw-and-expected exact-count assertion for
  both M and M1: `cutOut_delta` and `cutOut_delta_prime` each have one=4,
  fractional=2, zero=12, other=0, blank=0.
- Triple Northern raw `case_name` values are compared directly and are not
  classified through the Dual-stage load-regime helper.
- Focused fixture integrity suite passed: 38 tests.
- Official oracle boundary remains AHRI 210/240 (2023) Appendix M/M1;
  AHRI 210/240-2026 formula parity is not established and the evidence is not
  certification data.

# Changed Files

- `tests/test_ahri210240_official_calculator_fixture_integrity.py`
- Four fixture `expected.json` and `provenance.md` files under
  `tests/fixtures/ahri210240/official_calculator/`
- `result_reports/REPORT_INDEX.md`
- `result_reports/memory/project_memory_seed.md`

# Known Risks

- The fixture schema is intentionally local; no production consumer or formula
  path is validated by this suite.
- Explicit bin temperature/hour mappings and calculator version remain absent
  from the official downloaded raw CSV evidence.
