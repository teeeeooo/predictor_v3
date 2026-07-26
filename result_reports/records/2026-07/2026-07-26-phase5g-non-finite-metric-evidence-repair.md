record:
  date: 2026-07-26
  topic: phase5g-non-finite-metric-evidence-repair
  tags: train-admin, phase-5g, audit-repair, non-finite, metric-evidence, strict-json
  memory_review: updated
  memory_reason: The second Phase 5G audit exposed a production-selection bypass requiring a durable finite-evidence and strict-JSON rule.
change_gate:
  new_source: none
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner

# Change Reason

The second independent Phase 5G audit failed because `NaN` and Infinity could
be accepted as numeric primary, guardrail, or instability evidence while all
threshold comparisons returned false. A Candidate could therefore pass the
production gate and enter incumbent or recommendation selection. Exact-head run
`30201667033` succeeded at that failed-audit head but is historical validation,
not acceptance. The audit's other 68 passing checks remain reusable historical
coverage; the earlier failed head and run remain historical as well.

# Contract / Behavior Changed

- Added one shared finite-number projection boundary for primary, guardrail,
  instability, complexity, execution-cost, leaderboard, and recommendation
  evidence.
- Project `NaN`, positive Infinity, and negative Infinity as `null` with safe
  `non_finite` context. Missing and non-finite remain distinguishable without
  copying non-standard numeric values into new selection artifacts.
- Require complete finite evidence across configured primary Targets.
  Non-finite baseline evidence preserves the finite current value but removes
  comparison, delta, and improvement claims.
- Keep configured non-finite guardrail/instability evidence unresolved with
  dedicated production blockers. Unconfigured gates remain `not_configured`.
- Reject non-finite tolerance, degradation, and instability policy limits
  before accepted policy persistence.
- Preserve raw historical analysis, Candidate history, Active, retry/budget,
  writer-lock, Definition/deployment/Predict boundaries, and Phase 5H exclusion.

# Evidence And Verification

The focused and targeted suite passed 52 tests. It covers each of `NaN`,
positive Infinity, and negative Infinity for current/baseline primary,
current/baseline guardrail, and instability evidence; mixed aggregates;
finite pass/violation behavior; unconfigured gates; policy rejection;
incumbent/runner-up/recommendation exclusion; standard-JSON gate, leaderboard,
recommendation, and headless projection; and the prior resumable retry-scope
regressions. Independent exact-head re-audit remains required; this record does
not declare audit PASS.

# Changed Files

Existing Phase 5G metric projection, gate, policy, leaderboard,
recommendation, focused tests, and their architecture/workflow/current-state
owners.

# Known Risks

- Historical Phase 5C analysis remains untouched and may contain non-finite raw
  diagnostics; Phase 5G creates a safe projection when reading it.
- This repair does not redefine metric formulas, ranking order, policy
  semantics, agent authority, proposal lifecycle, or retry/budget behavior.
- Production data/model quality, Phase 5H snapshot/final confirmation,
  migration, retention, and deletion remain outside.
- PR #34 must remain open, Draft, unmerged, and independently re-audited at the
  new exact head.
