record:
  date: 2026-07-16
  topic: train-admin-phase3-slice3f-table-first-correction
  tags: train-admin, data-definition, phase-3, slice-3f, table-first, details-modal, native-macos, correction
  memory_review: updated
  memory_reason: The active Slice 3F composition is now table-first with on-demand Details; native rerun remains blocked by the locked desktop.
change_gate:
  new_source: split
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner

# Change Reason

Correct the Slice 3F default Definition workspace from a Summary-led diagnostics
composition to a table-first Feature Manager while preserving the existing
controller, command, validation, schema-save, compatibility, mapping, handoff,
and Slice 3E interaction contracts.

# Contract / Behavior Changed

- The active Slice 3F design and `docs/WORK_PLAN.md` now explicitly supersede
  the always-visible Summary Card, clean lower panel, and Label-only stretch
  policy.
- Normal Inventory projects eight user-facing columns: Label, Kind, Data Type,
  Value source, Predict, Model input, Required, and Status. Compact Inventory
  keeps Label, Kind, Data Type, Value source, Predict, and Status.
- Inventory owns bounded Interactive column widths and deterministic compact
  visibility; no visible column or last section stretches by default.
- Summary remains a Qt-free projection authority and is normalized with existing
  detail rows into an immutable `DataDefinitionDetailsProjection`. A modal
  `QDialog.exec()` renders it read-only with one outer vertical scroll area,
  fixed Close, explicit Escape handling, wrapped values, and no nested vertical
  technical-table scrollbar.
- Enter/double-click uses the controlled Edit dialog for schema-backed rows and
  the read-only Details dialog for derived/read-only rows. Details closes with
  selection, filter, draft, and Inventory focus restored.
- Header actions are Add/Edit/Save schema/More, with Review changes, Review
  blocker, and saved-only Open Data Mapping surfaced conditionally. Clean state
  has no lower impact panel; dirty/blocked/write-error/saved handoff surfaces
  remain conditional.
- The production-path Summary Card widget was removed because its normalized
  projection is now consumed by Details.

# Evidence And Verification

- Full repository pytest suite passed: 2,204 tests passed and 2 expected xfails.
- Focused table-first Details tests passed: 4 tests covering normal modal
  snapshot/scroll/focus, Enter editable/read-only routing, Escape recovery, and
  double-click controlled routing. The impacted Data Definition suite passed
  56 tests before the additional Escape test; the final full suite includes it.
- `python3 -m py_compile` passed for the changed Details, projection, header,
  behavior, and native scenario modules. `git diff --check` passed.
- `tools/check_code_structure.py` completed with only the repository's existing
  unrelated soft warnings; no new hard finding was reported. Offscreen scenario
  layout assertions passed at 1280x820 and 900x640.
- Native correction assets are reserved under
  `docs/designs/assets/phase-3-slice-3f-table-first-correction/`. The safe Cocoa
  runner was prepared, but Computer Use reported the Mac was locked and could
  not unlock it. No native onscreen PNG or physical interaction is claimed.
  The known AppKit Qt table accessibility click/hit-test path was not used.

# Changed Files

- `apps/train/controllers/data_definition_interaction.py`
- `apps/train/controllers/data_definition_presentation.py`
- `apps/train/controllers/data_definition_summary_projection.py`
- `apps/train/controllers/data_definition_workspace_projection.py`
- `apps/train/controllers/data_definition_details_projection.py`
- `apps/train/ui/data_definition_panel.py`
- `apps/train/ui/data_definition/inventory_view.py`
- `apps/train/ui/data_definition/task_header.py`
- `apps/train/ui/data_definition/workspace_behavior.py`
- `apps/train/ui/data_definition_details_dialog.py`
- removed `apps/train/ui/data_definition/summary_card.py`
- focused Data Definition tests and `tools/dev/native_acceptance/run_phase3f_native_scenarios.py`
- active design, work plan, correction evidence README, memory, and report index

# Known Risks

- Native onscreen correction acceptance is still pending a manual desktop
  unlock. The current evidence is automated/offscreen and a native scenario
  contract, not a desktop-composited or physical-interaction claim.
- Existing repository structure warnings remain outside this bounded UI slice.
- Phase 3 final audit, merge, and Phase 4 remain explicitly deferred.
