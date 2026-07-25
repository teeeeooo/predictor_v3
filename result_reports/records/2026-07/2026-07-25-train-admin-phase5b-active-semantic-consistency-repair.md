# Train/Admin Phase 5B Active Semantic Consistency Repair

```yaml
record:
  date: 2026-07-25
  topic: train-admin-phase5b-active-semantic-consistency-repair
  tags: train-admin, phase-5b, audit-repair, active-reference, semantic-consistency, recovery
  memory_review: updated
  memory_reason: The audit established Active current/history semantic equality and intended Candidate identity as durable committed-recovery requirements.
```

```yaml
change_gate:
  new_source: none
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

## Change Reason

The independent audit of Draft PR #28 head
`7ac586a7610b02cfd1cb4b47d72bec7a70481a23` remained `FAIL`. An Active
payload could present Candidate B at revision 2 while its latest history record
presented Candidate A at revision 2, and committed recovery compared only the
revision before deleting marker/backup evidence. Earlier validation remains
historical evidence rather than current acceptance.

## Contract / Behavior Changed

- Active deserialization validates one semantic revision unit: history starts at
  revision 1 and increases without duplicate, reversal, or gap; every Candidate
  identity is path-safe; and top-level identity, revision, and activation time
  exactly match latest history.
- Empty, malformed, unsupported-schema, unsafe-identity, and semantically
  inconsistent Active payloads raise the existing dedicated Active corruption
  boundary and resolve as controlled `invalid-active`.
- New recovery markers carry intended Candidate identity as well as intended
  revision. Committed forward reconciliation validates the complete Active
  contract and both marker bindings before cleanup.
- Corrupt Active state or marker/current identity mismatch remains
  `recovery-required` and preserves marker and backup evidence.
- Normal promotion, rollback, mandatory expected-revision guards, forward
  cleanup reconciliation, and idempotent repeated recovery remain unchanged.
- Previous Qt/QProcess, non-Qt CI, legacy fail-closed, and narrow resolver
  exception-boundary repairs remain intact.

## Evidence And Verification

- Lifecycle/application/QProcess focused bundle: 81 passed.
- QProcess success, starting/running cancellation, launch failure, and cleanup:
  4 passed in each of five consecutive runs.
- PySide6-blocked non-Qt CI simulation of the previously failing AHRI test:
  1 passed.
- Canonical macOS/offscreen suite: 2527 passed, 2 xfailed.
- Structure guard: passed with 27 pre-existing unrelated soft warnings.
- Current 9-path repair staged gate: passed. Exact 55-path full-PR staged gate:
  passed with four warning-first source-size findings and no hard errors.
- No running training/mock child or repository-local lifecycle lock, recovery
  marker, Active temporary/backup, Candidate model binary, or mock lifecycle
  state remained after validation.
- Official GitHub check is required after push.
- Windows-native and packaging validation were not run and remain outside this
  repair acceptance.

## Changed Files

- Active reference contract validation, repository deserialization, and
  committed recovery identity binding
- focused semantic-corruption, evidence-preservation, recovery, promotion, and
  rollback regression tests
- current work plan, project log, memory, index, and this correction record

## Known Risks

- Independent exact-head re-audit is still required. This record does not claim
  final Phase 5B PASS, merge readiness, or completion.
- Official GitHub check evidence is pending the repair push.
- Windows-native locking and executable packaging remain unverified.
- Phase 5C and later UI/CLI/campaign/agent-loop work remain outside scope.
