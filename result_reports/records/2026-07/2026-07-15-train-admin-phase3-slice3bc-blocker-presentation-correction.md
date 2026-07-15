```yaml
record:
  date: 2026-07-15
  topic: train-admin-phase3-slice3bc-blocker-presentation-correction
  tags: train-admin, data-definition, phase-3, slice-3b, slice-3c, blocker-presentation
  memory_review: updated
  memory_reason: The durable save-plan contract now preserves independent full-parity evidence beside ML compatibility blockers and renders row identity without selection.
change_gate:
  new_source: none
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

# Change Reason

Draft-wide ML fingerprint suppression hid unrelated full-parity issues, and the
no-selection Impact Preview retained structured row evidence without rendering
the affected definition key.

# Contract / Behavior Changed

- Save planning derives ML compatibility blockers once, reverts only their
  attributed row/field changes against the immutable baseline or controlled-Add
  provenance, and revalidates the reference candidate. Parity issues that remain
  are independent and stay visible; parity caused only by the explained ML
  projection change is suppressed as duplicate evidence.
- Independent mapping, source, label, and UI-key parity evidence remains stable
  before and after an unrelated ML edit is reverted. Multiple definitions retain
  separate blocker identities and selection-relative relevance.
- Impact Save decision text renders the stable definition key for
  `other_definition` and `selection_unavailable` row blockers, plus field and a
  distinct target. True global blockers remain definition-free.

# Evidence And Verification

- 160 focused tests passed for structural duplicate suppression, independent and
  multiple parity blockers, partial revert stability, writer/result deduplication,
  Controlled Add/Edit, and no-selection rendering/recovery.
- 356 impacted tests passed across Data Definition, Data Mapping dynamic
  requirements and workflows, Predict schema/mapping adapters, ML Feature
  Catalog fingerprint/parity, and the four-tab Train shell.
- Compile, diff, staged change, and structure guards passed. The structure guard
  retained the warning-only `save_contract.py` hotspot; the correction keeps the
  policy inside its existing save-plan owner and adds no new source owner.
- Native Computer Use was not retried, as required by scope.

# Changed Files

- Data Definition save-plan parity suppression and Impact Preview text owners
- Focused core, controller, and offscreen presentation regressions
- Work plan, active memory, and result-record index

# Known Risks

- `save_contract.py` remains above the 400-LOC soft threshold. The added logic is
  confined to its existing blocker-composition responsibility; final Slice 3B+3C
  re-audit remains mandatory before any Slice 3D implementation.
- Native physical interaction evidence remains intentionally excluded.
