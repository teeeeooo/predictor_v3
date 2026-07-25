# Train/Admin Phase 5C Canonical Artifact And Failure-Evidence Repair

```yaml
record:
  date: 2026-07-25
  topic: train-admin-phase5c-canonical-artifact-failure-evidence-repair
  tags: train-admin, phase-5c, audit-repair, canonical-path, strict-types, failure-evidence
  memory_review: updated
  memory_reason: The second Phase 5C audit FAIL and the canonical identity plus non-destructive failure-evidence boundaries are durable final re-audit context.
change_gate:
  new_source: split
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

## Change Reason

The second independent L4 audit of PR #30 returned `FAIL` for three direct
blockers: normalized path aliases could identify one artifact twice, persisted
reference fields were coerced by truthiness/string conversion, and Candidate
publication failures could lose the already-produced Core target evidence.
Both earlier audit verdicts and Worker records remain historical.

## Contract / Behavior Changed

- Manifest v2 and structured result references now share canonical
  POSIX-relative artifact identity validation. Absolute, empty, traversal,
  outside-namespace, dot-segment, repeated-separator, trailing-separator, and
  backslash spellings are rejected rather than normalized.
- Persisted `path`, `category`, `required`, and manifest SHA-256 fields use
  strict raw JSON types and formats. String/numeric/null/container substitutes
  are controlled corruption, not coerced values.
- Successful publication retains original Core evidence as an optional,
  hash-validated Candidate-owned artifact while the required artifact set
  remains exactly nine. Artifact generation/readback, lifecycle validation,
  atomic publication, and recovery-required failures preserve original target
  identities, status, metrics, Core reasons, and exact publication stage/reason
  in immutable run evidence while Active and existing Candidates remain
  unchanged.
- Terminal evidence first retains the full derived report path. If that writer
  remains unavailable, a separate adapter writes truthful minimal JSON only,
  marks fallback mode, and does not claim absent CSV/XLSX artifacts.

## Evidence And Verification

- Canonical alias, strict type/format, failure preservation, prior lifecycle,
  production integration, Train/Predict boundary focused suite: 201 passed.
- Canonical full suite: 2608 passed, 2 xfailed.
- Failure regressions cover persistent writer failure, lifecycle hash rejection,
  pre-rename atomic publication failure, and recovery-required publication.
  Each retains original successful-target metrics and Core reasons, records the
  actual failure stage/reason, preserves Active identity/revision/history, and
  leaves no incomplete visible Candidate or unowned terminal staging.
- Structure validation has no new warning; existing repository soft warnings
  remain unchanged.
- Official exact-head GitHub validation is recorded in the Draft PR after push.

## Changed Files

- lifecycle Candidate reference parser, canonical identity, validation error,
  and publication validation boundary
- shared structured result parser
- Train evidence/artifact ports, filesystem adapters, publication service, and
  terminal fallback policy
- direct canonical/type/failure evidence regressions and adjacent lifecycle,
  production, Train, and Predict coverage
- current work-plan, design-set status, project log, index, and memory owners

## Known Risks

- Recovery-required publication retains the existing Phase 5B recovery marker
  semantics; evidence preservation does not silently resolve or activate the
  hidden Candidate.
- This worker does not declare audit `PASS`, merge, or start Phase 5D, CLI,
  Campaign, leaderboard, or the agent loop.
