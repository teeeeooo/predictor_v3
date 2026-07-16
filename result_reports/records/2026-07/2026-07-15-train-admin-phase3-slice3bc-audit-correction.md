```yaml
record:
  date: 2026-07-15
  topic: train-admin-phase3-slice3bc-audit-correction
  tags: train-admin, data-definition, phase-3, slice-3b, slice-3c, audit-correction
  memory_review: updated
  memory_reason: The durable workflow now separates full parity from the ML fingerprint and preserves controlled-Add and no-selection attribution.
change_gate:
  new_source: none
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

# Change Reason

The accepted Slice 3B+3C structure still allowed unsupported cross-contract row
shapes, lost field attribution after activating a newly added model input, and
hid blockers whenever search or filters removed the current selection.

# Contract / Behavior Changed

- Controlled Edit validates the complete current-role shape and exposes only
  options its Qt-free command contract can complete. Supported source changes
  clean source-owned metadata as one atomic transition; invalid transitions do
  not mutate the draft or selection.
- Controlled Add stores an immutable initial-row snapshot. Later field changes
  are compared to that snapshot for ML blocker attribution and Add impact text,
  while the initial projection-neutral Add remains one authorized row addition.
- Save planning and the temporary-candidate writer reuse full Data Definition
  validation for role shape, current Feature Catalog parity, and one-hot
  relationships. ML fingerprint meaning remains limited to model compatibility.
- Impact collection no longer depends on selection. Row blockers use
  `selection_unavailable` during no-match presentation and recover direct/other
  relevance without changing blocker evidence when selection returns.

# Evidence And Verification

- 116 focused tests passed for role/source atomicity, metadata cleanup, full
  candidate safety, writer pre-backup rejection, Add provenance/activation/
  partial revert, impact summaries, and no-match blocker preservation.
- 268 impacted tests passed across Data Definition, dynamic Data Mapping
  requirements, Predict schema/mapping adapters, Feature Catalog parity, and the
  four-tab Train shell.
- Compile, diff check, and structure guard passed. The structure guard retained
  warning-only hotspot findings for `save_contract.py` and
  `data_definition_state_builder.py`; the correction adds no new owner or source
  package, and re-audit remains the next gate before Slice 3D.
- Native Computer Use was not retried, as required by the correction scope.

# Changed Files

- Data Definition command contract/validation, immutable draft, save-plan,
  candidate validation/writer, and UI-facing blocker/impact projection owners
- Role-aware Edit dialog projection and focused/offscreen regressions
- Work plan, active memory, and result-record index

# Known Risks

- The changed save-contract and state-builder owners remain above the 400-LOC
  soft threshold. Their current responsibilities remain cohesive for this
  correction; Slice 3B+3C re-audit must precede any Slice 3D implementation.
- Native physical interaction evidence remains intentionally excluded.
