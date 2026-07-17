# Train/Admin Phase 4C+4D Audit Correction

```yaml
record:
  date: 2026-07-18
  topic: train-admin-phase4c-4d-audit-correction
  tags: train-admin, phase-4c, phase-4d, audit-correction, stable-identity, prepared-preview, dependency-evidence
  memory_review: updated
  memory_reason: Protection provenance, identity-only matching, and prepared Preview/Apply stale semantics are durable Phase 4 lifecycle invariants.
change_gate:
  new_source: small
  hotspot_delta: none
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

## Change Reason

The initial PR #21 implementation inferred protected Predict consumers from
baseline presence/visibility, allowed key fallback to replace a new identity
with a removed object, and executed UUID-producing Duplicate separately for
Preview and Apply. Those behaviors broke saved user Feature lifecycle, identity
independence, and Preview parity.

## Contract / Behavior Changed

- Predict protection consumes the fixed-index/import-time key contract from its
  runtime owner; manifest membership, role, visibility, and persistence do not
  create protection.
- Stable-identity rows match canonical Features only by identity. Key matching
  is limited to explicit identityless legacy rows, so same-key recreation gets
  new Feature, ordering, dependency, Mapping requirement, and generation identity.
- The application prepares a command once and retains its immutable result,
  candidate generation/fingerprint, and evidence. Controller revision/source-
  generation checks reject stale approval after another command, Reset, or reload.
- Preview evidence identifies affected Feature/reference, dependency owner/code,
  Predict/ML alias changes, automatic reference updates, blocker resolution,
  model/retraining impact, and Save eligibility. The View only renders it.

## Evidence And Verification

- Saved Predict-only Feature Add/Save/reload remains Rename/Remove capable while
  actual fixed-index Features remain blocked.
- Saved mapping-backed Feature Remove/same-key Add produces a new stable identity
  and a new Mapping requirement identity; the removed identities do not appear
  in the candidate.
- Duplicate Preview and Apply retain the same identity, generation ID, and scoped
  candidate fingerprint; cancellation is inert and stale command/Reset approvals
  preserve the latest draft.
- Full repository regression passes with `2268 passed, 2 xfailed`; the focused
  Data Definition/Phase 4B/controller/impact/offscreen UI subset passes with
  `124 passed`. Structure checks pass with warning-only pre-existing hotspots;
  no changed file introduces a new soft-limit warning.
- Windows native UI smoke was not run on the macOS host and remains pre-release.

## Changed Files

- Predict fixed-consumer owner and Data Definition dependency/candidate policy
- prepared command application contract, service, controller, Preview DTO, and UI
- Feature lifecycle, identity, stale/parity, persistence, and offscreen UI tests
- Phase owner/current-state docs, project log, memory, and this record/index

## Known Risks

- Existing fixed-index Predict keys, Derived/One-hot/Target references, and model
  compatibility contracts remain protected until their approved migration.
- Windows native dialog/focus smoke remains required before release; automated
  offscreen coverage is not reported as native evidence.
