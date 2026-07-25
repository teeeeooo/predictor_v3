```yaml
record:
  date: 2026-07-26
  topic: train-admin-phase5d-ui-state-projection-audit-repair
  tags: train-admin, phase-5d, audit-repair, qt-model, compatibility, target-comparison, advanced-evidence, promotion-guidance
  memory_review: updated
  memory_reason: The repair makes current compatibility and target-level persisted decisions durable model-management projection invariants.
change_gate:
  new_source: none
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

# Change Reason

The first independent Phase 5D L4 audit returned `FAIL` at head
`c163da7027cdfdcc1bc8f831c17f6e1285b0d6db`. Five blockers remained in empty
Qt table transitions, current compatibility, target comparison meaning,
Advanced evidence fidelity, and user-facing promotion rejection guidance.

# Contract / Behavior Changed

- Make the shared read-only Qt model tolerate zero rows/columns and stale
  header/data queries across populated, empty, corruption, and repopulated
  states.
- Reuse one lifecycle promotion compatibility owner for both read-only current
  availability and final guarded promotion. Stored eligibility alone no longer
  enables promotion after registry or definition drift.
- Project target comparison only from the stored target-level decision and
  numeric metric/delta availability. Global baseline context cannot upgrade an
  unavailable target to fair.
- Preserve all stored RFECV, selected-feature, importance, Optuna,
  preprocessing, and data-quality fields in the collapsible Advanced
  projection without deriving missing values.
- Map structured lifecycle/promotion reason codes to Korean problem,
  Active-preservation, and next-action guidance while retaining raw details in
  application diagnostics.

# Evidence And Verification

- Focused model-management, Qt, and lifecycle suite: 59 passed.
- Impacted Train, lifecycle, and Predict suite: 328 passed.
- Full canonical repository suite: 2635 passed, 2 expected xfailed.
- Structure guard: no hard failure. The stale-revision typed error adds one
  class-count soft warning in the existing lifecycle error owner; splitting
  closely related lifecycle errors is not justified for this bounded repair.
- Deterministic offscreen interaction covers promotion, rollback, Candidate
  corruption, fail-closed refresh, zero-dimension models, and stale header
  queries. Native platform smoke remains outside this automated repair.

# Changed Files

- lifecycle promotion/repository structured status owners
- Train model-management application projections and immutable DTOs
- Train model-management Qt surface, Korean text mapping, and static table model
- focused application/lifecycle/offscreen QWidget tests
- Phase 5D current-state documents and this repair record

# Known Risks

- A compatibility change after inspection is intentionally resolved by the
  final promotion validation; the UI may briefly show a stale availability
  status until the guarded command is rejected and refreshed.
- The PR remains Draft, open, and unmerged. This repair worker does not declare
  audit `PASS`; the repaired exact head requires independent L4 re-audit.
