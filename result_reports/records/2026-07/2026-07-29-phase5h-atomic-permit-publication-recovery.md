record:
  date: 2026-07-29
  topic: phase5h-atomic-permit-publication-recovery
  tags: train-admin, phase-5h, audit-repair, start-permit, atomic-publication, durability
  memory_review: updated
  memory_reason: The sixth Phase 5H audit exposed a final-path durability boundary whose pre-commit and post-commit states must be structurally distinguishable.
change_gate:
  new_source: small
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner

# Change Reason

The sixth independent audit failed at exact head
`7175060236ede4596246f64f6acf0d1b932075ca` despite successful historical
exact-head run `30416243161`. The handshake store created the final permit path
before writing its JSON bytes, so process failure could leave an empty or
partial file that retry interpreted as irreversible actual-start evidence.
Earlier audit failures and successful runs remain non-acceptance history.

# Contract / Behavior Changed

- The closeout handshake owner serializes canonical permit bytes into a unique
  attempt-private temporary artifact, flushes and fsyncs the file, and verifies
  its exact bytes before publication.
- One same-directory atomic hard-link commit exposes the complete permit at an
  absent final path without clobbering, followed by containing-directory fsync.
  Existing shared callers retain their prior publication behavior.
- Failure before final commit leaves no final permit. Temporary residue is not
  child-visible start evidence and does not block a reconstructed service from
  registering one replacement attempt under the same confirmation identity.
- Failure after commit leaves a complete verifiable permit and therefore
  preserves the at-most-once boundary. Retry does not infer that ambiguity is
  safe to rerun.
- Exact concurrent publishers converge on one permit. Conflicting concurrent
  payload, malformed final bytes, identity/version/hash mismatch, and later
  tampering are preserved and fail closed rather than being deleted or
  overwritten.

# Evidence And Verification

Direct failure injection covers temporary creation, partial byte write,
pre-flush/fsync, post-file-fsync/pre-commit, and immediate post-commit parent
failure. It verifies final-path invisibility before commit, stale temporary
residue tolerance, one replacement subprocess execution, post-commit no-rerun,
single-winner exact concurrency, conflicting concurrency, and tamper
rejection. Actual subprocess and QProcess handshake paths, ordinary
non-confirmation training, prepared-state recovery, terminal replay, locked
finalization, Candidate publication, promotion authorization, and retention
contracts remain covered by focused adjacent suites. Independent exact-head
re-audit remains mandatory.

# Changed Files

The correction stays within the lifecycle filesystem and confirmation
start-permit publication owners, closeout store wiring, direct regressions, and
authoritative Phase 5H current-state/history documents.

# Known Risks

Post-commit parent failure intentionally favors at-most-once execution over
automatic availability. The atomic commit relies on the repository's
same-filesystem lifecycle root and filesystem support for exclusive hard-link
publication; failures preserve evidence and fail closed. No production
confirmation/promotion, migration apply, retention/delete apply, deployment
mutation, merge, or audit acceptance was performed.
