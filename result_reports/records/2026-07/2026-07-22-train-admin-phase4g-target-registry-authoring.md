# Train/Admin Phase 4G Target Registry Authoring

```yaml
record:
  date: 2026-07-22
  topic: train-admin-phase4g-target-registry-authoring
  tags: train-admin, phase-4g, target, result-feature, registry, migration, training-snapshot
  memory_review: updated
  memory_reason: Canonical Target association/policy ownership and frozen Train registry snapshots are durable Phase 4 boundaries.
change_gate:
  new_source: small
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

## Change Reason

Target/model-group membership and policy were duplicated between Target rows,
group membership lists, and ML-name-keyed Python dictionaries. Result Features had
no atomic Target lifecycle, presentation ordering affected model compatibility, and
production Train iterated import-time registry/Target state.

## Contract / Behavior Changed

- Contract v4 makes each Target the single writable owner of its Result Feature,
  one of the three validated model groups, closed allowed/exclude policy over stable
  input-owner identities, independent registry/presentation order, and active state.
  Model-group key/name/use_rfe remain read-only validated facts.
- v1/v2/v3 generations decode without in-place mutation. Existing Target, Result,
  and group identities survive migration. Legacy Result-name exclusions that were
  removed by leakage protection before policy evaluation are preserved as stable
  compatibility references, while missing or ambiguous real input references fail.
- Atomic Add/Edit/Rename/Duplicate/Remove/Enable/Disable/Move/Change Group/Change
  Policy commands keep Result and Target lifecycle together. Add/Duplicate are
  inactive, Remove returns a newly-added definition to an exact clean baseline,
  and prepared Preview/Apply retains candidate identities and stale protection.
- Target presentation has a separate fingerprint. Label, Predict visibility, and
  presentation order do not alter model compatibility; active ML name, membership,
  group, registry order, and policy do.
- The immutable registry projection carries generation and scoped fingerprints,
  fixed group metadata, ordered active Targets, resolved policy names, training
  headers, and pre-Target input order. Production Train freezes its serialized value
  into the request and child process; later Definition changes cannot mutate a run.
  `MODEL_REGISTRY` remains only a bootstrap-derived compatibility facade.
- The table-first Result/Target manager displays the inventory, read-only group
  evidence, structured policy owners, final training inputs, and prepared impact.
  It does not create identity, evaluate policy, access repositories, or start Train.

## Evidence And Verification

- Golden coverage retains three groups, five Targets, exact membership/use_rfe,
  group and Target iteration, and exact final input columns for all five policies.
- Migration coverage retains v1/v2/v3 read/rollback and identity relations, rejects
  malformed references, and proves representation-only model fingerprint parity.
- CRUD, raw validation, prepared transition, inactive Save/reload, active Save guard,
  frozen request, dynamic Target projection, Mapping/model byte invariance, and
  pre-staging publication rejection are covered by focused tests.
- Full repository regression passes with `2396 passed, 2 xfailed`. Compile, diff,
  structure, staged-change, remote-head, and CI evidence are completed during final
  branch closeout.

## Changed Files

- canonical contract v4 Target DTO, compatibility decoder, validation, projection,
  scoped fingerprints, draft/candidate, and immutable Target registry package
- Train request/QProcess/job/preprocessing composition and generated registry facade
- Data Definition service/controller/impact projection and Result/Target manager
- focused migration/CRUD/policy/runtime/publication/UI regressions and active records

## Known Risks

- Phase 4H still owns process-wide TrainShell/Predict generation cutover. A running
  request is frozen, but Save does not atomically reload every tab.
- Candidate artifact lifecycle, training promotion, algorithms, group creation, and
  automatic retraining remain out of scope.
- Windows native UI smoke was not run and remains a pre-release verification item.
