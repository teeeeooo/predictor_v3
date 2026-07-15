```yaml
record:
  date: 2026-07-15
  topic: train-admin-phase3-slice3d-value-contract-audit-correction
  tags: train-admin, data-definition, data-mapping, phase-3, slice-3d, audit-correction, shared-cell, value-provenance
  memory_review: updated
  memory_reason: The durable Slice 3D contract now aggregates every definition sharing one mapping cell and keeps untouched requirement blanks outside concrete mapping payload.
change_gate:
  new_source: small
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

# Change Reason

Data Mapping previously selected the first requirement for a shared group and
attribute even though coverage still projected every source definition. It also
materialized an empty row value merely to show a dynamic column, allowing an
untouched placeholder to survive requirement removal and later enter JSON.

# Contract / Behavior Changed

- One Qt-free resolver now groups requirements by resolved editor group and
  mapping attribute. Compatible sources share one effective type, relation,
  coverage item, validation path, and column; required intent is aggregated with
  `any`, and deterministic source definition keys remain available for both
  saved handoffs.
- Type or trigger/rule conflicts produce a structured blocker carrying the
  group, attribute, and all definition keys. Conflicting cells are excluded from
  normal overlay and coverage, and schema candidate validation, Data Mapping
  Save, exchange export, and import candidate application all remain blocked.
- Dynamic visibility is now lazy: an absent runtime value renders blank through
  `value_for` without adding a row payload key. Runtime/import/user-owned values,
  including an explicit blank edit, remain concrete because their key exists;
  undo restores that presence with the draft snapshot.
- Requirement removal discards only untouched lazy absence. Existing runtime and
  user-authored backing values remain hidden and persist. Exchange candidate
  construction preserves lazy absence for a matching existing row so an official
  export/import no-op does not create dirty state, payload, or undo history.

# Evidence And Verification

- Focused contract tests cover type and relation conflicts, required aggregation,
  identical duplicate deduplication, alias-resolved cell identity, deterministic
  source references, both saved handoffs, and full Data Definition candidate
  Save blocking.
- Persistence tests cover simple and condenser-spec placeholders, runtime and
  user-authored nonblank values, explicit blank edits, repeated add/remove and
  refresh, no projection undo command, explicit Save, and exchange import
  candidate behavior.
- Offscreen Data Mapping tests cover one shared column/coverage item, required
  completion and Save availability, plus requirement removal followed by an
  unrelated edit without a synthetic JSON key.
- The final impacted Data Definition, Data Mapping, import/export, condenser,
  Predict adapter, and Train shell regression passed 422 tests. Native Computer
  Use was not run, as required by this correction scope.

# Changed Files

- shared Mapping Requirement contract resolver and Data Definition validation
- Data Mapping effective projection, snapshot validation, coverage, navigation,
  and concise source-reference presentation contract
- lazy editor-row value projection and exchange candidate absence preservation
- focused core, service/application, persistence/import, and offscreen tests
- work plan, memory seed, report index, and this correction record

# Known Risks

- Mapping JSON and mapping_bundle_v1 gain no provenance field or format change.
  Concrete ownership is represented in memory by row-key presence, while an
  untouched projected blank remains absent.
- A conflicted cell deliberately has no normal coverage item or first-wins
  column contract; users must resolve the Data Definition conflict first.
- Slice 3E native/editing polish and Predict live schema reload remain excluded.
