# Train/Admin Phase 5B Malformed Active Recovery Repair

```yaml
record:
  date: 2026-07-25
  topic: train-admin-phase5b-malformed-active-recovery-repair
  tags: train-admin, phase-5b, audit-repair, active-recovery, malformed-json, evidence-preservation
  memory_review: updated
  memory_reason: The audit established malformed and non-object committed Active artifacts as a controlled recovery boundary that must preserve evidence without hiding programmer defects.
```

```yaml
change_gate:
  new_source: none
  hotspot_delta: none
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

## Change Reason

The independent audit of Draft PR #28 head
`e27f924675c7c516ae23a5ec66cee6687c97022e` remained `FAIL`. Committed
recovery could expose raw JSON parsing errors or an `AttributeError` when
`active_model.json` contained malformed JSON or a valid non-object JSON value.

## Contract / Behavior Changed

- The shared Active deserializer rejects non-object top-level payloads before
  field access and preserves all existing identity, revision, timestamp, and
  sequential-history validation.
- Committed recovery converts expected lifecycle filesystem, decoding, parsing,
  missing-field, schema, and Active contract corruption to
  `LifecycleRecoveryRequiredError`.
- Controlled failure preserves the recovery marker and backup, changes no Active
  revision/history, and returns the same recovery-required state on repetition.
- Unexpected programmer `AttributeError` is not classified as artifact
  corruption. Resolver status distinctions and normal committed forward
  reconciliation remain unchanged.

## Evidence And Verification

- Lifecycle/application/resolver/startup focused bundle: 68 passed.
- Canonical macOS/offscreen suite: 2531 passed, 2 xfailed.
- Structure guard: passed with 27 pre-existing unrelated soft warnings.
- Current repair and exact-base full-PR staged change gates: passed with no hard
  errors.
- Official GitHub check is required after push.
- Windows-native and packaging validation were not run and remain outside this
  repair acceptance.

## Changed Files

- Shared Active contract, committed recovery, and repository corruption boundary
- Focused malformed/non-object recovery, evidence-preservation, idempotency, and
  programmer-error regression tests
- Current work plan, project log, memory, index, and this repair record

## Known Risks

- Independent exact-head re-audit is still required. This record does not claim
  final Phase 5B PASS, merge readiness, or completion.
- Phase 5C and later UI/CLI/campaign/agent-loop work remain outside scope.
