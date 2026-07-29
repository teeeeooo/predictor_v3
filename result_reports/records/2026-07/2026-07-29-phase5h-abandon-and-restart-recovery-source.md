record:
  date: 2026-07-29
  topic: phase5h-abandon-and-restart-recovery-source
  tags: train-admin, phase-5h, recovery-source, abandon, liveness-fence, locked-seal
  memory_review: updated
  memory_reason: The approved recovery decision now has a bounded process-lifetime fence and source-complete lifecycle implementation.

change_gate:
  new_source: split
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner

# Change Reason

The user-approved abandon-and-restart decision required source enforcement
before another independent audit. A permit alone could not distinguish a live
child from a terminated attempt, while permanent post-permit blocking
prevented safe sequential recovery after proven termination.

# Contract / Behavior Changed

- A confirmation child acquires an exact attempt-specific lifecycle lock
  before its start request and holds it until process exit.
- Recovery remains under the existing execution-key and lifecycle writers.
  A live or uncertain lock blocks replacement; a successfully acquired lock is
  held through immutable attempt abandonment before one replacement is
  registered.
- Each replacement owns a new run, permit, post-durability grant, liveness
  lock, and private staging identity. Stale attempts cannot use replacement
  authority or enter Candidate publication.
- Pre-seal failure abandons only the ended attempt and retrains from the
  beginning. Consumed-seal failure without complete official finalization
  makes the whole Confirmation terminal `abandoned`.
- Success-like terminal replay requires the exact durable public Candidate and
  manifest linkage. Corrupt or missing persisted evidence fails closed.

# Evidence And Verification

Actual subprocess coverage holds a child at its start request, proves that
reconstructed recovery cannot replace it, terminates it without Core work, and
then completes exactly one replacement. QProcess coverage verifies exact
post-durability grant transport. Direct tests also cover sequential and
concurrent recovery, corrupt liveness/permit evidence, stale callbacks,
atomic permit crash windows, consumed-seal abandonment, terminal replay, and
ordinary non-confirmation training. Materially adjacent lifecycle, locked
finalization, Candidate publication, promotion authorization, and retention
tests remain in the focused validation set.

# Changed Files

Lifecycle closeout contracts/store/locking, confirmation orchestration,
training subprocess and QProcess adapters, child start boundary, direct
regressions, and authoritative Phase 5H current-state/history documents.

# Known Risks

The process-lifetime fence depends on the existing cross-platform advisory
locking primitive. An OS/filesystem error is intentionally treated as
live-or-unknown and fails closed. No daemon, process adoption, partial-artifact
resume, destructive cleanup, production confirmation/promotion, migration
apply, or retention/delete apply is introduced. Fresh independent exact-head
audit is still required. The closeout store and confirmation application remain
large existing hotspots, but attempt persistence stays inside the store's
shared writer transaction and recovery sequencing stays inside the current
application owner; the child authorization mechanism was split into a bounded
confirmation-only job gate rather than adding more process logic to
`train_job.py`.
