```yaml
record:
  date: 2026-07-14
  topic: train-admin-mapping-data-foundation-audit-correction
  tags: train-admin, mapping, dynamic-attribute, boolean, finite-number, option-payload
  memory_review: updated
  memory_reason: Preserve the corrected cross-group dynamic value and option-payload contract for later Train/Admin work.
change_gate:
  new_source: small
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

# Change Reason

The Phase 1 final audit found that Refrigerant/Expansion requirement columns
discarded runtime payloads, boolean metadata did not produce canonical JSON
booleans, non-finite numeric values could pass conversion, and the DEV mock
resolver assembled condenser keys outside the shared identity owner.

# Contract / Behavior Changed

- Refrigerant and Expansion keep their runtime section keys as Predict options
  while definition-backed payload columns now project, validate, persist,
  reload, and export like other mapping groups.
- Raw payload remains row backing data but does not become an editor column or
  schema without a Data Definition requirement.
- Boolean values use one Qt-free coercion policy and persist as JSON booleans;
  ambiguous values are rejected and required `False` remains valid.
- Built-in and dynamic numeric mapping values must be finite. Atomic JSON save
  also disables non-standard NaN serialization as a final boundary guard.
- DEV mock condenser resolution uses the shared canonical Pi and conditional
  condenser-key helpers.

# Evidence And Verification

- Focused dynamic mapping, persistence, validation, Predict, and DEV mock suite:
  125 passed.
- Full repository suite: 1970 passed, 2 expected xfailed.
- Focused tests cover option payload restore/edit/save/reload/export, canonical
  boolean inputs and invalid-value preservation, non-finite built-in/dynamic
  numeric failures, hidden unknown payload, and shared condenser-key use.
- The legacy wide fixture and `data/mapping.json` are unchanged.

# Changed Files

- Shared mapping value policy and editor projection/validation/persistence
- Generic mapping entity validation and DEV mock condenser resolution
- Focused dynamic mapping, value-policy, Predict-adjacent, and mock tests
- Phase 1 design/closeout state, work plan, project log, memory, and report index

# Known Risks

Repository fixtures prove structural contracts only. Company-local mapping
completeness, real training data, model quality, and production readiness remain
outside this correction. PR #14 remains Draft/Open pending final re-audit;
Phase 2 is not started.
