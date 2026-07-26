record:
  date: 2026-07-26
  topic: phase5g-agent-assisted-campaign-loop
  tags: train-admin, phase-5g, agent-campaign, proposal, hard-gate, leaderboard, recommendation
  memory_review: updated
  memory_reason: Phase 5G changed from unstarted to source-complete pending independent exact-head audit and established new durable authority boundaries.
change_gate:
  new_source: split
  hotspot_delta: wiring-only
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner

# Change Reason

Phase 5F provided explicit bounded campaign execution but intentionally did not
own external proposal policy, Candidate selection, leaderboard, or
recommendation. Phase 5G needs those decisions without giving a local agent
production mutation authority or adding an in-product LLM.

# Contract / Behavior Changed

- Added versioned agent campaign, proposal, gate, leaderboard, recommendation,
  and operator budget-extension contracts beside the unchanged Phase 5F
  Experiment Specification.
- Persisted hypothesis and resolved before/delta/after evidence before training,
  with closed category paths and structured non-consuming rejection.
- Reused Core-owned training-start consumption, bounded attempts, shared writer
  lock, Candidate publication, pause/cancel/resume, and immutable lifecycle
  stores.
- Added production/exploratory hard gates, deterministic ranking, campaign
  incumbent distinct from Active, honest comparable/unbenchmarked/Bootstrap
  baselines, and immutable approval-required recommendation history.
- Kept budget increase behind a separate operator command and kept Definition,
  Active, deployment, retention, migration, and Phase 5H confirmation outside.

# Evidence And Verification

The final owner-focused command passed 396 tests covering deterministic
contract, gate, ranking, recommendation, headless/store, UI projection,
restart/budget, representative DEV child-process campaign, Phase 5F
experiment/lock/retry, Candidate lifecycle, deployment export, and Predict
reload boundaries. The code-structure guard passed with pre-existing hotspot
warnings only, and the cached agent change gate returned `OK`. Exact-head
evidence is prepared for an independent Auditor; this record does not declare
audit PASS.

# Changed Files

Phase 5G application owners and tests under `apps/train/application/experiments/`
and `tests/apps/train/`, headless command wiring, the existing read-only Train
campaign projection, and their architecture/workflow/current-state owners.

# Known Risks

- Real production data and model-quality judgment were intentionally not used;
  deterministic fixtures and DEV mock execution prove lifecycle semantics only.
- Preprocessing proposals remain limited to contracts actually supported by the
  shared resolver; unsupported variants are rejected rather than silently
  ignored.
- Independent exact-head audit remains required before merge. Phase 5H is
  unstarted.
