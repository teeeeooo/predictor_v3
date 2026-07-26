# Phase 5E Refresh Ordering And UI Failure Boundary Audit Repair

```yaml
record:
  date: 2026-07-26
  topic: phase5e-refresh-ordering-ui-failure-boundary-repair
  tags: train-admin, phase-5e, audit-repair, refresh-ordering, stale-callback, export-boundary
  memory_review: updated
  memory_reason: The second Phase 5E audit exposed durable ordering and UI exception-boundary rules needed for every lifecycle observation.
change_gate:
  new_source: none
  hotspot_delta: none
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

## Change Reason

The second independent Phase 5E L4 audit returned `FAIL` at exact head
`f22d6e9526bc3c31d0775123a9614b860fadbf5b`. It found that ordinary refresh
could bypass reload ordering, stale UI completion could trigger another
unguarded refresh, prediction-running UI bypassed structured guidance, and an
unexpected export exception could escape the UI event boundary. Earlier audit
verdicts and successful validation runs remain historical evidence.

## Contract / Behavior Changed

- Every refresh and reload begins one monotonic application-owned status
  observation. Observation is published only if it is still current after the
  repository read; stale callers retain their result without changing shared
  status.
- UI refresh and reload callbacks reject stale operation identities and render
  the application owner's read-only authoritative current status without
  starting another refresh.
- Prediction-running reload reaches the command boundary and returns the same
  structured cause, loaded-model preservation, and retry guidance as other
  reload failures.
- Unexpected export exceptions are normalized at application/controller
  boundaries, with UI event containment as a final guard. Default messages
  preserve Active, Candidate, and existing export facts while raw exception and
  traceback remain in diagnostics.

## Evidence And Verification

- Exact real-repository regressions cover A loaded, A/B refresh observation
  blocked, C promotion, and newer C reload success or structured incompatibility
  failure before the stale refresh resumes.
- A blocked B reload followed by current C incompatibility failure leaves the C
  failure category and guidance authoritative when B completes stale. UI guards
  cover stale success, failure, and refresh callbacks.
- Prediction-running UI guidance and unexpected export exception containment,
  redaction, diagnostics, lifecycle/history/export immutability, and residue
  cleanup are covered by focused tests.
- Focused Phase 5E ordering/UI/export regression: 144 passed.
- Full canonical repository suite: 2677 passed, 2 expected xfailed.

## Changed Files

- Predict lifecycle application owner, controller, and thin UI adapter
- deployment-export outcome, Train application/controller, and UI boundaries
- focused ordering, structured guidance, export containment, and invariance tests
- architecture/current-state/log/memory owners and this indexed record

## Known Risks

- The new repaired head has no independent L4 verdict. Draft PR #32 remains
  open and unmerged for exact-head re-audit.
- Native Windows UI and installer/package verification remain outside Phase 5E.
