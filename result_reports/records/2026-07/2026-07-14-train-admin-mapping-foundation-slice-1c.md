```yaml
record:
  date: 2026-07-14
  topic: train-admin-mapping-foundation-slice-1c
  tags: train-admin, mapping, data-definition, dynamic-attribute, persistence, round-trip
  memory_review: updated
  memory_reason: Record the definition-backed dynamic mapping attribute and identity/payload boundary.
change_gate:
  new_source: none
  hotspot_delta: wiring-only
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

# Change Reason

ODU Cond Specs projection and persistence retained only `Cond Area` and
`Cond Volume`, so a Data Definition-added mapping attribute could appear as an
empty column but its existing value could not reload or persist.

# Contract / Behavior Changed

- Mapping requirements carry Data Definition type and required metadata into
  editor groups.
- Definition-backed columns use that metadata for required/numeric validation
  and Data Mapping attribute presentation.
- Runtime row payload values remain available for requirement-backed
  projection, while unknown attributes never become columns automatically.
- ODU Cond Specs persistence writes every visible non-identity editor column;
  ODU, Fin Type, canonical Pi, and Row remain the only identity controls.

# Evidence And Verification

- 125 focused Data Definition, mapping projection/validation/persistence/export,
  service/controller, and UI-model tests pass; a final 68-test dynamic/Predict
  subset also passes after the acceptance helper was definition-derived.
- `Cond Inner Area` number/required metadata, edit, save, runtime numeric value,
  reload, and JSON review export round-trip pass.
- Existing Cond Area/Cond Volume and conditional F&T/PFC behavior remain intact.
- Unsupported dynamic types fail and unknown raw values do not create columns.

# Changed Files

- Data Definition mapping requirement metadata
- mapping editor group, projection, validation, persistence, and controller metadata
- Data Mapping service validation integration and focused tests
- Phase 1 design, work plan, memory, and result index

# Known Risks

The current schema contract has no unit field, so this slice preserves existing
unit behavior and does not invent a second unit schema. Supporting a future unit
column requires an explicit Data Definition schema change. This evidence does
not establish production mapping completeness or model quality.
