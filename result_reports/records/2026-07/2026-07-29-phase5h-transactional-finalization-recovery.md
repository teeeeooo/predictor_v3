record:
  date: 2026-07-29
  topic: phase5h-transactional-finalization-recovery
  tags: train-admin, phase-5h, audit-repair, partial-claim-recovery, locked-finalization-fence
  memory_review: updated
  memory_reason: The third Phase 5H audit failure and its two transactional invariants are durable exact-head re-audit context.
change_gate:
  new_source: none
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner

# Change Reason

The third independent audit failed at exact head
`ae20c626a12c15906c5ffb9e4f159875418caed4` despite successful historical
exact-head run `30323789487`. A claim-only partial confirmation could not reach
recovery, and locked evidence was not completely revalidated after result
publication and immediately before public Candidate finalization. The two
earlier audit failures and runs remain historical non-acceptance evidence.

# Contract / Behavior Changed

- A versioned execution claim owns one confirmation identity, the exact
  canonical pending record, and its hash. Missing initial records and safe
  empty partial identity directories recover from that payload under the
  lifecycle writer lock. Claim/record version, hash, identity, bytes, or
  immutable execution disagreement fails closed.
- One durable start marker separates pending publication from execution.
  Process reconstruction, alternate IDs, ambiguous publication failure, and
  concurrent recovery therefore converge on one record and at most one
  training, locked evaluation, and Candidate publication.
- After staged training, seal consumption, locked evaluation, and immutable
  result publication, one finalization fence rechecks snapshot evidence,
  initial/consumed seal, dataset/membership, Target/split/evaluation policy,
  locked result, staged model/manifest hashes, and exact result linkage inside
  the shared Candidate writer. Only a passing fence can reach atomic public
  finalization.
- Fence failure keeps the seal consumed and failure evidence immutable while
  leaving Candidate inventory, Active, source Candidate, campaign,
  recommendation, leaderboard, and confirmation success linkage unchanged.
- Trusted authority, single-use decisions, orphan confirmation-Candidate
  promotion blocking, private staging, retention/migration preview-only
  behavior, and Python 3.11 compatibility remain required.

# Evidence And Verification

Direct failure injection covers claim success with missing or ambiguously
published initial record, reconstructed alternate-ID recovery, corrupt
claim/record bytes, concurrent recovery, and exact terminal replay. Locked
evidence injection covers dataset, membership, split, Target, seal-version, and
result drift plus the no-drift linkage path. Focused confirmation, locked-test,
Candidate publication, promotion authorization, and lifecycle suites, Python
3.11 parsing, structure/change/diff gates, and exact-head validation are Worker
evidence only; independent exact-head re-audit remains mandatory.

# Changed Files

The repair stays within the existing closeout contract/store, confirmation
execution/locked-evaluator, shared Candidate repository, direct regressions,
and authoritative Phase 5H state/history owners.

# Known Risks

A process that dies after the durable single-start marker cannot safely replay
the execution with the same identity; it remains fail-closed and requires
operator review rather than risking duplicate training or locked evidence.
No production confirmation/promotion, migration apply, retention/delete apply,
deployment mutation, merge, or audit acceptance was performed.
