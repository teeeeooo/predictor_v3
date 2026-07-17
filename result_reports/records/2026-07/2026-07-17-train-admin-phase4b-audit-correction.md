# Train/Admin Phase 4B Audit Correction

```yaml
record:
  date: 2026-07-17
  topic: train-admin-phase4b-audit-correction
  tags: train-admin, phase-4b, audit-correction, production-wiring, stale-writer, ordering, cross-validation
  memory_review: updated
  memory_reason: Production composition, stale-writer atomicity, and canonical ordering are durable Phase 4B completion invariants needed before Phase 4C.
change_gate:
  new_source: split
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

## Change Reason

The Phase 4B generation transaction was test-usable but production Train still
constructed the legacy schema writer by default. Bootstrap identity covered only
selected identities, drafts were not bound to their loaded generation, and
several ordering and relation contracts were not enforced end to end.

## Contract / Behavior Changed

- Production `create_shell()` initializes the approved bootstrap generation and
  injects the filesystem adapter through a small application repository port.
  Direct schema writing remains only for explicitly constructed compatibility
  services.
- Bootstrap and candidate generation names share the complete canonical semantic
  manifest hash, excluding only generation metadata.
- Drafts retain their base generation. The POSIX filesystem adapter serializes
  parent comparison, immutable publication, and active-pointer replacement, so a
  stale writer cannot replace a newer active generation.
- Predict, ordered ML, dependency-topological Derived, One-hot category, and
  Target presentation orders have explicit canonical owners used by projection
  and fingerprints. Duplicate compatibility fields must agree with those owners.
- One-hot membership/category policy, Mapping-requirement parity and coverage,
  Target/model-group association, and generation-scoped projection parity now
  block invalid candidates before publication.
- Mapping values, model artifacts, training/promotion, runtime cutover, Phase 4C
  mutation commands, and Predict reload remain outside this transaction.

## Evidence And Verification

Focused acceptance and regression coverage proves production composition
bootstrap/Save, legacy-path isolation, deterministic semantic identity, stale and
concurrent writer rejection, staging/pointer failure preservation, rollback,
canonical Derived/One-hot/Target projection order, projection generation parity,
relation validation, presentation-only Save, protected model-impacting guards,
and Phase 3 Data Definition behavior. The impacted suite passes 265 tests.

## Changed Files

- Train application port, production composition, persistence service, and
  filesystem generation adapter
- canonical manifest identity, draft binding, projection, fingerprint, and
  validation owners
- focused Phase 4B acceptance and Phase 3 regression tests
- architecture, work-plan, project-log, result-index, and memory records

## Known Risks

- The single-writer primitive targets the already approved macOS/POSIX
  same-filesystem deployment boundary; a future non-POSIX adapter needs its own
  supported locking primitive behind the same port.
- Process-wide runtime cutover, standalone Predict reload, authoring UI, model
  candidate/promotion, and Data Mapping dirty-draft reconciliation remain later
  slices and are not implied by disk publication.
- Phase 4C may start after this corrected Phase 4B PR is merged; it must retain
  the protected consumer guards until its explicit dependency migrations exist.
