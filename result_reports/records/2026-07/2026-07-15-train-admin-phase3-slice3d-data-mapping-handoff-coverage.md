```yaml
record:
  date: 2026-07-15
  topic: train-admin-phase3-slice3d-data-mapping-handoff-coverage
  tags: train-admin, data-definition, data-mapping, phase-3, slice-3d, handoff, coverage
  memory_review: updated
  memory_reason: The durable Train/Admin workflow now includes saved-only public navigation, draft-preserving requirement refresh, and required/optional coverage ownership.
change_gate:
  new_source: split
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

# Change Reason

Saved Mapping Requirements could already project dynamic Data Mapping columns,
but users had to find the affected group and unresolved values manually. No
public shell/panel contract connected the saved schema result to concrete value
coverage.

# Contract / Behavior Changed

- A Qt-free request/result contract carries saved definition identity, exact
  entity/group/attribute, optional stable unresolved row identity, and explicit
  success/failure status. Train shell owns four-tab orchestration and calls one
  public Data Mapping panel entry point.
- Data Definition exposes only requirements affected by the latest successful
  schema write. Unsaved/blocked candidates never become handoffs; Refresh,
  Reset, selection, and failed Save preserve prior successful evidence; the
  next successful Save replaces it.
- Data Mapping reprojects the latest canonical schema requirements over its
  current service-owned draft, baseline, and undo snapshots. Navigation does
  not reload the runtime source, discard edits, clear history, import, save, or
  rewrite JSON.
- Qt-free coverage reports canonical required/optional items with ready,
  missing, invalid, no-row, and unavailable states. Unresolved targets use group,
  row key plus duplicate occurrence, and attribute identity; issue and coverage
  focus share the same UI target resolver.
- Required missing values retain existing validation/Save blocking. Optional
  missing values remain visible as incomplete coverage without becoming a new
  Save blocker. Typed invalid values use the canonical number/boolean policy.
- Runtime persistence no longer materializes absent blank built-in fields into
  unrelated groups. Existing visible/backing fields, including intentionally
  cleared optional fields, remain authoritative overlays.

# Evidence And Verification

- Qt-free tests cover request/result states, existing group resolution, exact
  attribute preservation, multiple canonical requirements, required/optional
  counts, invalid typing, no rows, unavailable group/attribute, distinct blank
  row occurrences, projection non-mutation, missing source, and load failure.
- Controller/service tests prove latest requirement projection preserves current
  edits, baseline dirty semantics, and undo history without disk writes.
- Offscreen Qt proves schema Add/Save, saved handoff selection, shell tab switch,
  exact ODU Cond Specs dynamic column, first unresolved focus, invalid recovery,
  ready coverage, explicit Save, and reload for two Cond Inner Area rows.
- The synthetic flow preserves F&T/PFC identity, PFC blank Pi, Cond Area/Volume,
  unrelated groups, features compatibility projection, and the four-tab shell.
- Focused navigation/UI validation, 407-test impacted regression, structure
  guard, diff checks, and protected-path review passed. Native Computer Use was
  intentionally excluded.

# Changed Files

- `apps/train/application/data_mapping/` contracts, handoff, and coverage owners
- Data Definition controller state and post-save handoff surface
- Data Mapping navigation controller, presentation, draft-session projection,
  coverage surface, and shared issue/coverage target focus
- Train shell public orchestration wiring
- mapping editor absent-blank persistence correction
- focused Qt-free, controller/service, persistence, shell, and offscreen workflow
  tests
- current work plan, memory seed, and result-record index

# Known Risks

- Existing Data Mapping and Data Definition panel/service hotspots remain above
  the soft LOC threshold. New policy and coverage owners were split into feature
  packages; panel changes are bounded public wiring/focus. Reassess the hotspot
  boundary during the required Slice 3D audit before any Slice 3E code.
- Predict still consumes the saved schema only after restart. Coverage ready does
  not clear restart-required state or activate/retrain a model.
- Native table interaction acceptance remains excluded for this slice.
