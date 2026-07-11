```yaml
record:
  date: 2026-07-12
  topic: calculator-table-slice2
  tags: calculator, tkinter, compact-result, result-panel, brazil, migration
  memory_review: no-change
  memory_reason: The existing Calculator table-family memory already names generic result and Brazil as progressive Compact Result Grid adopters.
change_gate:
  new_source: none
  hotspot_delta: none
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

# Change Reason

Approved Slice 2 required generic result summaries and Brazil result/Rule grids
to adopt the shared compact-result foundation without changing profile meaning.

# Contract / Behavior Changed

`ResultPanel` now uses shared flat grid surfaces and cell primitives while
retaining its registries, stable in-place updates, text compatibility, and
external-focus preservation. Brazil composes two `CompactResultGrid` instances,
keeps Rule tone and Final decisions local, and rebinds keyboard copy to its
sectioned export document. Brazil-local generic grid construction was removed.

# Evidence And Verification

- 218 focused result, Brazil, dependent profile, auto-calc, lifecycle, and refit tests passed.
- Targeted Python compilation and whitespace checks passed.
- Structure guard completed with only unchanged legacy warnings.
- Tests preserve Brazil Result/Rule/Final TSV and CSV output exactly.

# Changed Files

- `apps/calculator/ui/result_panel.py`
- `apps/calculator/ui/brazil_cspf/result_surface.py`
- focused ResultPanel and Brazil tests
- `docs/WORK_PLAN.md`

# Known Risks

Remaining simple result surfaces are intentionally unmigrated until Slice 3.
No manual platform visual smoke was required; flat-surface, alignment, focus,
semantic-tone, export, and sizing behavior are covered by focused Tk tests.
