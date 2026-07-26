---
record:
  date: 2026-07-26
  topic: phase5f-core-ack-retry-compatibility-audit-repair
  tags: train-admin, phase-5f, audit-repair, core-training-start, retry-exhaustion, compatibility
  memory_review: updated
  memory_reason: The second Phase 5F audit failure and its three bounded lifecycle repairs are durable exact-head re-audit context.
change_gate:
  new_source: none
  hotspot_delta: wiring-only
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
---

# Phase 5F Core Acknowledgement, Retry, And Compatibility Audit Repair

## Change Reason

The second independent audit returned `FAIL` at exact head
`e5558e82d7ca736bb45ca71eb94ab83b71a19950`. Validation run `30195511666`
had succeeded but did not close three remaining campaign lifecycle defects.
The first failed head and validation run remain unchanged historical evidence.

## Contract / Behavior Changed

- Training start is acknowledged inside the Core optimization owner after
  configuration plus data/pipeline preflight and immediately before
  RFECV/Optuna/training work. The child job and adapters only transport that
  owner event. Duplicate delivery cannot consume an iteration twice.
- `max_attempts` includes the initial attempt and is the total allowance for one
  iteration across all resume calls. Pre-start failure consumes an attempt but
  no iteration. Exhausted resume returns `campaign_retry_exhausted` without
  starting execution or changing persisted campaign, run, Candidate, or Active
  state.
- Identified revision mismatch, clean/dirty mismatch, missing identity, lookup
  failure, and uncertain identity all return detached compatibility outcomes.
  They do not rewrite saved campaign or run evidence.

## Evidence And Verification

- The focused Phase 5F specification/campaign/headless suite passes `40` tests,
  including Core preflight versus training boundary, post-ack failure,
  cancellation, duplicate acknowledgement, one/three-attempt exhaustion, and
  byte-identical compatibility blocks.
- Adjacent lifecycle, production result, writer-lock, and GUI status suites pass
  `81` tests.
- Required exact-head validation and independent re-audit remain the next gate.

## Known Risks

- Full historical compatibility, immutable snapshots, final confirmation, and
  retention remain Phase 5H.
- This worker does not declare audit PASS or merge PR #33. Phase 5G and Phase 5H
  remain unstarted.
