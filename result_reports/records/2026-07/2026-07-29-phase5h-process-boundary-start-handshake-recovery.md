record:
  date: 2026-07-29
  topic: phase5h-process-boundary-start-handshake-recovery
  tags: train-admin, phase-5h, audit-repair, process-handshake, start-permit, recovery
  memory_review: updated
  memory_reason: The fifth Phase 5H audit exposed a cross-process start race that requires an attempt-bound durable permit before Core work.
change_gate:
  new_source: small
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner

# Change Reason

The fifth independent audit failed at exact head
`55141965c262bddd1fb1dd2b6692ed5bce99464d` despite successful historical
exact-head run `30413469249`. A confirmation child emitted the Core-start event
and immediately continued training while the parent had not yet persisted
durable start evidence. Parent exit in that window could let retry launch a
second child. Earlier audit failures and successful runs remain non-acceptance
history.

# Contract / Behavior Changed

- Confirmation-only training requests carry a versioned handshake bound to
  confirmation identity, canonical execution key, unique launch attempt,
  expected training meaning hash, and exact durable permit path.
- The closeout owner immutably registers each attempt under the existing
  execution-key ownership. The child emits a structured start request at the
  Core work callback and blocks until the parent publishes its exact permit.
- The adapter validates child transport against its frozen request before the
  application may grant a permit. The child validates every permit field before
  it emits `training_started` and returns to actual work.
- Parent exit before permit leaves actual work unstarted and allows one new
  attempt. A stale child rejects a replacement permit. Once a permit exists,
  automatic rerun is prohibited even when the original child's result is
  ambiguous; the existing confirmation remains running/recovery-required.
- Corrupt attempt, execution key, confirmation, protocol, training meaning, or
  permit fails closed without Candidate or Active mutation. Non-confirmation
  training retains the existing no-handshake behavior.

# Evidence And Verification

Actual `SubprocessTrainingRunner` and `train_job` failure injection verifies
that no work-boundary marker or artifact appears without a permit, exact permit
allows one execution, stale and corrupt permits do not start work, and ordinary
training remains unchanged. QProcess transport verifies the same exact permit
request. A real headless confirmation completes child training and publishes
one Candidate. Application recovery tests cover pre-permit reconstruction,
post-permit no-rerun, alternate IDs, concurrent ownership, and corrupt durable
evidence. Adjacent locked finalization, promotion, decision, retention,
Experiment, and lifecycle tests remain Worker evidence only; independent
exact-head re-audit remains mandatory.

# Changed Files

The correction stays within the closeout start protocol/store, immutable
training request and execution port, QProcess/subprocess/job transport,
confirmation/Experiment orchestration, direct regressions, and authoritative
Phase 5H history owners.

# Known Risks

Post-permit parent failure intentionally favors at-most-once execution over
automatic availability. Operator recovery remains outside this Phase; no
rerun/override authority was added. No production confirmation/promotion,
migration apply, retention/delete apply, deployment mutation, merge, or audit
acceptance was performed.
