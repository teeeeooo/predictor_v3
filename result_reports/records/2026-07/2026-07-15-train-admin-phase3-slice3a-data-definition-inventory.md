record:
  date: 2026-07-15
  topic: train-admin-phase3-slice3a-data-definition-inventory
  tags: train-admin, data-definition, phase-3, slice-3a, inventory, presentation
  memory_review: updated
  memory_reason: The active Data Definition owner state now includes the Slice 3A inventory projection and pre-Slice 3B+3C audit hold.

change_gate:
  new_source: split
  hotspot_delta: wiring-only
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner

# Change Reason

The editable Data Definition tab exposed its raw twenty-field draft and eleven
diagnostic panels as the default workflow. Slice 3A needed an inventory-first
information architecture without changing the accepted draft, validation,
compatibility, save-plan, writer, or mapping owners.

# Contract / Behavior Changed

- A Qt-free presentation owner projects stable draft identities into canonical
  inventory rows, deterministic search/filter results, selection, application
  status, and focused detail.
- The default panel prioritizes status/actions, definition inventory, and focused
  detail. Existing raw editing and all diagnostic evidence remain available in a
  collapsed secondary tab area.
- Save is enabled only for `draft_changed and can_save_schema`; future Add/Edit
  entries are visible but disabled and identify their later-slice ownership.
- Search, filters, selection, and detail are read-only projections. They do not
  create draft changes or write schema, mapping, fixture, configuration, or model
  data.

# Evidence And Verification

- 22 focused projection and offscreen Data Definition UI/edit/save tests passed.
- 178 impacted tests passed across Data Definition projection/readiness/draft/
  save-plan/schema-writer, dynamic Data Mapping requirements, Train shell, and
  Predict schema/catalog adapters.
- `tools/check_code_structure.py` passed with only pre-existing unrelated soft
  warnings. New production files remain below the 250 LOC review threshold after
  separating focused detail and diagnostics responsibilities.
- Offscreen programmatic renders confirmed the inventory/detail-first default and
  the reachable eleven-tab Advanced Diagnostics area.
- Native Computer Use interaction was intentionally not run; Slice 3A acceptance
  uses automated and programmatic offscreen rendering evidence.

# Changed Files

- `apps/train/controllers/data_definition_presentation.py`
- `apps/train/controllers/data_definition_detail_projection.py`
- `apps/train/controllers/data_definition_state_builder.py`
- `apps/train/ui/data_definition_models.py`
- `apps/train/ui/data_definition_diagnostics.py`
- `apps/train/ui/data_definition_panel.py`
- focused Data Definition projection/UI/save tests
- `docs/WORK_PLAN.md`, result index, and active memory

# Known Risks

- Native macOS table interaction and visual acceptance remain outside this Slice.
- Controlled Add Definition, Add Mapping Attribute, and Edit commands are disabled
  placeholders until Slice 3B+3C.
- The repository runtime `data/mapping.json` is absent in this checkout; the
  missing state remained unchanged and dynamic requirement tests used repository
  fixtures without claiming production mapping completeness.
