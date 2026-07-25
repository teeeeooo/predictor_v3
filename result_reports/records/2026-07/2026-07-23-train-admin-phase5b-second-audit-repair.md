# Train/Admin Phase 5B Second Independent-Audit Repair

```yaml
record:
  date: 2026-07-23
  topic: train-admin-phase5b-second-audit-repair
  tags: train-admin, phase-5b, audit-repair, durability, recovery, root-race, qprocess
  memory_review: updated
  memory_reason: The second audit invalidated the first repair evidence and established the lifecycle durability and Qt application-ownership recovery contract.
```

```yaml
change_gate:
  new_source: split
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

## Change Reason

The second independent audit of Draft PR #28 head
`6fb25e86b1e420f18ff98b60b1dc7ac5acbf8045` remained `FAIL`. It found a
lifecycle-root replacement race before lock creation, post-rename Candidate and
Active durability outcomes that could disagree with visible repository state,
and canonical-order QProcess failures. The original implementation and first
repair validation counts remain historical evidence only and are superseded for
current acceptance by this record.

## Contract / Behavior Changed

- POSIX/macOS lock creation is relative to an identity-checked lifecycle-root
  descriptor. Replacing the validated root with an external symlink before lock
  creation fails closed without writing the external lock path; the Windows lock
  path and native locking branch remain intact.
- Candidate and Active mutations use the same outcome principle without one
  cross-domain transaction: pre-rename failure preserves prior state;
  post-rename durability failure rolls back; failed rollback retains a recovery
  marker and returns `recovery-required`.
- Candidate recovery markers hide indeterminate final directories from
  list/read. Active recovery markers block normal pointer resolution. Explicit
  repository reconciliation restores Candidate staging or the previous Active
  pointer/history before clearing the marker.
- Active history remains embedded in the atomic revisioned pointer, so pointer
  and history are replaced and recovered as one unit. Mandatory revision guards
  remain unchanged.
- QProcess tests keep one session-lifetime `QApplication`, wait on terminal
  signals, and cancel/reap on timeout. Runner disposal synchronously kills and
  reaps any remaining child; mock shell teardown deletes the shell before exit.
- Phase 5C remains unstarted and this worker evidence is not an independent
  audit PASS or merge-ready decision.

## Evidence And Verification

- Adversarial/fault-injection plus QProcess focused bundle: 64 passed.
- QProcess focused repetition: 4 passed in each of five independent runs.
- Previously failing three-test bundle: 3 passed in each of five runs.
- Lifecycle/application focused: 55 passed.
- Dependency/startup focused: 15 passed.
- Canonical macOS/offscreen suite: 2509 passed, 2 xfailed.
- Structure guard: passed with 27 pre-existing unrelated soft warnings.
- Exact full-PR staged change gate: passed with the selected current report and
  explicit reuse/commonization decision.
- No repository-local lifecycle lock, recovery marker, Candidate model binary,
  mock lifecycle state, or running training child remained after validation.
- Windows-native and packaging validation were not run and remain outside this
  repair acceptance.

## Changed Files

- lifecycle filesystem, lock, durability errors, recovery owner, repository,
  promotion/resolution contracts, and training publication handling
- adversarial root-race, post-rename rollback/recovery, revision/history, and
  structured outcome tests
- QProcess runner disposal, shared Qt test application ownership, terminal wait
  cleanup, and mock shell cleanup
- current plan/state, project log, memory, index, and this correction record

## Known Risks

- Independent exact-head re-audit is still required; this record does not claim
  final Phase 5B PASS, merge readiness, or completion.
- Windows-native locking and executable packaging remain unverified.
- Candidate management UI, Phase 5C analysis artifacts, Predict reload UI,
  CLI/campaign/agent-loop, retention/delete, and deployment export remain out of
  scope.
