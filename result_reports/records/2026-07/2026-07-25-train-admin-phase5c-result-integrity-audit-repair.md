# Train/Admin Phase 5C Result-Integrity Audit Repair

```yaml
record:
  date: 2026-07-25
  topic: train-admin-phase5c-result-integrity-audit-repair
  tags: train-admin, phase-5c, audit-repair, result-integrity, artifact-parity, production-training
  memory_review: updated
  memory_reason: The first Phase 5C audit FAIL and its repaired lifecycle, adapter, parity, and production-evidence boundaries are durable resume context.
change_gate:
  new_source: split
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

## Change Reason

The first independent L4 audit of PR #30 returned `FAIL`. Its bounded blockers
were incomplete lifecycle-side analysis validation, missing baseline and target
failure decisions in CSV/XLSX, absent production-owner integration evidence,
application-to-file-adapter dependency inversion, and inaccurate preprocessing
stage labeling. The original worker record and audit verdict remain historical.

## Contract / Behavior Changed

- Manifest v2 read and promotion now share one lifecycle-owned gate for the
  exact required analysis set, unique paths/categories, required/optional
  semantics, safe files, hashes, supported result version, manifest/result
  version agreement, shared parsing, and manifest/result artifact agreement.
  Manifest v1 remains read-only and is not migrated.
- Target Metrics CSV and XLSX now include baseline type/identity/comparability,
  baseline and target comparison unavailable reasons, R²/MAE/RMSE deltas, and
  target blocking/failure reasons from the same JSON result contract.
- Application publication depends on application-owned evidence, artifact, and
  publication ports. Filesystem reads, report serialization, and hashing remain
  adapters injected by Train composition.
- Preprocessing evidence separates the actual quality collection stage from the
  post-target-policy/pre-RFECV target-usage stage.
- A bounded production configuration preserves the existing defaults while
  allowing deterministic integration coverage to run the real preprocessing,
  canonical multi-target loop, target policy, RFECV, configured Optuna,
  evaluation, Core evidence, artifact readback, lifecycle validation, and
  Candidate publication path without `--dev-fast` or direct evidence assembly.

## Evidence And Verification

- Focused lifecycle, result, Train application, controller, shell, and
  production integration regression: 126 passed.
- Final canonical suite: 2558 passed, 2 xfailed.
- The production integration independently reads JSON, CSV, and XLSX, validates
  every canonical target identity and metric binding, confirms real RFECV and
  configured Optuna evidence, reads the published Candidate through lifecycle
  validation, and confirms the prior Active reference is unchanged.
- Structure validation completes with warnings limited to pre-existing
  repository hotspots; this repair adds no structure error.
- Official exact-head GitHub validation remains a pre-handoff step and is
  recorded in the Draft PR rather than backfilled into historical records.

## Changed Files

- common lifecycle result contract and Candidate analysis validation
- Train application evidence/artifact/publication ports and composition
- filesystem evidence and JSON/CSV/XLSX adapters
- Core production optimization configuration and preprocessing stage evidence
- production job helper and bounded canonical multi-target integration
- focused lifecycle integrity, cross-artifact parity, dependency, and regression
  tests
- current work-plan, design-set status, project log, index, and memory owners

## Known Risks

- The integration intentionally uses one bounded Optuna trial, two CV folds,
  and low estimator counts through the production configuration seam; it proves
  owner/path integration rather than the full 30-trial quality matrix.
- This worker does not declare audit `PASS`, merge, or start Phase 5D, CLI,
  Campaign, leaderboard, or the agent loop.
