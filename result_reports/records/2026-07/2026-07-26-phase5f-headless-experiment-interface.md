---
record:
  date: 2026-07-26
  topic: phase5f-headless-experiment-interface
  tags: train-admin, phase-5f, experiment-specification, headless, campaign, execution-lock
  memory_review: updated
  memory_reason: Phase 5F establishes durable cross-interface contracts and becomes the exact-head audit target.
change_gate:
  new_source: split
  hotspot_delta: wiring-only
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
---

# Phase 5F Headless Experiment Interface

## Change Reason

Phase 5G requires a safe machine-readable execution foundation that does not
duplicate GUI training or grant production decision authority.

## Contract / Behavior Changed

- Added one strict resolved `predictor_v3.experiment.v1` contract shared by GUI
  and headless callers.
- Added versioned JSON output and run/campaign records with explicit budget,
  attempt, pause/cancel/resume, result, and diagnostics references.
- Added a Qt-free subprocess adapter that invokes the existing child training
  job and publication boundary.
- Added one diagnostic workspace writer lock across GUI, single-run, campaign,
  and resume.
- Kept Candidate immutable/non-Active and added no promotion, Definition
  publication, deletion, deployment, or budget-extension command.

## Evidence And Verification

- Strict/default/parity/validation-only, lock, Candidate/analysis, campaign,
  retry/resume, and real subprocess/cancel integration tests.
- Existing Train lifecycle, Phase 5C publication, Train UI/runtime target, and
  Model Management focused suites.
- Structure and staged gates are required at the final exact head.
- Independent exact-head audit remains pending; this record declares no PASS.

## Changed Files

The source PR changes the experiment application package, headless
adapter/interface/composition, narrow training request/job wiring, Train GUI
composition/status projection, focused tests, and owner/current-state docs.

## Known Risks

- Current-version resume only; historical adapters, immutable full data
  snapshots, final confirmation, and retention remain Phase 5H.
- Reserved early-stopping/recommendation policy is persisted but intentionally
  does not execute Phase 5G behavior.
- Independent exact-head audit and merge authority remain outside this worker.
