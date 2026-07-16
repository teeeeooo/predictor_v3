record:
  date: 2026-07-16
  topic: train-admin-phase3-slice3f-task-oriented-definition-workspace
  tags: train-admin, data-definition, phase-3, slice-3f, task-workspace, presentation, native-macos
  memory_review: updated
  memory_reason: Slice 3F changes the default Definition composition and moves the next gate to the dedicated Slice 3F audit.
change_gate:
  new_source: split
  hotspot_delta: none
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner

# Change Reason

Replace the refined diagnostics-console presentation left after Slice 3E with a
task-oriented Definition Manager, without adding schema intent or moving domain,
validation, compatibility, mapping-value, save, or persistence policy into Qt.

# Contract / Behavior Changed

- The default workspace is now a vertical flow: current state/actions, filters,
  full-width Inventory, selected-definition summary, conditional concise state,
  and collapsed Advanced Diagnostics. The horizontal Inventory/detail splitter
  and default Property/Value detail table are removed.
- The Inventory exposes exactly Label, Kind, Value source, Predict, Model input,
  and Status. Label alone stretches; the remaining columns use bounded widths,
  the last section does not stretch, and internal key/ML name remain available
  through tooltip and accessibility metadata.
- Qt-free projection owners describe the selected definition and clean, dirty,
  blocked, saved, write-error, no-match, no-selection, and load-error states from
  existing controller evidence. Technical details and full impact/blocker data
  remain progressively disclosed.
- One Add menu routes manual Predict input, mapping-backed Predict input, and Data
  Mapping attribute choices through the existing controlled command/dialog owner.
  Existing Save/Edit enablement, retry, Reset/Refresh, focus, shortcuts, dialog
  validation, selection identity, and saved-only Mapping handoff remain intact.
- Saved Mapping Requirements appear only from the latest successful schema Save,
  with the existing exact Data Mapping navigation contract unchanged.

# Evidence And Verification

- Final focused Qt-free/offscreen presentation and impacted workflow suite passed
  55 tests, including normal/compact geometry, exact six-column policy, summary
  and technical evidence, unified Add, state hierarchy, retry, no-match recovery,
  accessibility/focus, and saved handoff behavior.
- The repository-wide offscreen suite passed 2,201 tests with two expected xfails.
  Python compilation and diff whitespace checks passed.
- The structure checker completed with 15 existing soft warnings and no hard
  failure. The Data Definition panel decreased from 496 to 363 LOC; new task
  header, filter, inventory, summary, and projection owners are each at or below
  250 LOC.
- Native evidence under `docs/designs/assets/phase-3-slice-3f/` contains the five
  required visible Cocoa states at 1280x820 and 900x640. Each uses synthetic
  temporary schema/mapping copies and a 2x visible-widget render-target capture.
- Protected production config/data/model/artifact paths have no diff, and the
  native driver reports canonical schema and runtime fixture bytes unchanged.

# Changed Files

- Data Definition inventory, summary, workspace-state, detail, and impact
  presentation owners under `apps/train/controllers/`
- task header, filter, full-width inventory, summary, conditional impact, handoff,
  responsive/focus, dialog, and panel composition under `apps/train/ui/`
- focused Data Definition/Data Mapping presentation and workflow tests
- `tools/dev/native_acceptance/run_phase3f_native_scenarios.py`
- Slice 3F native evidence and current project/work/memory/index documents

# Known Risks

- Native state preparation and interaction were programmatic, not physical.
  Computer Use could not inspect the app because macOS was locked; no app state,
  Qt table hierarchy, accessibility hit-test, or click was used.
- `QScreen.grabWindow()` returned a null pixmap in the locked environment, so the
  evidence is a visible `QWidget.render` target capture, not a desktop-composited
  screenshot or a physical-interaction claim.
- Fifteen repository structure warnings remain outside this slice. The relevant
  pre-existing `data_definition_state_builder.py` and `data_mapping_panel.py`
  hotspots were not expanded with new presentation responsibility.
