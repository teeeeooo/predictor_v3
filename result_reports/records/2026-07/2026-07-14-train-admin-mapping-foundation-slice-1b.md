```yaml
record:
  date: 2026-07-14
  topic: train-admin-mapping-foundation-slice-1b
  tags: train-admin, mapping, fixture, bootstrap, predict, populated-state
  memory_review: updated
  memory_reason: Record the repository-only runtime-equivalent fixture and its shared consumer boundary.
```

# Change Reason

Phase 1 needed a populated mapping state that represents the approved legacy
bootstrap without installing synthetic values as the application's default
`data/mapping.json`.

# Contract / Behavior Changed

- `mapping_runtime_equivalent.json` is the deterministic repository fixture for
  the bootstrap runtime projection.
- An exact bootstrap-to-JSON comparison makes fixture drift fail visibly.
- Data Mapping loads all seven populated editor groups from this path with no
  unresolved rows, and Predict consumes the same fixture for F&T and PFC
  cascade/autofill behavior.
- The legacy wide source remains unchanged and `Cond Index` remains ignored.

# Evidence And Verification

- 50 focused bootstrap, Data Mapping service, and Predict mapping tests pass.
- All seven editor groups are populated and editor validation passes.
- F&T and PFC fixture-backed autofill paths resolve through the existing
  conditional condenser identity policy.
- Neither the legacy CSV fixture nor `data/mapping.json` changed.

# Changed Files

- repository runtime-equivalent mapping fixture
- focused bootstrap, Data Mapping, and Predict integration tests
- Phase 1 design, work plan, memory, and result index

# Known Risks

The fixture values are synthetic structural evidence. They do not establish
company mapping completeness, physical correctness, model quality, or
production readiness.
