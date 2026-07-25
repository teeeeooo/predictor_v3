# Train/Admin Phase 5B Final Bounded Audit Repair

```yaml
record:
  date: 2026-07-25
  topic: train-admin-phase5b-final-bounded-audit-repair
  tags: train-admin, phase-5b, audit-repair, active-recovery, qprocess, resolver, ci
  memory_review: updated
  memory_reason: The audit established committed Active forward reconciliation, explicit Qt fixture ownership, and a narrow startup exception boundary as durable Phase 5B requirements.
```

```yaml
change_gate:
  new_source: none
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

## Change Reason

Audit of Draft PR #28 head
`f944cbc6d40a36db94a599462bb2cdcc21ce2265` remained `FAIL`. A durable new
Active revision could be treated as the previous revision when backup cleanup
failed or remain permanently recovery-required when marker cleanup failed. The
root autouse QApplication fixture also imported PySide6 in non-Qt CI, and the
Active resolver converted unexpected programmer errors to `invalid-active`.
Earlier head counts remain historical and superseded for current acceptance.

## Contract / Behavior Changed

- Active recovery records `committed` durably before cleanup. Backup or marker
  cleanup failure reports the actual committed revision, and reconciliation
  verifies then preserves that pointer/history before removing rollback
  evidence. Repeated reconciliation creates no revision or history entry.
- Pre-commit and indeterminate post-rename failures retain rollback-first
  behavior. Expected revision remains mandatory for promotion and rollback.
- The session QApplication fixture is no longer autouse. Only explicit
  Qt/QProcess tests request it, so non-Qt collection and execution do not import
  PySide6.
- The startup resolver controls recovery-required, lifecycle corruption,
  missing Candidate, integrity, and expected filesystem failures. Unexpected
  `AssertionError` and contract-defect `TypeError` propagate.
- Parent-root symlink hardening and arbitrary QCore-first QWidget construction
  remain non-blocking exclusions, not new product requirements.

## Evidence And Verification

- Expanded lifecycle/application/QProcess focused bundle: 68 passed.
- QProcess success, starting/running cancellation, launch failure, and cleanup:
  4 passed in each of five consecutive runs.
- PySide6-blocked non-Qt CI simulation of the previously failing AHRI test:
  1 passed.
- Canonical macOS/offscreen suite: 2514 passed, 2 xfailed.
- Structure guard: passed with 27 pre-existing unrelated soft warnings.
- Current repair staged change gate: passed. Exact 54-path full-PR staged change
  gate: passed with four warning-first new-source size findings already covered
  by the existing owner split.
- No running training/mock child or repository-local lifecycle lock, recovery
  marker, Active temporary/backup, Candidate model binary, or mock lifecycle
  state remained after validation.
- Windows-native and packaging validation were not run and remain outside this
  repair acceptance.

## Changed Files

- Active durability error, recovery, repository, promotion, and resolver owners
- focused Active cleanup/reconciliation and resolver exception-boundary tests
- explicit Qt fixture ownership
- current work plan, project log, memory, index, and this correction record

## Known Risks

- Independent exact-head re-audit is still required. This record does not claim
  final Phase 5B PASS, merge readiness, or completion.
- Official GitHub check evidence is pending the repair push.
- Windows-native locking and executable packaging remain unverified.
- Phase 5C analysis artifacts and later UI/CLI/campaign/agent-loop work remain
  outside scope.
