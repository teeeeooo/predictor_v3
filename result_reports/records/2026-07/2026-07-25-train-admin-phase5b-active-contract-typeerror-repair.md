# Train/Admin Phase 5B Active Contract TypeError Repair

```yaml
record:
  date: 2026-07-25
  topic: train-admin-phase5b-active-contract-typeerror-repair
  tags: train-admin, phase-5b, audit-repair, active-contract, typeerror, recovery
  memory_review: updated
  memory_reason: The audit established that payload type corruption must be explicit contract validation while unrelated contract TypeError remains a visible programmer failure.
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
`af7d789dd8f7e8c8aa9a55825747571cb461c7b2` remained `FAIL`. Repository
Active reads and committed recovery caught every `TypeError`, including
unrelated failures raised inside the shared Active contract implementation.

## Contract / Behavior Changed

- The shared Active contract explicitly validates top-level required fields,
  history container shape, history-record mappings, and required record fields
  before constructing domain records.
- Malformed payload shape and field types continue through the existing
  controlled Active corruption boundary.
- Repository Active reads, resolver calls, and committed recovery no longer
  classify unrelated contract `TypeError` as artifact corruption.
- Programmer failure during committed recovery preserves marker, backup, and
  Active bytes and performs no cleanup or revision/history mutation.
- Malformed/non-object JSON, identity/history mismatch, marker binding, normal
  forward reconciliation, and repeated reconciliation remain unchanged.

## Evidence And Verification

- Lifecycle/repository/resolver/startup/application focused bundle: 71 passed.
- Canonical macOS/offscreen suite: 2534 passed, 2 xfailed.
- Structure guard: passed with 27 pre-existing unrelated soft warnings.
- Current repair and exact-base full-PR staged change gates: passed with no hard
  errors.
- Official GitHub check is required after push.
- Windows-native and packaging validation were not run and remain outside this
  repair acceptance.

## Changed Files

- Shared Active payload contract and repository/recovery expected-error boundaries
- Focused payload-shape and real contract-call programmer-error regressions
- Current work plan, project log, memory, index, and this repair record

## Known Risks

- Independent exact-head re-audit is still required. This record does not claim
  final Phase 5B PASS, merge readiness, or completion.
- Phase 5C and later UI/CLI/campaign/agent-loop work remain outside scope.
