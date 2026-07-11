```yaml
record:
  date: 2026-07-12
  topic: calculator-table-slice4
  tags: calculator, tkinter, batch, editable-matrix, viewport, migration
  memory_review: no-change
  memory_reason: Existing table-family and batch-lifecycle memory already preserves the shared visual seam, controller, snapshot, and viewport boundaries.
change_gate:
  new_source: none
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

# Change Reason

Approved Slice 4 required both batch table shapes to consume the shared visual
foundation without changing their distinct logical models or workflow behavior.

# Contract / Behavior Changed

`BatchCaseTable` and `BatchMatrixTable` now construct flat header/body cells
through the shared grid primitives. Their canvas viewport content also uses the
shared no-heavy-outer-edge surface. Existing controllers, logical row/case
models, overlays, snapshots, scroll containment, auto-calc, status counts, and
copy/CSV contracts remain unchanged. Action-row wording and ordering were not
changed.

# Evidence And Verification

- 130 focused batch table, controller, snapshot, viewport, dialog, profile, and export tests passed.
- 38 shared foundation, compact result, and Brazil regression tests passed.
- Targeted Python compilation and whitespace checks passed.
- Structure guard completed with only unchanged legacy warnings.

# Changed Files

- `apps/calculator/ui/batch/case_table.py`
- `apps/calculator/ui/batch/matrix_table.py`
- `apps/calculator/ui/batch/viewport.py`
- shared grid primitive focus metadata
- focused batch visual-family tests
- `docs/WORK_PLAN.md`

# Known Risks

`BatchMatrixTable` remains an existing over-400-LOC cohesive owner for logical
case state, surface protocol, viewport composition, and rendering. This Slice
reduced local construction duplication without adding responsibility; any
future responsibility addition should first audit a construction/view split.
No manual platform smoke was required.
