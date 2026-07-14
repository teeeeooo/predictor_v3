```yaml
record:
  date: 2026-07-14
  topic: train-admin-phase2-slice2bc-audit-correction
  tags: train-admin, mapping, phase-2, slice-2b, slice-2c, canonicalization, paste, selection
  memory_review: updated
  memory_reason: Preserve typed dirty semantics and the atomic overflow/one-rectangle interaction contract across future spreadsheet work.
change_gate:
  new_source: none
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

# Change Reason

Valid numeric and boolean input could remain as UI strings and compare dirty
against canonical runtime values. Paste also silently discarded cells outside
the table, while extended multi-range selection let copy and clear act on
different cell sets.

# Contract / Behavior Changed

- The Qt-free mapping value policy is the single built-in and
  definition-backed column-type resolver used by mutation, validation,
  presentation metadata, and persistence.
- The service command boundary canonicalizes valid numeric and boolean input;
  invalid input remains raw and undoable for validation feedback.
- Paste preflights the expanded clipboard grid before calling the application
  command. Any row or column overflow blocks the whole operation with explicit
  feedback and no draft/history mutation.
- The table uses contiguous selection and normalizes copy and clear to the same
  complete rectangle. In-bounds protected targets retain partial non-shifting
  application and one-step Undo.

# Evidence And Verification

- The final correction-focused offscreen suite passed 32 tests for typed input,
  paste/clear/Undo, PFC Pi, selection, and baseline workflow.
- The impacted offscreen regression passed 285 tests across Data Mapping,
  mapping core/persistence/runtime/bootstrap, Data Definition integration, and
  Train shell.
- Structure validation passed with existing warning-first Data Mapping panel
  and service hotspots; the correction adds only status binding in the panel
  and command-boundary coercion in the service.
- Protected fixtures and `data/mapping.json` remain unchanged.

# Changed Files

- Shared mapping value/type policy, validation, and persistence
- Data Mapping application mutation boundary and presentation metadata
- Spreadsheet selection, overflow preflight, and status feedback
- Focused typed-value, overflow, rectangle, and existing selection tests

# Known Risks

Computer Use must not repeat the known AppKit accessibility table click. Native
interaction evidence still requires physical user input in the prepared
synthetic session; automated regression is not a substitute. Slice 2D remains
out of scope.
