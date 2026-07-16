record:
  date: 2026-07-15
  topic: train-admin-phase3-slice3e-editing-native-polish
  tags: train-admin, data-definition, data-mapping, phase-3, slice-3e, keyboard, accessibility, focus, native-macos
  memory_review: updated
  memory_reason: Phase 3 now waits at final audit with bounded native Slice 3E evidence instead of waiting to start Slice 3E.
change_gate:
  new_source: split
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner

# Change Reason

Complete the existing Definition-to-Mapping workflow for repeated engineering
use without changing definition, validation, mapping-value, save-plan, or
persistence contracts.

# Contract / Behavior Changed

- Data Definition now separates preferred canonical selection from the visible
  filtered current row, routes standard Find/Save and Escape behavior without
  writing when Save is disabled, and restores useful focus after dialog,
  Save, Reset, Refresh, no-match, and blocked operations.
- Add/Edit dialogs use explicit label buddies, logical tab order, first-field
  focus, focusable command-validation summaries, non-mutating Cancel/Escape,
  and a scrollable form body that leaves Apply/Cancel available.
- Default state and impact copy distinguishes clean, unsaved, blocked, saved,
  write-error, empty, and no-match states without making raw internal values the
  primary language. Advanced Diagnostics remains the raw compatibility path.
- Data Mapping handoff focuses only an exact unresolved cell; ready coverage
  focuses the requirement selector, and stale/unavailable requests retain the
  current draft and row coordinates. The toolbar reflows at compact width.
- The existing domain, command validation, schema writer, mapping draft/undo,
  exchange, and persistence contracts are unchanged.

# Evidence And Verification

- Focused Qt-free/offscreen workflow and impacted UI suites cover keyboard
  search/Edit, Add cancel/apply/save, blocked Reset, retry, no-match recovery,
  accessibility metadata, compact geometry, and ready/incomplete/stale handoff.
- Repository-wide offscreen suite passed with the two expected xfails after the
  final compact-toolbar correction.
- Structure and staged-diff guards pass; soft warnings were triaged rather than
  treated as contract failures.
- Native evidence under `docs/designs/assets/phase-3-slice-3e/` contains seven
  visible cocoa states at 1280x820 and 900x640 using synthetic temporary schema
  and mapping copies. Computer Use confirmed the Python app process without
  inspecting or clicking Qt table accessibility hierarchy.

# Changed Files

- `apps/train/controllers/data_definition_*`
- `apps/train/ui/data_definition*`
- `apps/train/ui/data_mapping*`
- `apps/train/ui/shell.py`
- focused Data Definition/Data Mapping UI tests
- `tools/dev/native_acceptance/run_phase3e_native_scenarios.py`
- Phase 3E native evidence, active work plan, and memory/index records

# Known Risks

- Native interaction was programmatic, not physical. The known AppKit table AX
  click path was deliberately not retried, so deferred Phase 2 physical table
  acceptance remains separate.
- macOS `QScreen.grabWindow()` returned a null pixmap without screen-recording
  access. Evidence uses the visible cocoa widget's native 2x backing-store grab
  and is not a desktop-composited capture.
- `data_definition_panel.py` remains above the 400 LOC soft warning at 496 LOC,
  but new keyboard/focus/responsive responsibility was extracted to the 155 LOC
  workspace behavior owner. `data_mapping_panel.py` remains an existing hotspot;
  this slice adds only bounded handoff focus routing. Further split is deferred
  to a dedicated audit rather than mixed into the final polish slice.
