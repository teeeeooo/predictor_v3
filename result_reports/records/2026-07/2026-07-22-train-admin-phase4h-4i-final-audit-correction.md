# Train/Admin Phase 4H+4I Final Audit Correction

record:
  date: 2026-07-22
  topic: train-admin-phase4h-4i-final-audit-correction
  tags: train-admin, phase-4h, phase-4i, predict-result, stable-identity, train-target, final-audit
  memory_review: updated
  memory_reason: Runtime cutover now preserves Result values by stable identity and refreshes all idle Train Target presentation from the committed registry.

change_gate:
  new_source: split
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner

## Change Reason

Predict case inputs migrated by stable Feature identity, but existing ResultRow
values remained keyed by the prior Result column key. Train registry cutover also
updated the Target list without rebuilding count, waiting metrics, and Training
Summary from the same committed registry.

## Corrected Contract

- Predict prepare projects case values and ResultRow state together. Result values
  move only through the canonical active Target's stable Result Feature identity;
  column/ML-name similarity is never used. Unchanged and hidden-active results are
  preserved, removed results are dropped at B commit, and newly owned results begin
  empty.
- The session validates revision and exact case order before installing copied
  input, autofill, dirty-field, status, result-value, and message state as one
  transition. Rollback snapshots restore the complete A case/result state.
- Train idle refresh projects list, order, count, waiting metrics, and Summary rows
  from one `ModelRegistrySnapshot`. A running request retains its A presentation
  while status distinguishes process-active B; terminal transition applies the
  pending B idle projection, and the next run freezes B.

## Verification

- Final-correction focused runtime/UI/rollback tests plus existing Phase 4H+4I
  participant and shell coverage: `50 passed`.
- Expanded Predict, Train, Phase 4G registry, and projection regression:
  `342 passed`.
- Full repository suite: `2448 passed, 2 xfailed`.
- Result/Target rename is verified at the actual `CaseTableModel` cell boundary;
  added/removed/hidden policies, result clear/running/completed stale rejection,
  and later-participant coordinator rollback preserve exact status/value/message.
- Train Add/Enable, Disable, Rename, and Reorder refresh list/count/Summary/order/
  waiting metrics. A running request retains A rows until terminal, then B idle
  rows apply and the next request freezes B.
- Windows-native Train/Predict/Mapping smoke was not run and remains pre-release
  verification. Phase 5 remains unimplemented.

## Invariants

No active model artifact or Mapping concrete value is read, promoted, or changed
by this correction. No result history store, dashboard framework, global state,
cross-process result synchronization, or Phase 5 UX was introduced.
