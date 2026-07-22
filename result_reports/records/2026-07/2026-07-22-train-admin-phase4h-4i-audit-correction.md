# Train/Admin Phase 4H+4I Audit Correction

record:
  date: 2026-07-22
  topic: train-admin-phase4h-4i-audit-correction
  tags: train-admin, phase-4h, phase-4i, generation, predict, stale-guard, mapping, audit-correction
  memory_review: updated
  memory_reason: Runtime generation ownership now includes actual Predict execution, mutable participant boundaries, Definition controller state, and exact Mapping dirty evidence.

change_gate:
  new_source: split
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner

## Change Reason

The first Phase 4H+4I closeout could report Predict generation B while parts of
inference still resolved bootstrap/static semantics. Predict cases and selected
Train CSV evidence were also incomplete stale boundaries, Data Definition used a
shadow state, and Mapping removal review inferred dirtiness from manifest drift.

## Corrected Contract

- One immutable `PredictRuntimeSnapshot` binds generation, Predict and ordered-ML
  projections, Derived evaluator, One-hot encoder, Target/result mapping,
  zero-fill policy, preprocessing identity, and scoped compatibility fingerprints.
  Embedded and standalone production composition inject this snapshot into the
  table/input/result/service execution graph; static/bootstrap defaults remain
  compatibility-only facades.
- Predict session mutation and execution state, model artifact identity, Train
  selection/file/header evidence, Definition draft/base/dirty evidence, and
  Mapping draft/provider evidence participate in prepare-to-commit stale checks.
- The Data Definition participant stages and commits the actual controller runtime
  baseline. Dirty external-update conflicts preserve draft and selection behind
  Save Definition, Reset Draft, and fresh Retry Apply recovery.
- Mapping reconciliation compares exact stable-identity column values between the
  current draft and baseline. Removed clean requirements, dirty affected removals,
  unrelated dirty values, and compatible preserved unsaved values are distinct.
- Model loading validates generation metadata before publishing the cached model
  object. DEV smoke artifacts carry the same bounded training contract.

## Verification

- Correction-focused coordinator, participant, Predict runtime, and standalone
  scenarios: `29 passed`.
- Mock Predict/Train artifact and generation-runtime integration: `36 passed`.
- Full repository suite: `2437 passed, 2 xfailed`.
- A/B behavior proves Derived, One-hot, ordered input, Target/result mapping, and
  zero-fill execution switch together only on commit and restore together on
  rollback. Predict edit/autofill/paste/add/delete/reset/running and Train
  path/replace/header/delete mutation scenarios reject stale commit.
- Definition controller/participant parity, exact Mapping review recomputation,
  real-participant happy path, injected commit failure, and reverse rollback pass.
- Windows-native Train/Predict/Mapping smoke was not run and remains pre-release
  verification. Phase 5 remains unimplemented.

## Invariants

No test or runtime transition promotes/replaces an active model. `mapping.json`
is unchanged except through explicit Mapping Save in the isolated reconciliation
test, and its fixture bytes are restored/removed by the smoke owner. No generic
transaction, event bus, IPC, watcher, or Phase 5 model workflow was introduced.
