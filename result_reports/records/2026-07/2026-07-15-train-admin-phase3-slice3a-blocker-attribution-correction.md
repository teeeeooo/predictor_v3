record:
  date: 2026-07-15
  topic: train-admin-phase3-slice3a-blocker-attribution-correction
  tags: train-admin, data-definition, phase-3, slice-3a, blocker-attribution, candidate-validation
  memory_review: updated
  memory_reason: Slice 3A now preserves blocker row/field/source context and projects selection-specific relevance without collapsing distinct same-code issues.

change_gate:
  new_source: none
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner

# Change Reason

The first Slice 3A correction exposed candidate issues in Focused Detail but
attributed every blocker to any selected row that happened to be changed. It also
deduplicated by issue code, which could discard distinct candidate errors sharing
`candidate_schema_validation_failed`.

# Contract / Behavior Changed

- Save-plan blockers carry optional row and field context for projection changes,
  restricted edits, raw-row changes, and derived-policy changes. Blockers without
  attributable definition evidence remain global.
- Predict schema validation retains its existing string result while also exposing
  structured row/field context for the guarded candidate writer. Save-result status,
  paths, messages, backup, and atomic replacement contracts are unchanged.
- Controller state preserves severity, code, target, message, row identity, field,
  and evidence source. Focused Detail classifies that evidence as direct,
  other-definition, or global for the selected identity.
- Cross-source duplicates are removed only when code, target, row, field, and
  normalized message match. Direct, other-definition, and global groups render in
  that deterministic order while source/canonical issue order remains stable inside
  each group.

# Evidence And Verification

- 56 focused validation/state/detail/save-plan/writer tests passed, covering two changed rows,
  direct/other/global relevance, same-code candidate errors, true cross-source
  duplicate removal, retry, and schema preservation.
- 186 impacted tests passed across Data Definition validation/state/inventory/UI,
  guarded Save, Data Mapping dynamic requirements, Train shell, Predict schema
  adapters, and ML catalog compatibility.
- The structure guard reported only pre-existing unrelated soft warnings and no
  changed-owner warning.
- Native Computer Use was not rerun, as required by the correction scope.

# Changed Files

- Predict schema structured validation context, Data Definition save-plan/writer
  blocker context, controller state, and focused-detail projection
- focused inventory and guarded-save tests
- Work Plan, result index, and active memory

# Known Risks

- Header/report/write-target errors without a definition identity remain global;
  row-aware parser and candidate validation errors are attributed directly.
- Controlled Add/Edit commands and all Slice 3B+3C behavior remain deferred.
- No production schema, mapping data, configuration, training data, or model
  artifact was changed.
