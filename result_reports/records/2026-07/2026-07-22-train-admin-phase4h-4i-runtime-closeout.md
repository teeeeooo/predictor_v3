# Train/Admin Phase 4H+4I Runtime Cutover Closeout

record:
  date: 2026-07-22
  topic: train-admin-phase4h-4i-runtime-closeout
  tags: train-admin, phase-4h, phase-4i, generation, cutover, mapping, standalone-predict, closeout
  memory_review: updated
  memory_reason: Phase 4 runtime generation ownership and the Phase 5 transition are now implemented rather than proposed.

change_gate:
  new_source: split
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner

## Change Reason

Immutable generation publication did not atomically advance all TrainShell
consumers, dirty Mapping drafts had no explicit pending-generation workflow, and
standalone Predict could execute against a stale persisted contract.

## Contract / Behavior Changed

- A UI-neutral coordinator freezes one repository snapshot, prepares all required
  participants without active mutation, rechecks pointer and revision evidence,
  and commits or rolls back as one process transition.
- Data Definition, embedded Predict, Train / Model, and Data Mapping report one
  active generation after success. Failure retains A or reports Restart required.
- Predict migrates case values by stable Feature identity, retains result rows,
  and classifies promoted-model metadata without replacing the artifact.
- Dirty Mapping retains draft, baseline, values, and history while exposing Review
  Update, Save Mapping, and Discard and Reload. Definition never writes concrete
  Mapping values.
- Standalone Predict checks generation at startup, explicit Refresh, and prediction
  boundaries. Failed reload preserves state and blocks new prediction.
- Model-incompatible Definition generations may publish and apply, but prediction
  remains retraining-required until compatibility is proven.

## Evidence And Verification

- Focused Phase 4H coordinator/participant/standalone tests cover happy path,
  failure rollback, stale evidence, selected training-header validation, state
  preservation, and recovery actions: `27 passed`.
- Full repository suite: `2413 passed, 2 xfailed`.
- Python compile gate: passed for `apps`, `core`, and `tests`.
- Staged change gate and diff check: passed. Structure guard: passed with 26
  warning-only existing/changed hotspots and no errors. GitHub CI evidence is
  recorded in the Draft PR body after publication.
- Windows-native Train/Predict/Mapping smoke was not run and remains pre-release.

## Changed Files

Shared runtime generation contracts/repository, Train coordinator and participants,
Predict reload participant/guard, Mapping staging boundary, shell recovery/status
adapters, focused tests, and Phase 4 owner/closeout documents.

## Known Risks

- Cross-process simultaneous atomic commit is intentionally not provided; each
  standalone process validates at its own execution boundary.
- Legacy or incomplete model metadata remains conservatively retraining-required.
- Existing UI/service hotspot warnings remain warning-first; new multi-owner logic
  is isolated in feature packages, while small wiring methods stay with their
  established state owners.
