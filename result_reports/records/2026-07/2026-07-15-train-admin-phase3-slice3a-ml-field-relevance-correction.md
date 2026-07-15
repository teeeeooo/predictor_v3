record:
  date: 2026-07-15
  topic: train-admin-phase3-slice3a-ml-field-relevance-correction
  tags: train-admin, data-definition, phase-3, slice-3a, ml-projection, field-relevance
  memory_review: updated
  memory_reason: ML blocker context now distinguishes impactful definitions from the fields that actually contribute to their projection result.

change_gate:
  new_source: none
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner

# Change Reason

The compound-attribution correction correctly identified a definition whose full
change bundle altered the ML compatibility fingerprint, but it emitted every
changed field from that definition. Projection-neutral metadata such as `notes`
could therefore appear as an ML compatibility cause beside the fields that
actually created the projected feature.

# Contract / Behavior Changed

- Complete per-definition bundle comparison remains the first attribution step.
- For each impactful definition, canonical changed fields are retained when the
  field alone changes the baseline fingerprint or removing it from the complete
  bundle changes the final definition fingerprint.
- This bounded singleton plus leave-one-out rule preserves compound necessities
  and independently impactful fields without a powerset search, while excluding
  projection-neutral metadata.
- Definition ordering, field ordering, direct/other-definition/global focused
  relevance, structured blocker DTOs, and logical deduplication remain unchanged.
- Widgets and focused-detail projection continue to consume structured results;
  neither layer recalculates ML projection impact.

# Evidence And Verification

- 60 focused save-plan, schema-writer, blocker-detail, and guarded-Save tests
  passed for compound activation plus notes, single projection field plus notes,
  unrelated and relevant reverts, canonical order, mutation safety, direct/other
  relevance, global fallback, and cross-source deduplication.
- The repository schema contains an actual independent-impact case:
  `cooling_capa.model_input_enabled=false` and `cooling_capa.active=false` each
  produce the same feature-removal fingerprint. Both remain attributed through
  singleton impact even though either leave-one-out projection matches the full
  bundle.
- 196 impacted tests passed across Data Definition projection, save-plan,
  controller state, inventory/UI, schema validation/writer, Data Mapping dynamic
  requirements, Train shell, Predict schema compatibility, and ML catalog
  fingerprint compatibility.
- Structure validation had no hard failure. The changed save-contract owner now
  exceeds the 400-LOC soft threshold; its private relevance helpers remain within
  the existing attribution responsibility for this correction. A split audit is
  required before adding another responsibility to this hotspot.
- Native Computer Use was not rerun, as required by the correction scope.

# Changed Files

- Data Definition save-plan ML attribution owner
- focused save-plan and inventory/detail regression tests
- Work Plan, result index, and active memory

# Known Risks

- The deterministic singleton plus leave-one-out rule intentionally does not
  explore higher-order field powersets. A mismatch that no changed definition can
  explain under the existing definition-attribution contract remains global.
- Controlled Add/Edit commands and all Slice 3B+3C behavior remain deferred.
- No production schema, feature catalog, mapping/configuration data, training
  data, or model artifact was changed.
