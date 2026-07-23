# Train/Admin Phase 5B Model Lifecycle Foundation

```yaml
record:
  date: 2026-07-23
  topic: train-admin-phase5b-model-lifecycle-foundation
  tags: train-admin, phase-5b, model-lifecycle, candidate, promotion, rollback, bootstrap, legacy-migration, predict
  memory_review: updated
  memory_reason: Phase 5B establishes the durable Candidate, Active, migration, shared-training, and Predict startup contracts consumed by later Phase 5 work.
```

```yaml
change_gate:
  new_source: split
  hotspot_delta: wiring-only
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

## Change Reason

Successful training previously replaced the sole fixed `model/model.pkl`, leaving
no safe review, rollback, or Bootstrap boundary for the planned Train/Model UX.
Phase 5B required lifecycle ownership before later analysis and UI slices.

## Contract / Behavior Changed

- One default stable workspace below user state owns immutable versioned
  Candidates and a revision-guarded atomic Active reference with activation
  history.
- Training freezes the registry snapshot, executes through the existing port,
  and publishes a validated Candidate without changing Active. Failure,
  cancellation, and publication exceptions preserve Active.
- Promotion and rollback re-promotion verify current generation/fingerprints,
  preprocessing, all production Targets, exact artifact feature order,
  experimental-feature eligibility, deserialize integrity, and bounded prediction
  smoke before atomic Active replacement.
- Legacy import preserves the original, uses hash identity, is idempotent, and
  creates continuity Active only when current compatibility is fully proven.
- Newly composed Predict resolves the immutable Active Candidate path or a
  controlled missing/invalid status. Existing loaded services do not hot-swap.
- Core ML receives a caller-provided staging path and has no lifecycle dependency.

## Evidence And Verification

- Lifecycle/application focused integration: 72 passed.
- Exact-base QProcess focused comparison: 2 passed; changed-head QProcess focused
  coverage also passed, including QProcess-to-Candidate publication. The earlier
  timeout was not reproduced when the test-owned QApplication/event-loop lifetime
  was present, so no runner defect was identified.
- Canonical macOS/offscreen pytest: 2478 passed, 2 xfailed.
- Structure guard: passed with pre-existing unrelated soft warnings only; new
  lifecycle/application source stays below the 250 LOC split threshold.
- Windows-native and packaging validation were not run and are outside this
  acceptance.

## Changed Files

- `apps/common/model_lifecycle/`
- `apps/train/application/`, controller, composition, job, and run contracts
- `apps/predict/app.py`
- `core/ml/training.py`
- focused lifecycle, QProcess, dependency, migration, promotion, and composition
  tests
- architecture, planning, project state, log, memory, and this record/index

## Known Risks

- Candidate management UI, Predict reload-required UI, detailed analysis
  artifacts, retention/deletion, packaging, CLI, campaigns, and agent loop remain
  later Phase 5 work.
- Real company model quality and production-data validation are not claimed by
  repository fixtures or DEV fast training.
