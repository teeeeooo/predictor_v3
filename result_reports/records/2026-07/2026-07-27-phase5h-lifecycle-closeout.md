record:
  date: 2026-07-27
  topic: phase5h-lifecycle-closeout
  tags: train-admin, phase-5h, snapshot, confirmation, compatibility, retention
  memory_review: updated
  memory_reason: Phase 5H adds durable cross-owner lifecycle and authority contracts.
change_gate:
  new_source: split
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner

# Change Reason

Close the Phase 5G recommendation lifecycle with reproducible evidence,
independent fixed confirmation, exact user authority, historical readability,
and non-destructive migration/retention policy.

# Contract / Behavior Changed

Lifecycle closeout now owns canonical immutable snapshots and training-input
materialization, separate confirmation Candidates/history, single-use locked
final-test seals, and exact final decisions. Approved decisions reuse the
existing guarded promotion owner; recommendation and confirmation Candidates
cannot bypass confirmation/approval through generic promotion.

Historical readers distinguish executable, blocked, historical-only, future,
and corrupt evidence without applying new defaults. Migration and retention
are preview-only. Missing Predict leases, unknown references, unsupported
versions, and the current unindexed export boundary protect artifacts.

# Evidence And Verification

Deterministic isolated-root tests cover canonical snapshot identity, source
change survival, incomplete/non-finite/external-reference rejection,
single-use seals, compatibility/migration/retention fail-closed behavior,
all-Target fixed confirmation, partial failure, no automatic Active mutation,
exact approval routing, and stale revision blocking. Existing lifecycle and
Phase 5F/5G focused regression suites are retained.

# Changed Files

Common lifecycle closeout owners, Train confirmation application/composition,
shared headless and minimal GUI projections, fixed-parameter Core orchestration,
Predict loaded-model lease projection, tests, and authoritative current-state
documents.

# Known Risks

Deployment exports predate a lifecycle-root export index, so retention preview
deliberately reports an incomplete graph and no eligible deletion. Real
confirmation, migration apply, deletion, production promotion, and deployment
replacement remain separately authorized operations. Independent exact-head
audit is still required.
