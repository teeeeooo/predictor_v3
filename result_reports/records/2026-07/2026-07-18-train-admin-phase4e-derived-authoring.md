# Train/Admin Phase 4E Restricted Derived Authoring

```yaml
record:
  date: 2026-07-18
  topic: train-admin-phase4e-derived-authoring
  tags: train-admin, phase-4e, derived-feature, stable-identity, safe-ratio, dag, evaluator, migration, fingerprint
  memory_review: updated
  memory_reason: Identity operands, shared evaluator semantics, versioned legacy decode, and inactive authoring are durable Phase 4 contract boundaries.
change_gate:
  new_source: split
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

## Change Reason

The canonical manifest already carried Derived identities but stored operands as
mutable ML names, while production preprocessing owned eight duplicated formula
assignments. Derived rows were dependency evidence only and could not be safely
authored, ordered, previewed, or published.

## Contract / Behavior Changed

- Unified Feature contract v2 stores numerator and denominator stable identities,
  explicit `safe_ratio`, `constant` zero-denominator policy, finite numeric
  `zero_value`, and active state. Existing eight definitions retain their opaque
  identities, output names, `0.0` zero result, and compatibility order.
- Version-1 name operands remain readable through explicit legacy DTO decoding.
  Each legacy name must resolve to exactly one Feature or Derived identity;
  missing or ambiguous sources fail actionably. New publication emits v2 without
  rewriting historical bundles.
- One deterministic DAG owner validates identity existence, numeric evaluator
  availability, active dependencies, self/cycles, downstream lifecycle, output
  collisions, and topological execution. Existing order is the stable tie-break;
  users do not move Derived definitions manually.
- Restricted Add/Edit/Rename/Duplicate/Remove/Enable/Disable commands are atomic.
  Add and Duplicate create inactive definitions with new identities; Rename keeps
  identity. Prepared Preview/Apply retains exact-candidate and stale protection.
- One pure shared evaluator owns formula semantics. Train and Predict retain the
  existing preprocessing facade but no production fallback formula remains.
- Canonical Derived semantics and active model compatibility fingerprints are
  separate. Inactive authoring is publishable; active semantic changes remain
  blocked by the existing retraining/migration Save guard.
- The table-first manager collects only catalog operands and restricted parameters,
  displays formula/dependency/order/fingerprint evidence, and leaves validation,
  DAG, evaluation, repository access, and identity allocation outside the View.

## Evidence And Verification

- Frozen production parity covers positive/negative/zero/floating/NaN/missing/
  non-numeric/infinity behavior, dtype and column order, pre-existing outputs,
  input-copy semantics, inactive exclusion, and Train/Predict adapter equality.
- DAG and command tests cover Feature-to-Derived, Derived chains, deterministic
  order, self/direct/indirect cycles, missing/type/inactive dependencies,
  downstream Remove/Disable, identity lifecycle, finite constants, atomic
  rejection, prepared stale handling, inactive Save, and active Save blockers.
- Migration tests prove representation-only Derived/model fingerprint parity,
  missing/ambiguous legacy rejection, historical v1 bundle reads, v2 publication,
  and rollback to v1.
- Full repository regression passes with `2290 passed, 2 xfailed`. The structure
  checker reports warning-only existing/changed hotspots and no hard failure.
  Formula search finds one production `np.where` owner in the shared evaluator.

## Changed Files

- `core/data_definition/contract/`, `core/data_definition/derived/`, and canonical
  bootstrap manifest
- Data Definition draft, dependency, impact, Save, application/controller, and
  generation repository compatibility boundaries
- shared ML evaluator adapter and preprocessing facade
- restricted Derived dialogs/actions and table-first presentation projections
- focused core/application/UI/migration/runtime regression tests and owner docs

## Known Risks

- Phase 4H still owns process-wide runtime generation cutover. The current ML
  adapter supplies an immutable snapshot from the existing repository composition.
- Windows native UI smoke was not run and remains a pre-release verification item;
  offscreen macOS automation is not equivalent evidence.
- `data_definition_panel.py`, state-builder, contract DTO collection, and Save
  contract retain soft structure warnings. Derived routing/evaluation/graph/
  command responsibilities were split for this slice; further additions to those
  hotspots require a fresh split audit.
