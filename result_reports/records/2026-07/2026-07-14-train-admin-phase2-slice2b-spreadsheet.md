```yaml
record:
  date: 2026-07-14
  topic: train-admin-phase2-slice2b-spreadsheet
  tags: train-admin, mapping, phase-2, slice-2b, spreadsheet, undo, pfc
  memory_review: updated
  memory_reason: Preserve the Data Mapping interaction and service-owned command boundaries before Slice 2C state workflow work.
change_gate:
  new_source: split
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

# Change Reason

Slice 2A established a table-centric editor but left row-only selection and no
spreadsheet clipboard, clear, keyboard, or grouped undo behavior. Its recorded
pre-Slice-2B trigger also required panel/controller responsibility separation.

# Contract / Behavior Changed

- The panel composes the screen while feature-local toolbar and table owners
  bind action state, selection, TSV clipboard, clear, navigation, and edit entry.
- The controller orchestrates commands while pure snapshot presentation lives
  in a separate feature owner.
- The service owns current draft and draft-level command history, so edit,
  rectangular paste, clear, CRUD, and F&T-to-PFC Pi clearing each undo as one
  user intent without a Qt shadow draft.
- PFC Pi is read-only in the model and rejected again at the service command
  boundary. Clipboard coordinates remain fixed, so protected targets do not
  shift later values into adjacent columns.
- Dynamic definition-backed columns use the same paste, clear, selection, and
  undo paths without panel field lists.

# Evidence And Verification

- Eight focused offscreen spreadsheet tests cover rectangular selection, TSV,
  paste shapes, Delete/Backspace, replace-on-type, navigation, PFC guard,
  dynamic columns, CRUD selection, and grouped undo.
- The Slice 2B intermediate regression passed 131 service/controller/UI,
  dynamic requirement, editor command/projection/validation/persistence, and
  Train shell tests.
- The structure gate is warning-only. Controller projection was reduced from
  the prior hotspot into a 220 LOC command owner; toolbar, interaction,
  presentation, and draft session are bounded feature owners.

# Changed Files

- Data Mapping feature-local toolbar and spreadsheet table view
- Data Mapping presentation projector and service-owned draft session
- Mapping service/controller/model command boundaries
- Focused spreadsheet interaction tests

# Known Risks

The panel remains above the 400 LOC soft limit because it still composes the
complete Slice 2A workspace and model binding. No spreadsheet behavior was
added there. Redo and non-contiguous selection semantics are not required for
this slice. Native interaction evidence is deferred to the bounded Batch check
after Slice 2C; Slice 2D export/import is not started.
