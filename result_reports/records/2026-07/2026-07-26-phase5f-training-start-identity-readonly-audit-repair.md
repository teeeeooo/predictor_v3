---
record:
  date: 2026-07-26
  topic: phase5f-training-start-identity-readonly-audit-repair
  tags: train-admin, phase-5f, audit-repair, training-start, build-identity, read-only-composition
  memory_review: updated
  memory_reason: The first Phase 5F audit failure and its three corrected execution boundaries are durable re-audit context.
change_gate:
  new_source: split
  hotspot_delta: wiring-only
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
---

# Phase 5F Training Start, Identity, And Read-only Audit Repair

## Change Reason

The first independent audit returned `FAIL` at exact head
`b5ce141711c3660e2ce38b738f58f478a333d251`. Validation run `30193572243`
had succeeded but did not cover three blocking application-boundary defects.

## Contract / Behavior Changed

- A structured child Core-training-start event now crosses the existing
  execution port and lifecycle owner before a campaign consumes one iteration.
  Adapter/process-start failure preserves a non-started run attempt and
  diagnostics without Candidate, Active, completed-run, or budget mutation.
- Build identity now records identifiable clean/dirty repository revision from
  the application-owned repository root, independent of caller `cwd`.
  Missing, lookup-failed, or fallback-only identity blocks resume without
  rewriting saved campaign/result evidence and directs the caller to create a
  new campaign.
- Headless service construction and `validate` are mutation-free. `resolve`
  reads an existing generation only and blocks when absent. Validated training
  mutation invokes the existing Bootstrap initializer explicitly.

## Evidence And Verification

- Focused regressions cover spawn failure with budget-preserving resume,
  post-start failure/retry/cancel accounting, attempt versus iteration identity,
  external-cwd revision equality, dirty-build detection, unavailable/missing
  identity blocking, and same-build resume.
- Empty-workspace valid/invalid validation and resolution assert no generation,
  pointer, projection, lifecycle, Candidate, Active, or lock artifacts; an
  existing generation resolves without byte changes.
- Existing lifecycle, Candidate/result, QProcess, lock, headless subprocess,
  campaign, and GUI status regressions remain the re-audit baseline.

## Changed Files

The repair changes the existing experiment campaign/service/record owners,
execution port and child adapters/job, headless composition/CLI, focused tests,
and Phase 5F owner/current-state documents. Campaign execution and durable run
callbacks are split inside the existing experiment package to retain source
size boundaries.

## Known Risks

- Full historical compatibility, immutable snapshots, final confirmation, and
  retention remain Phase 5H.
- This worker does not declare audit PASS or merge PR #33. Independent
  exact-head re-audit remains required.
