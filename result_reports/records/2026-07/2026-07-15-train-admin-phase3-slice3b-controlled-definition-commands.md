```yaml
record:
  date: 2026-07-15
  topic: train-admin-phase3-slice3b-controlled-definition-commands
  tags: train-admin, data-definition, phase-3, slice-3b, command, add-edit
  memory_review: no-change
  memory_reason: The active Phase 3 design and Data Definition memory entry already preserve the owner boundary; Slice 3C remains part of the same pending workflow.
change_gate:
  new_source: split
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

# Change Reason

Slice 3A exposed definitions but still required the raw diagnostics grid for every
mutation. Supported Add and Edit intent needed one atomic Qt-free command path
without weakening raw row, identity, order, role, derived-policy, or ML
compatibility guards.

# Contract / Behavior Changed

- Add commands normalize and allocate stable schema identity/order, construct a
  complete manual or supported mapping-backed row, and mark only that new row as
  controlled provenance.
- Edit commands validate every requested field and the complete candidate before
  applying one immutable transition. Restricted fields fail without mutation;
  projection-changing metadata remains staged but save-blocked.
- The existing save-plan and schema writer recognize controlled additions as
  schema changes while continuing to reject raw row additions/deletions.
- Constrained dialogs expose supported intent fields only. Mapping templates are
  exact current entity/trigger/rule relations and never carry concrete values.

# Evidence And Verification

- Qt-free command tests cover normalization, deterministic allocation, atomic
  rejection, projection neutrality, mapping requirements, controlled edit,
  ML-blocked edit, reset, writer/reload, and sequential commands.
- Offscreen Qt tests cover Add/Edit forms, validation feedback, no-op cancel,
  inventory selection/detail/raw-draft alignment, and standalone mapping intent.
- Impacted Data Definition, Data Mapping requirement, Predict schema adapter, ML
  catalog, and Train shell tests passed before commit.
- Structure guard passed with warnings only. `save_contract.py` received only
  controlled schema-change classification; `data_definition_state_builder.py`
  remains the UI-state composition owner. Slice 3C must use a separate impact
  projection and add no further responsibility to either hotspot.

# Changed Files

- `core/data_definition/command_contract.py`, `command_types.py`,
  `command_validation.py`, `commands.py`, draft/projection/save/writer exports
- Data Definition service/controller/state composition
- Add/Edit dialogs and inventory panel wiring
- focused Qt-free and offscreen Qt tests
- `docs/WORK_PLAN.md` and result-record index

# Known Risks

- Native interaction acceptance is intentionally excluded; only automated and
  offscreen Qt evidence is claimed.
- Slice 3C impact presentation and final guarded-save workflow remain pending.
