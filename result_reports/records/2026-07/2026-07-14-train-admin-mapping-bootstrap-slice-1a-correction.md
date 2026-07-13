```yaml
record:
  date: 2026-07-14
  topic: train-admin-mapping-bootstrap-slice-1a-correction
  tags: train-admin, mapping, condenser, pfc, normalization, correction
  memory_review: updated
  memory_reason: Canonical removal of every PFC Pi value across mapping producers and consumers is a durable runtime invariant.
change_gate:
  new_source: none
  hotspot_delta: wiring-only
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

# Change Reason

Slice 1A excluded Pi from PFC identity keys but raw draft Pi could still enter
runtime cascade and global option sections. Editor commands and Predict row/Pi
events could also retain a pasted or stale PFC Pi value.

# Contract / Behavior Changed

The shared condenser policy now canonicalizes every PFC Pi input to empty before
identity, validation, persistence, option generation, legacy bootstrap,
converter, or Predict autofill use. F&T and every future non-PFC Fin Type remain
Pi-required by default. No compatibility read or migration for historical
four-segment PFC keys was added.

Editor commands clear Pi when a row becomes PFC and reject Pi cell mutation for
an existing PFC row. Phase 2 requires the eventual UI to disable the Pi cell and
protect it from paste independently of the core invariant.

# Evidence And Verification

- Focused tests cover PFC placeholder and stale values, editor commands,
  validation, persistence options/cascade, the existing Excel converter, and
  Predict controller/autofill behavior.
- Existing mapping/editor/Predict focused regressions, Python compilation,
  structure checks, and the staged agent gate pass.
- The legacy fixture and `data/mapping.json` are unchanged.

# Changed Files

- shared mapping identity, editor, converter, bootstrap, and Predict policy paths
- focused mapping, converter, editor, and Predict tests
- Phase 2 Data Mapping design, current work plan, memory, and report index

# Known Risks

This proves mapping structure and pipeline consistency only. It does not prove
company mapping values, completeness, model quality, or production readiness.
The actual PFC Pi read-only/disabled UI remains Phase 2 work.
