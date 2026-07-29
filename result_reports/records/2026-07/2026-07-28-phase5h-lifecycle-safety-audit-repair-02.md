record:
  date: 2026-07-28
  topic: phase5h-final-lifecycle-safety-audit-repair
  tags: train-admin, phase-5h, audit-repair, confirmation-idempotency, retention-invariance, prepublication-integrity
  memory_review: updated
  memory_reason: The second Phase 5H audit failure and final three lifecycle repair invariants are durable re-audit context.
change_gate:
  new_source: none
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner

# Change Reason

The second independent audit failed at exact repaired head
`97914c0285c7155ecfbd6da1fb9fa1d7c60f24a7` despite successful historical
run `30286229720`. Three reproduced lifecycle findings remained merge blockers.
The first audit failure and its ten repaired findings remain historical
evidence.

# Contract / Behavior Changed

- Confirmation starts derive one content-addressed execution key from immutable
  snapshot, mode, seal, Target, policy, and training-semantic meaning. A durable
  writer-locked claim makes implicit, alternate-ID, concurrent, pending,
  running, terminal, and reconstructed retries resolve to one execution.
- Retention inventory uses persisted timestamps or stable `unknown` values.
  Synthetic nodes, conservative age eligibility, and lease projection no longer
  include the process clock in preview identity or bytes.
- Confirmation Candidate evidence is completed in private staging. Configured
  locked evaluation, complete snapshot revalidation, and generated-Candidate
  validation execute inside the shared lifecycle writer lock before atomic
  public finalization. Failure publishes no discoverable Candidate or success
  link.
- Trusted authority, single-use decision/promotion, consumed-seal behavior,
  orphan-Candidate promotion blocking, complete retention references, and
  migration preview invariance remain unchanged.
- Production confirmation/promotion, migration apply, deletion, cleanup, merge,
  and audit acceptance remain outside Worker authority.

# Evidence And Verification

Direct adversarial regressions cover implicit, alternate-ID, concurrent and
reconstructed confirmation starts; empty and populated retention inventory
under different clocks; state-change identity; four captured-evidence drift
classes; and publication-guard ordering before Candidate visibility. Focused
confirmation, locked-test, promotion, Experiment, Candidate publication,
migration, retention, and lifecycle validation passed. Python 3.11 parsing,
diff/structure/change gates, and the new exact-head CI run are recorded in the
Worker handoff; independent exact-head re-audit remains mandatory.

# Changed Files

The repair stays within existing closeout store/contracts, confirmation and
retention application owners, shared TrainingLifecycle/CandidatePublisher
finalization, direct regressions, and authoritative Phase 5H state/history
documents.

# Known Risks

Deployment exports still lack a lifecycle-root index, so retention remains
deliberately incomplete and non-destructive. Age-based eligibility remains
conservatively blocked without an immutable policy-as-of input. No actual
user-data or production lifecycle operation was executed.
