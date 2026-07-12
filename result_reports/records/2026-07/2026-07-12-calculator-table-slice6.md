```yaml
record:
  date: 2026-07-12
  topic: calculator-table-slice6
  tags: calculator, tkinter, en14825, compact-result, migration, closeout
  memory_review: updated
  memory_reason: The table-family migration is now complete across all active Calculator surfaces, replacing the prior Slice-1-only resume state.
change_gate:
  new_source: none
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

# Change Reason

Approved Slice 6 required EN14825 complex surfaces to adopt the shared table
families and close the active Calculator table inventory.

# Contract / Behavior Changed

EN14825 common, design, condition, and climate matrices now use the shared
Editable Matrix visual seam. SCOP Declared/Tested blocks use
`CompactResultGrid` while preserving their stable label registries, status,
visibility, and calculated Tested-row presentation. The remaining Brazil
single input was included by the final active-inventory rule. With every active
caller migrated, the obsolete `MetricInputTable` legacy rendering branch was
removed and shared rendering became its sole visual contract.

Final family inventory:

- Editable Matrix: all active single/common/profile `MetricInputTable` callers,
  `BatchCaseTable`, and `BatchMatrixTable` use shared grid primitives.
- Compact Result Grid: ISO/ISEER, SASO, Brazil result/Rule, Korea midpoint,
  SCOP climate results, and generic `ResultPanel` compact primitives.
- Scrollable Data Table: the only active Calculator Treeview is
  `BinTraceTable`, bound through the shared Treeview style adapter.

# Evidence And Verification

- 279 focused shared-table, controller, EN14825, Brazil, detail, batch, and refit tests passed.
- Source inventory found 20 active `MetricInputTable` construction sites and 20 explicit shared-style bindings.
- Source inventory found one active Treeview construction site, `BinTraceTable`, with the shared adapter.
- Targeted Python compilation, whitespace checks, and structure guard passed; structure output contains only existing warnings.

# Changed Files

- EN14825 tab, SEER/SCOP section wiring, and SCOP compact result surface
- Brazil single input visual binding
- `MetricInputTable` staged legacy-renderer cleanup
- focused EN14825, Brazil, and shared table tests
- active design/index, work plan, project log, and memory seed

# Known Risks

EN14825 SEER/SCOP sections remain existing over-400-LOC hotspots. This Slice
added only visual-policy wiring and reduced the separate SCOP result owner;
design explicitly excluded a concurrent section refactor. Any new section
responsibility should first run a split audit. No manual platform visual smoke
was performed; automated behavior, sizing, focus, role, export, and lifecycle
guards passed.
