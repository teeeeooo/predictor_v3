# Train/Admin Phase 4F One-hot Authoring

```yaml
record:
  date: 2026-07-18
  topic: train-admin-phase4f-one-hot-authoring
  tags: train-admin, phase-4f, one-hot, stable-identity, source-ownership, runtime-projection, migration, fingerprint
  memory_review: updated
  memory_reason: Stable category-to-emitted identity, source-mode ownership, and the shared runtime snapshot are durable Phase 4 contract boundaries.
change_gate:
  new_source: split
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

## Change Reason

The canonical manifest defined One-hot groups and categories but related category
rules to emitted Features by mutable names. Predict separately knew the two
selector/group pairs, and no controlled owner could manage group/category
lifecycle, source ownership, category order, or compatibility impact.

## Contract / Behavior Changed

- Unified Feature contract v3 gives groups, categories, selectors, and emitted
  Features independent stable identities. Existing v2 generations decode a
  legacy emitted name only when it resolves to exactly one Feature; missing or
  ambiguous relations fail actionably without modifying historical bundles.
- Static vocabulary is Definition-owned. Mapping-backed concrete values are
  immutable read-only Data Mapping snapshots used for candidates and drift only.
  External category identity/value is provider-owned and accepted only through a
  registered immutable snapshot; production creation is disabled without one.
- Atomic group/category commands cover Add/Edit/Rename/Duplicate/Remove/
  Enable/Disable, selector assignment, source-mode migration, and group-local
  category movement. Add and Duplicate start inactive and allocate identities in
  the prepared transition; Apply never reallocates them.
- Category order is independent from Predict display order and controls only the
  relative active emitted block in canonical ML order. Whole-contract validation
  rejects malformed identities, shape, membership, collision, policies, source
  binding, active state, and category/ML-order relations.
- The One-hot scoped fingerprint contains active selector relation, source mode
  and binding, source-to-emitted identity/name mapping, order, and explicit
  unknown/missing policies. Transient Mapping/provider vocabulary and group-key
  presentation are excluded.
- Predict encoding and dropdown options consume one immutable canonical runtime
  snapshot. The fixed `ref_type`/`refrigerant` and
  `exp_type`/`expansion_device` runtime table is removed. Train continues to use
  canonical emitted Feature membership/order rather than re-encoding selectors.
- Existing `warn_all_zero` unknown behavior, `all_zero` missing behavior, five
  emitted names, float output, deterministic order, and input-copy semantics are
  preserved. Inactive authoring is publishable; active semantic changes remain
  behind the existing retraining/migration Save guard.
- The group-centered table-first UI collects intent and presents owner, category,
  emitted Feature, order, drift, provider, compatibility, header, fingerprint,
  Save, and resolution evidence. It does not read/write Mapping data, allocate
  identity, encode runtime rows, or decide collisions and compatibility.

## Evidence And Verification

- Golden runtime coverage locks Refrigerant `R410A`, `R32`, `R290` and Expansion
  `EEV`, `Capi` order, known/missing/unknown output, warnings, float dtype,
  input immutability, source/emitted-name divergence, group rename, and Train
  emitted-header parity.
- Migration coverage proves v2 decode, exact identity resolution, actionable
  missing/ambiguous failure, representation-only One-hot/model fingerprint
  parity, historical generation read, and rollback.
- Source-mode coverage proves Static selector-option projection, Mapping
  candidate/drift handling, byte-identical `mapping.json` across command and
  Save, identity preservation across Mapping rename drift, External read-only
  identity/value, unavailable-provider blockers, and disabled production creation.
- Command and persistence coverage exercises identity lifecycle, atomic
  rejection, dependency blockers, local reorder, group disable/re-enable,
  prepared exact-candidate/stale behavior, inactive Save/reload, active Save
  guard, stale-parent/failure recovery, immutable history, and publication
  validation.
- Focused Data Definition/Derived/Predict regression passes with 449 tests. Full
  repository regression passes with `2378 passed, 2 xfailed`. Compile, diff,
  structure, staged-change, remote-head, and CI evidence are recorded in the
  terminal closeout after the final branch state is fixed.

## Changed Files

- `core/data_definition/contract/`, `core/data_definition/one_hot/`, canonical
  draft/candidate/validation/fingerprint/impact/Save owners, and bootstrap manifest
- Predict row adapter, dropdown adapter, and Train/Predict composition snapshot wiring
- Data Definition service/controller, persisted Mapping vocabulary adapter,
  group-centered One-hot dialogs/actions/presentation, and Preview evidence
- focused core/application/UI/migration/runtime/persistence regression tests
- current work plan, project log, active memory, and result-record index

## Known Risks

- Phase 4H still owns process-wide generation cutover and standalone Predict
  generation detection. Current Train composition injects one immutable active
  snapshot; standalone compatibility continues to use the bootstrap snapshot.
- Dirty Data Mapping draft reconciliation remains Phase 4H/4I work. Phase 4F
  reads only the persisted Mapping snapshot and never mutates concrete values.
- No production External provider is registered; fake immutable snapshots cover
  the bounded contract without introducing a provider framework.
- Windows native UI smoke was not run and remains a pre-release verification
  item; macOS/offscreen automation is not equivalent evidence.
