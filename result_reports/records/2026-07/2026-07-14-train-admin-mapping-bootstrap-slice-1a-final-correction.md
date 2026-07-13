```yaml
record:
  date: 2026-07-14
  topic: train-admin-mapping-bootstrap-slice-1a-final-correction
  tags: train-admin, mapping, condenser, converter, source-key, correction
  memory_review: updated
  memory_reason: Strict converter identity validation and current editor source identity are durable mapping invariants.
change_gate:
  new_source: none
  hotspot_delta: wiring-only
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

# Change Reason

The existing Excel converter could create an incomplete non-PFC condenser key
when Pi, Fin Type, or Row was missing. ODU Cond Specs edits also changed identity
values without updating the row `source_key`, leaving validation context stale.

# Contract / Behavior Changed

ODU sheet rows now validate ODU, Fin Type, Row, and conditionally required Pi
before contributing to converter output. Failures include sheet, Excel row, and
field context, propagate to the caller, and occur before JSON write so no new
partial output replaces an existing mapping.

ODU Cond Specs edits to ODU, Fin Type, Pi, or Row now recalculate `source_key`
through the shared canonical Pi and condenser key policy. Incomplete non-PFC
draft identities remain editable and reach validation without exceptions.

# Evidence And Verification

- Focused tests cover missing F&T/future-Fin Pi, missing Fin Type/Row, valid
  future-Fin and PFC keys, no partial converter output, all four editor identity
  edits, PFC normalization, and incomplete-draft validation context.
- Existing bootstrap, editor, persistence, converter, and Predict regressions,
  Python compilation, structure checks, and the staged agent gate pass.
- The legacy fixture and `data/mapping.json` are unchanged.

# Changed Files

- existing Excel mapping converter and ODU Cond Specs editor commands
- focused converter and editor identity tests
- current work plan, mapping memory, and result report index

# Known Risks

This proves mapping structure and identity pipeline consistency only. It does
not prove company mapping values, completeness, model quality, or production
readiness. Slice 1B and actual Data Mapping UI work remain unstarted.
