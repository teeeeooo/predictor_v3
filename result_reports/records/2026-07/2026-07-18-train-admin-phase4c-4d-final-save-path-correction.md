# Train/Admin Phase 4C+4D Final Save-path Correction

```yaml
record:
  date: 2026-07-18
  topic: train-admin-phase4c-4d-final-save-path-correction
  tags: train-admin, phase-4c, phase-4d, save-validation, lifecycle, stable-identity, audit-correction
  memory_review: updated
  memory_reason: Identity-first Save validation and exact controlled lifecycle evidence are durable Feature lifecycle invariants.
change_gate:
  new_source: none
  hotspot_delta: none
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

## Change Reason

Canonical candidate generation correctly assigned new Feature and Mapping
requirement identities after Remove/same-key Add, but restricted-field Save
validation still zipped equal-length baseline/current rows and misclassified the
two lifecycle events as a direct `stable_identity` edit.

## Contract / Behavior Changed

- Restricted-field validation matches shared rows by canonical identity and
  evaluates unmatched baseline/current identities without positional pairing.
- Exact controlled removal and exact controlled addition are independent events,
  even when `column_key`, `ml_name`, row count, or row position coincide.
- Controlled lifecycle records must match actual baseline/current identity set
  differences. Direct identity replacement, raw row add/delete, inconsistent
  evidence, and removed-identity reuse remain blocked.
- No field became editable and no Save, candidate, repository, dependency, UI,
  Mapping-value, model, or runtime publication contract changed.

## Evidence And Verification

- Mapping-backed Add/Save/reload/Remove/same-key Add now has an allowed prepared
  Preview and Save plan, publishes with `written`, and reloads the new Feature
  and Mapping requirement identities.
- The old Feature and requirement identities are absent from the active manifest
  and Predict/ML ordering; the new generation differs from its parent.
- Direct `stable_identity` replacement and forced reuse of a removed identity
  remain blocked with `restricted_field_edit_not_allowed`; raw row add/delete
  guards remain active.
- Full repository regression passes with `2270 passed, 2 xfailed`; the expanded
  Save/schema-writer/Feature/Phase 4B/Data Definition UI subset passes with
  `171 passed`. Structure checks pass with warning-only unchanged hotspots.
  Windows native UI smoke is out of scope and was not run.

## Changed Files

- `core/data_definition/edit_policy.py`
- Save-contract and end-to-end Feature lifecycle regression tests
- Phase owner/current-state documents, project log, memory, index, and this record

## Known Risks

- Windows native Feature Manager smoke remains a pre-release item.
- Existing protected Predict, Derived, One-hot, Target/registry, and model
  compatibility migrations remain outside this correction.
