```yaml
record:
  date: 2026-07-14
  topic: train-admin-mapping-foundation-slice-1d
  tags: train-admin, mapping, schema, mock-training, readiness, fixture-alignment
  memory_review: updated
  memory_reason: Record the strict schema/mapping/mock-training alignment boundary and evidence limits.
change_gate:
  new_source: small
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

# Change Reason

The DEV mock mapping, case selectors, and numeric training generator previously
used independent synthetic values. Their individual smoke success could not
prove that schema-backed values or condenser combinations resolved from the
repository mapping fixture.

# Contract / Behavior Changed

- DEV mock mapping generation now consumes the Slice 1B runtime-equivalent
  repository fixture.
- Mapping-backed numeric and one-hot training values are resolved from paired
  selector rows; the strict model training CSV headers remain unchanged.
- The alignment validator checks the active Predict schema, base mapping
  options, conditional condenser cascade/spec identity, schema-backed values,
  and one-hot selections row by row.
- F&T selector rows carry Pi; PFC selector rows keep Pi empty.

# Evidence And Verification

- 76 focused mock generator, schema readiness, Train service/process runner,
  bootstrap, and Predict mapping tests pass.
- Existing Predict and Train execution smoke CLIs pass through their DEV
  artifact/training entry points.
- Invalid IDU, ODU, Compressor, Refrigerant, Expansion, condenser combination,
  F&T/PFC Pi state, and mapping/training value mismatch tests fail explicitly.
- The legacy fixture and `data/mapping.json` remain unchanged.

# Changed Files

- DEV mock mapping/training generator and aligned-set validator
- mapping requirement ML relationship metadata
- focused mock/readiness/smoke tests and DEV documentation
- Phase 1 design, work plan, memory, and result index

# Known Risks

The aligned set uses synthetic fixture values and a DEV training backend. It
proves schema/readiness wiring and current entry-point compatibility only, not
physical relationships, feature usefulness, accuracy, generalization, real
company mapping completeness, or production readiness.
