```yaml
record:
  date: 2026-07-15
  topic: train-admin-phase3-slice3c-impact-and-guarded-save
  tags: train-admin, data-definition, phase-3, slice-3c, impact, guarded-save
  memory_review: updated
  memory_reason: The durable Data Definition owner state now includes controlled command provenance, concise impact projection, and the pre-Slice-3D audit hold.
change_gate:
  new_source: split
  hotspot_delta: wiring-only
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

# Change Reason

Draft changes, save-plan evidence, compatibility blockers, mapping requirements,
readiness, and writer results were available only across advanced diagnostic
tabs. The default workflow needed one concise projection that kept those owners
authoritative and made guarded Save state understandable.

# Contract / Behavior Changed

- A Qt-free UI-facing projection groups deterministic Add/Edit changes, schema
  write decision, direct/other/global blockers, restart/retrain/ML evidence,
  changed mapping requirements, and the latest writer result.
- Mapping impact names entity, attribute, trigger/rule, required/optional intent,
  and Data Mapping value ownership while explicitly deferring coverage and
  navigation to Slice 3D.
- The default Data Definition workspace renders the projection immediately after
  command, raw edit, selection relevance, Reset, Refresh, blocked/error Save, and
  successful Save states.
- Existing controller `save_action_enabled`, candidate validation, backup, atomic
  replace, reload, and retry behavior remain authoritative. No second Save
  condition or persistence path was introduced.

# Evidence And Verification

- Projection tests cover clean/dirty/blocked decisions, deterministic multi-
  definition changes, blocker relevance, restart/retrain/compatibility evidence,
  mapping ownership, stale-result clearing, candidate correction, retryable
  writer error, successful backup/reload, and non-mutation.
- Offscreen Qt tests cover visible impact updates, Save enablement, successful
  controlled Add/Save/reload with stable identity/order, mapping impact, ML-
  blocked Edit, and Reset clearing.
- Schema-only mapping saves preserve `features.csv` and the current missing-or-
  present `mapping.json` state. Blocked ML Save preserves schema and features.
- Impacted Data Definition, Data Mapping, Predict schema/runtime compatibility,
  ML catalog, Train shell, structure, and cached change gates passed.

# Changed Files

- `apps/train/controllers/data_definition_impact_projection.py`
- `apps/train/controllers/data_definition_impact_text.py`
- `apps/train/ui/data_definition_impact_view.py`
- Data Definition panel impact wiring
- impact/offscreen workflow and invalid-command acceptance tests
- current work plan, memory seed, and result-record index

# Known Risks

- Training-header and model activation evidence remain explicitly not evaluated
  when the existing readiness owner has no artifact input; the projection does
  not infer readiness.
- Mapping coverage, unresolved rows, navigation handoff, and Predict live reload
  remain deferred to Slice 3D or later.
- Native Computer Use acceptance is intentionally excluded.
