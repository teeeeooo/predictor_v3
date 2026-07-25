```yaml
record:
  date: 2026-07-26
  topic: train-admin-phase5d-training-running-guidance-repair
  tags: train-admin, phase-5d, audit-repair, training-running, promotion-guidance, qwidget
  memory_review: updated
  memory_reason: The default blocked-state projection now shares the structured promotion guidance contract, not only the unreachable command outcome.
change_gate:
  new_source: none
  hotspot_delta: wiring-only
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

# Change Reason

The second independent Phase 5D L4 audit returned `FAIL` at
`89e20055cc45a5c7fad59aa24a2b9d34c16e4237`. The previous repair corrected
four blocker areas, but the normal training-running QWidget state displayed
only that promotion was unavailable. Because the button was disabled, users
never reached the complete structured command-outcome guidance.

# Contract / Behavior Changed

- Reuse the existing structured `training_running` Korean promotion message in
  the normal selected-Candidate QWidget state.
- Keep the promotion button disabled and avoid issuing a promotion command.
- State all three required facts in the default surface: training blocks the
  change, the existing Active model is maintained, and the user should retry
  after training completes.
- Keep lifecycle, application command, diagnostics, and all four previously
  repaired blocker areas unchanged.

# Evidence And Verification

- Focused model-management, Qt, and lifecycle suite: 59 passed.
- Impacted Train, lifecycle, and Predict suite: 328 passed.
- Full canonical repository suite: 2635 passed, 2 expected xfailed.
- Deterministic offscreen QWidget assertion verifies the exact complete
  training-running guidance, disabled button, and zero promotion calls.
- Diff check and Python compilation passed.

# Changed Files

- Train model-management Korean message owner and QWidget projection
- focused offscreen QWidget regression
- Phase 5D current-state documents and this correction record

# Known Risks

- Native desktop smoke was not repeated; deterministic offscreen QWidget
  interaction directly covers the failed contract.
- PR #31 remains open, Draft, and unmerged. This worker does not declare audit
  `PASS`; the new exact head requires independent L4 re-audit.
