record:
  date: 2026-07-29
  topic: phase5h-durable-execution-start-recovery
  tags: train-admin, phase-5h, audit-repair, execution-start, recovery, core-ack
  memory_review: updated
  memory_reason: The fourth Phase 5H audit failure and recoverable prepared-versus-started distinction supersede the prior fail-closed start-marker limitation.
change_gate:
  new_source: none
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner

# Change Reason

The fourth independent audit failed at exact head
`c58413cabfa005154c1a5b70d80f2a3a355431a6` despite successful historical
exact-head run `30375698091`. The start marker was written before the
`confirmation_running` history record, so a failure between those writes left
a pending confirmation that could never reacquire execution ownership. Earlier
audit failures and successful runs remain non-acceptance history.

# Contract / Behavior Changed

- Start preparation durably embeds and hashes the exact expected running
  transition. It is bound to the execution claim, confirmation identity, and
  canonical execution key but does not assert that training started.
- One execution-key OS lock serializes preparation, recovery, actual execution,
  and terminal handoff. Process termination releases the live owner without
  changing persisted evidence.
- A retry may recover `prepared + pending` by publishing the exact running
  transition, or `prepared + running` when actual-start evidence is absent.
  Concurrent retry therefore selects one execution owner and one running
  transition.
- The existing TrainingLifecycle Core-start acknowledgement writes separate
  immutable `execution_started` evidence after the durable Experiment run
  acknowledgement. Once present, duplicate training, locked evaluation, and
  Candidate publication are prohibited.
- Claim/preparation/running/acknowledgement identity, key, payload, or hash
  mismatch fails closed without a new confirmation or execution. Alternate
  caller IDs reconstruct the execution request with the claimed confirmation
  identity.
- Partial-claim recovery, locked finalization integrity, private staging,
  promotion/decision single-use, retention time invariance, and preview-only
  migration/retention behavior remain unchanged.

# Evidence And Verification

Direct failure injection writes preparation and then fails the running history
transition. Reconstructed implicit and alternate-ID retry recover the same
identity, publish one running transition, execute once, and replay without
increment. Concurrent recovery selects one owner. Corrupt preparation identity,
execution key, or running hash fails closed, while existing actual-start
evidence prevents duplicate execution. Focused confirmation, locked-test,
Candidate publication, promotion authorization, Experiment execution,
retention, and lifecycle validation are Worker evidence only; independent
exact-head re-audit remains mandatory.

# Changed Files

The correction stays within the existing closeout execution store,
confirmation execution contract/service, TrainingLifecycle confirmation
adapter, direct regressions, and authoritative Phase 5H state/history owners.

# Known Risks

The execution-key lock intentionally serializes duplicate retry until the live
owner reaches terminal handoff or its process exits. This favors at-most-once
execution over an immediate duplicate response. No production
confirmation/promotion, migration apply, retention/delete apply, deployment
mutation, merge, or audit acceptance was performed.
