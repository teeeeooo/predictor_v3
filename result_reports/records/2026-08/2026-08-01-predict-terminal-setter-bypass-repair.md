record:
  date: 2026-08-01
  topic: predict-terminal-setter-bypass-repair
  tags: predict, typed-result, canonical-acceptance, session, terminal-state, correction
  memory_review: no-change
  memory_reason: Active Predict architecture and Work Plan owners plus this correction record are sufficient while PR #44 remains an unmerged Draft.
change_gate:
  new_source: none
  hotspot_delta: none
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner

# Change Reason

The first PR #44 canonical-acceptance repair rejected direct storage only when
a result carried execution context or typed outcomes. Empty, message-only, or
legacy-value `complete`, `partial`, `error`, and `cancelled` rows could therefore
bypass the canonical gate.

# Contract / Behavior Corrected

`PredictSession.set_result()` and `set_results()` now use one explicit direct
storage allowlist: `pending`, `running`, and `invalid`. Every terminal status is
rejected before storage regardless of payload form. Bulk validation completes
before any row is stored, preventing a preceding non-executed item from being
partially committed when a later terminal item is invalid.

Production input-validation and running preparation continue through the direct
non-executed path. Existing UI/status and legacy generation-migration fixtures
now use a test-owned helper over the established runtime projection boundary;
no unsafe production fixture API or terminal setter exception was added.

# Evidence And Verification

- Direct-setter and canonical-acceptance narrow suite: 35 passed.
- Migrated UI/status and generation participant fixture suite: 75 passed.
- Related Predict application/session/controller/worker/status/lifecycle,
  generation participant, schema, and shared-composition suite: 228 passed.
- The six focused regressions for the prior aggregate/progress/terminal repair
  passed together.
- Changed source/test compilation, diff hygiene, and cached staged change gate
  passed. Structure check retained the same 34 warning-only findings; the only
  changed production owner (`predict_session.py`) added no structure warning,
  while the unchanged 482-line controller warning remains Auditor evidence.

# Compatibility And Scope

The accepted typed-result path, expected-target/aggregate validation,
accepted-disposition reconciliation, terminal execution context, reload and
generation freshness/migration, public generated Predict schema, and persisted
Feature Definition shape are unchanged. No production data is mutated.

Controller refactoring, Target unit authoring, partial-target Active models,
Result Review, EER/COP, `사양 요약`, Layout B, bulk paste, export redesign,
Calculate integration, and cross-launch history remain excluded. PR #44 remains
Draft and Slice 2 is not recorded as merged or closed.
