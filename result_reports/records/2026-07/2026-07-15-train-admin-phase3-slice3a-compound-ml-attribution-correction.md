record:
  date: 2026-07-15
  topic: train-admin-phase3-slice3a-compound-ml-attribution-correction
  tags: train-admin, data-definition, phase-3, slice-3a, ml-projection, compound-attribution
  memory_review: updated
  memory_reason: ML blocker attribution now evaluates complete per-definition change bundles and preserves every related field before global fallback.

change_gate:
  new_source: none
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner

# Change Reason

The row-aware Slice 3A blocker projection evaluated each field change alone.
Mutually dependent changes such as enabling `idu` as a model input and assigning
its previously blank ML name therefore changed the full candidate projection but
could not be attributed to `idu`, producing an incorrect global blocker.

# Contract / Behavior Changed

- The save-plan projection owner groups canonical draft changes by stable row
  identity and applies every field in one definition bundle to the baseline before
  comparing compatibility fingerprints.
- An impactful definition emits one structured blocker item per changed field, so
  compound context such as `model_input_enabled` plus `ml_name` remains complete.
- Multiple independently impactful definitions retain their canonical row/field
  order. Global fallback remains only when no changed definition bundle explains
  the confirmed full-candidate mismatch.
- Focused-detail relevance, cross-source logical deduplication, widget rendering,
  writer/persistence behavior, and candidate-validation attribution are unchanged.

# Evidence And Verification

- 62 focused validation/save-plan/writer/detail tests passed, covering single-field,
  same-definition compound, multi-definition compound, partial-revert, global,
  deduplication, retry, and protected-file invariants.
- 192 impacted tests passed across Data Definition projection/state/inventory/UI,
  guarded Save, schema validation/writer, Data Mapping dynamic requirements, Train
  shell, Predict schema adapters, and ML catalog compatibility.
- Native Computer Use was not rerun, as required by the correction scope.

# Changed Files

- Data Definition save-plan compound attribution helper
- focused save-plan and inventory/detail projection tests
- Work Plan, result index, and active memory

# Known Risks

- A compatibility mismatch that no individual changed-definition bundle can
  explain remains global by contract; no speculative multi-row owner is inferred.
- Controlled Add/Edit commands and all Slice 3B+3C behavior remain deferred.
- No production schema, feature catalog, mapping data, configuration, training
  data, or model artifact was changed.
