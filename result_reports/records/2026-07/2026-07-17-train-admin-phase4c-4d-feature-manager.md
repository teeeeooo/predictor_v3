# Train/Admin Phase 4C+4D Feature Manager

```yaml
record:
  date: 2026-07-17
  topic: train-admin-phase4c-4d-feature-manager
  tags: train-admin, phase-4c, phase-4d, feature-mutation, stable-identity, dependency-preview, table-first
  memory_review: updated
  memory_reason: Stable identity, atomic Rename, isolated ordering, and protected dependency behavior are durable Phase 4 boundaries.
```

## Change Reason

Phase 4B provided canonical generation persistence, but users could not complete
the basic Feature lifecycle through one controlled Data Definition workflow.
Rename semantics also needed to separate stable identity from consumer-facing
aliases and from presentation-only label editing.

## Contract / Behavior Changed

- Basic supported Features use atomic Add, Edit, Rename, Duplicate, Remove,
  Enable, Disable, Predict Move, and ML Move commands over immutable drafts.
- Rename optionally changes label, Predict key, and ML name in one transaction,
  requires a Predict-key or ML-name change, and preserves stable identity.
  Label-only changes use Edit; Duplicate always creates a new identity.
- Dependency policy updates only approved identity-safe references and blocks
  unapproved fixed-string/import-time, Derived, One-hot, Target/registry,
  training-header, model-compatibility, source, trigger, and rule dependencies.
- Predict display order, including inactive Features, is independent from ordered
  ML contract order. Boundary moves reject without mutation.
- Side-effect-free Impact Preview describes exact candidate projection changes,
  Mapping requirements, model compatibility, retraining, affected references,
  blockers, and Save eligibility.
- The existing table-first controller owns selection, dirty state, Preview,
  Reset, and Save orchestration. Phase 4B stale-parent and atomic generation
  publication remain the only canonical persistence path.

## Evidence And Verification

- Full repository regression: `2262 passed, 2 xfailed`.
- Focused Feature mutation, controller, Mapping handoff, and offscreen UI tests
  cover command atomicity, identity, collisions, dependency blockers, independent
  ordering, Preview parity, selection, dirty state, Reset/Save recovery, and
  accessibility.
- Structure gate exits successfully with 15 warning-only existing hotspots; no
  new manager file exceeds the configured soft boundaries.
- Concrete `mapping.json` values and model artifacts are not written by command
  Preview or Feature mutation tests.
- Windows native Feature Manager smoke was not run on the macOS host and remains
  a pre-release verification item alongside the Phase 4B Windows smoke.

## Changed Files

- `core/data_definition/`
- `apps/train/services/data_definition_service.py`
- `apps/train/controllers/`
- `apps/train/ui/data_definition*`
- Data Definition, persistence, Mapping handoff, controller, and UI tests
- Phase 4 owner, architecture, plan, log, memory, and closeout documents

## Known Risks

- Existing fixed-string/import-time consumers and model compatibility contracts
  intentionally prevent some baseline Rename, Remove, Disable, and ML-order Save
  operations until an approved migration or retraining workflow exists.
- Derived, One-hot, and Target/registry entries are dependency evidence only;
  their authoring remains in later slices.
- Windows native focus, keyboard, and dialog behavior still needs bounded smoke
  evidence before release.
