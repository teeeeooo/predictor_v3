# Train/Admin Phase 5B Independent-Audit Repair

```yaml
record:
  date: 2026-07-23
  topic: train-admin-phase5b-audit-repair
  tags: train-admin, phase-5b, audit-repair, filesystem-ownership, stale-guard, legacy-migration, qprocess
  memory_review: updated
  memory_reason: The independent audit invalidated earlier Phase 5B acceptance evidence and established durable repair and re-audit requirements.
```

```yaml
change_gate:
  new_source: split
  hotspot_delta: wiring-only
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

## Change Reason

Independent audit of PR #28 head
`61856fe47dab2ea32aa9315c85c450b5ed5f466a` found merge-blocking
filesystem-ownership, stale-write, legacy-corruption, and QProcess cancellation
defects. This audit FAIL supersedes the earlier record's local PASS counts as
Phase 5B acceptance evidence.

## Contract / Behavior Changed

- Lifecycle filesystem operations reject symlinked/non-regular staging,
  Candidate, model, metadata, pointer, and lock objects and validate lexical and
  resolved workspace ownership before publication or reading.
- Promotion, rollback, first activation, and legacy continuity require an
  explicit non-null current Active revision. Stale writes preserve identity,
  revision, and history.
- Known corruption in an existing deterministic legacy Candidate returns a
  structured retraining-required outcome, preserves the original legacy model,
  creates no duplicate Candidate/history, and does not crash Train or Predict
  startup.
- QProcess cancellation wins accepted cancel/error/finished races and emits one
  consistent `cancelled` terminal callback. Genuine launch failure remains
  `failed`; process and timer cleanup precede the callback.
- Phase 5C remains unstarted and Phase 5B remains awaiting independent exact-head
  re-audit.

## Evidence And Verification

- QProcess focused: 4 passed per run across five consecutive independent runs.
- Lifecycle/application focused: 48 passed.
- Dependency/composition focused: 12 passed.
- Canonical macOS/offscreen pytest: 2498 passed, 2 xfailed.
- Structure guard: passed; 27 pre-existing unrelated soft warnings remain.
- Staged change gate: passed.
- Windows-native and packaging validation were not run and remain outside this
  repair acceptance.

## Changed Files

- lifecycle filesystem, Candidate validation, repository, promotion, migration,
  and contracts under `apps/common/model_lifecycle/`
- QProcess command/terminal helpers, runner, and training staging cleanup
- adversarial filesystem, revision competition, corrupt migration/startup, and
  signal-driven QProcess tests
- architecture, current plan/state, project log, memory, index, and this
  correction record

## Known Risks

- Independent exact-head re-audit is still required; this record does not claim
  merge-ready or final Phase 5B PASS.
- Windows-native and packaging behavior remains unverified in this repair.
- Phase 5C analysis artifacts and later UI/CLI/campaign/agent-loop work remain
  outside scope.
