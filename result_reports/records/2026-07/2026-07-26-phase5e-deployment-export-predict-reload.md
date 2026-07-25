# Phase 5E Deployment Export And Predict Reload Boundary

```yaml
record:
  date: 2026-07-26
  topic: phase5e-deployment-export-predict-reload
  tags: train-admin, phase-5e, deployment-export, predict-reload, active-revision, failure-preservation
  memory_review: updated
  memory_reason: Phase 5E establishes the durable runtime loaded-versus-Active boundary and immutable export publication contract.
change_gate:
  new_source: split
  hotspot_delta: wiring-only
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

## Change Reason

Phase 5D completed explicit promotion and rollback, but a running Predict process
had no owner-controlled way to distinguish its loaded model from a later Active
revision, safely reload while idle, or export the approved Active for deployment.

## Contract / Behavior Changed

- Predict application state records the actually loaded Candidate, Active
  revision, and generation separately from the lifecycle store's current Active.
- Active observation updates status only. A running process continues to use its
  loaded service until the user explicitly requests reload while idle.
- Reload fully validates and loads a detached replacement, then installs it
  through one controller assignment under a final serialized Active revision
  guard. Every failure retains the prior service and loaded identity.
- Deployment export accepts no Candidate selection: it reads the current Active
  under the lifecycle writer lock, revalidates Candidate integrity and current
  compatibility, stages and verifies `model.pkl`, manifest, summary, and
  checksums, and publishes one non-overwriting identity.
- UI owns only status projection, destination selection, and explicit command
  forwarding. It does not read or mutate lifecycle files.

## Evidence And Verification

- Focused runtime, reload, export, lifecycle, Train/Model UI, Predict UI,
  generation, worker, and mock-smoke tests passed.
- Full canonical repository suite passed after adding the new export control to
  the existing Train mock-smoke allowlist.
- Structure guard completed without hard failures. New production owners remain
  below 250 LOC; existing Predict workspace growth is wiring-only, and the
  repository addition is the bounded Active serialization responsibility.

## Changed Files

- `apps/common/model_lifecycle/`
- `apps/predict/`
- `apps/train/`
- focused lifecycle, Predict, Train UI, and mock-smoke tests
- architecture/current-state/memory owner documents
- this record and `result_reports/REPORT_INDEX.md`

## Known Risks

- No independent L4 audit verdict is included; the worker must leave the Draft
  PR open and unmerged.
- Native Windows UI and installer/package verification are outside Phase 5E.
- Directory publication uses the platform's same-filesystem directory rename
  after a collision check; the lifecycle lock serializes project writers, while
  unrelated external writers to the user-selected export directory remain an
  environmental risk.
