record:
  date: 2026-07-16
  topic: train-admin-phase3-slice3f-table-first-correction
  tags: train-admin, data-definition, phase-3, slice-3f, table-first, details-modal, native-macos, correction
  memory_review: updated
  memory_reason: Slice 3F table-first correction and its single-requirement saved handoff now have complete automated and native evidence before final re-audit.
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
- A single saved Mapping Requirement now omits the selector and resolves its
  unique saved request directly. Multiple saved requirements retain
  deterministic explicit selection, while a no-handoff state clears selector,
  request, and detail presentation state.
- The production-path Summary Card widget was removed because its normalized
  projection is now consumed by Details.

# Evidence And Verification

- The final authoritative repository run passed: 2,205 tests passed and 2
  expected xfails in 63.45 seconds.
- The focused and impacted Slice 3D handoff, coverage, navigation,
  reconciliation, shared-cell contract, and Data Definition/Data Mapping UI
  run passed. Its focused handoff workflow covers single, multiple,
  invalid-selection, exact-navigation, and clean-state transitions.
- `python3 -m py_compile` passed for the affected handoff presentation and
  native scenario modules. `git diff --check` passed.
- `tools/check_code_structure.py` completed with only the repository's existing
  unrelated soft warnings; no new hard finding was reported. Offscreen scenario
  layout assertions passed at 1280x820 and 900x640.
- The affected native capture `05-saved-mapping-next-step.png` was regenerated
  from audit-correction commit `d969807b4239b8fef264d20e003133bf77d6028c`
  at 1280x820 logical / 2560x1640 pixels. It shows one saved requirement,
  concise direct guidance, no selector, the enabled Open Data Mapping action,
  and the Inventory-first layout without unused selector space.
- The native manifest reports a visible Cocoa window, `native_onscreen: true`,
  visible QWidget render-target capture, programmatic Qt public actions, no
  Computer Use or physical interaction, no known AppKit accessibility table
  path, and no protected schema/runtime fixture changes. The other five
  unaffected native images remain valid.
- Commit lineage is explicit: logical table-first correction
  `b9bd4e84a751147cab78021082e6c4edde6dbe4e`, native evidence follow-up
  `260a712aacabd314940aa5404a9a195086340efe`, and final-audit correction
  `d969807b4239b8fef264d20e003133bf77d6028c`.

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
- final-audit handoff presentation tests, affected native capture/manifest, and
  authoritative record/Work Plan reconciliation

# Known Risks

- Native evidence is programmatic visible-Cocoa evidence and does not claim
  physical interaction; physical interaction is not required for this bounded
  correction.
- Existing repository structure warnings remain outside this bounded UI slice.
- Phase 3 final audit, merge, and Phase 4 remain explicitly deferred.

Historical note: an earlier locked-desktop attempt preceded the successful
native follow-up. It is resolved history, not an active blocker or risk.
