```yaml
record:
  date: 2026-07-14
  topic: train-admin-mapping-bootstrap-slice-1a
  tags: train-admin, mapping, bootstrap, legacy-csv, condenser, migration
  memory_review: updated
  memory_reason: The bootstrap-only boundary and conditional F&T/PFC identity are durable mapping contracts.
change_gate:
  new_source: split
  hotspot_delta: wiring-only
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

# Change Reason

The legacy wide fixture stores independent tables side by side and cannot be
processed by the generic one-sheet CSV converter. Its `Cond Index` column is a
historical Excel lookup helper rather than the runtime condenser identity.

# Contract / Behavior Changed

A strict Train adapter now parses the fixed legacy layout into the existing
Mapping Editor draft, runs existing validation, and remains outside normal
Import and persistence UI. Numeric aliases are normalized to current editor
names, blank block keys skip only their own block, and duplicates or malformed
values fail with legacy row/group/field context.

Condenser identity formatting has one core owner. F&T uses ODU + Fin Type + Pi +
Row; PFC normalizes the legacy Pi placeholder to absent and uses ODU + Fin Type +
Row. Editor projection, validation, runtime projection, the legacy converter,
and Predict autofill share that policy. `Cond Index` values are ignored.

# Evidence And Verification

- The validation fixture projects deterministically into seven editor groups and
  passes the existing editor validation/runtime projection boundary.
- Focused parser, mapping editor, Predict autofill/dropdown, controller, and
  service regression tests pass.
- Python compilation and the repository structure/change gates pass.

# Changed Files

- `apps/train/adapters/mapping/`
- `core/mapping/`
- focused mapping and Predict tests
- Phase 1/governing designs and current work plan
- mapping memory and result record index

# Known Risks

This proves fixture structure and contract compatibility only. It does not prove
company mapping value correctness, completeness, model quality, or production
readiness. Slice 1A does not install populated mapping data or change UI widgets.
