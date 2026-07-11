```yaml
record:
  date: 2026-07-12
  topic: calculator-table-foundation
  tags: calculator, tkinter, table, architecture, compact-result, iso-iseer
  memory_review: updated
  memory_reason: The three-family table architecture and first shared Tk visual owner are durable migration boundaries.
change_gate:
  new_source: split
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

# Change Reason

Calculator table visuals were repeated inside editable and small-result views,
and the approved architecture requires three explicit table families over one
shared Tk presentation policy.

# Contract / Behavior Changed

The UI table package now owns the Tk visual policy, small grid primitives, and
Compact Result Grid. ISO/ISEER is the representative migration: its editable
matrix opts into the shared flat grid and its fixed result no longer uses
Treeview. Existing interaction controllers, logical result rows, status text,
copy/export data, auto-calculation, profile routing, and lifecycle remain
unchanged. Other table families and profiles remain unmigrated.

# Evidence And Verification

- 193 focused table, ISO, empty-state, lifecycle, refit, and token tests passed.
- Targeted Python compilation passed.
- Structure guard completed; warnings were unchanged legacy hotspots.
- Cached whitespace and agent change-gate hard checks passed.
- `MetricInputTable` remains the editable view/protocol owner. Its net growth is
  accepted for Slice 1 because the new responsibility is delegated to three
  bounded shared modules; further growth requires renewed hotspot triage.

# Changed Files

- `apps/calculator/ui/table/`
- `apps/calculator/ui/metric_input_table.py`
- `apps/calculator/ui/sections/iso_iseer_2point_*`
- focused Tk Calculator tests
- active Calculator table design and current-state documents

# Known Risks

Only ISO/ISEER uses the new foundation. Temporary visual duplication remains in
unmigrated profiles by design, and must be removed only in their approved
migration Slices. Automated Tk assertions cover roles and compatibility; no
platform-specific manual visual smoke was required for this Slice.
