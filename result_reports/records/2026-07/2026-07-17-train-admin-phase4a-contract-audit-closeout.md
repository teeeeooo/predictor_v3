# Train/Admin Phase 4A Contract Audit Closeout

```yaml
record:
  date: 2026-07-17
  topic: train-admin-phase4a-contract-audit-closeout
  tags: train-admin, phase-4a, feature-contract, stable-identity, generation, persistence, data-mapping, one-hot, target-registry, model-artifact
  memory_review: no-change
  memory_reason: Existing active Phase 4 memory entries already preserve the durable owner, generation, dirty-draft, source-mode, and candidate/promotion boundaries; exact 4A contract decisions remain discoverable in the active closeout design.
```

## Change Reason

The merged Phase 3 foundation and approved Phase 4 direction still required a
current-state audit before Unified Feature Manager production work could begin.
The audit had to resolve canonical storage, stable identity, ordering, persistence,
runtime generation, dirty Mapping, One-hot, Target, and training/artifact
questions without bypassing existing write guards.

## Contract / Behavior Changed

Phase 4A is closed with these approved design decisions:

- one versioned structured JSON manifest becomes the canonical Data Definition
  contract, while existing Predict/ML/Derived/One-hot/Target surfaces become
  generated projections;
- managed definitions receive stable opaque identities independent of user-facing
  keys and ML names;
- Predict order, ordered ML contract, One-hot emitted order, Derived DAG order,
  and Target presentation order remain isolated;
- Definition persistence uses immutable generation bundles and an atomic active-
  generation pointer, with no partial publication;
- runtime consumers use immutable snapshots and staged TrainShell prepare/commit/
  abort cutover, while standalone Predict performs required generation checks at
  startup and execution boundaries;
- dirty Data Mapping drafts retain their state and expose pending-generation
  reconciliation instead of silent reprojection;
- One-hot category mutation follows static, mapping-backed, or external/provider
  source ownership;
- initial Target CRUD is limited to validated existing model groups and target-
  level policy;
- training runs and future candidates preserve scoped contract fingerprints;
  candidate storage and explicit Phase 5 promotion remain separate from the
  active model;
- protected string-bound consumers remain blocked from ordinary rename/delete
  until their owner migration exists;
- Slice 4B is the next work and owns the canonical manifest, bootstrap migration,
  projection providers, generation bundle, active pointer, cross-contract
  validation, and scoped fingerprints.

No production behavior changes in this closeout.

## Evidence And Verification

The audit inspected the merged Data Definition draft/identity, schema loader and
writer, save-plan guards, ML Feature Catalog and projections, Derived evaluator,
model registry, training request/result and child-process publication path,
Predict schema/composition/cache routes, Data Mapping requirement projection and
draft session, and TrainShell process composition.

The documented decisions preserve the current Data Definition/Data Mapping/Train/
Predict owners and explicitly retain ML-projection-changing Save guards until
Slice 4B replaces them with an accepted all-or-nothing boundary.

This is a docs-only closeout. ML, GUI, and training suites are not required for
behavior verification; repository document consistency and change-gate checks
remain the PR validation target.

## Changed Files

- `docs/designs/2026-07-17-train-admin-phase-4a-current-state-contract-audit-closeout.md`
- Train/Admin design discovery and phase-state documents
- `docs/WORK_PLAN.md`
- `project_brief.md`
- `result_reports/REPORT_INDEX.md`
- this result record

## Known Risks

- The parent Phase 4 design retains some pre-closeout pending/open-question wording;
  the approved Phase 4A closeout is the authoritative amendment and must remain in
  the active design indexes.
- Exact manifest path, JSON field names, package layout, migration mechanics, and
  public DTO names remain intentionally deferred to Slice 4B owner audit.
- Existing import-time and fixed-string consumers remain protected migration work;
  the closeout does not make them dynamically reloadable.
