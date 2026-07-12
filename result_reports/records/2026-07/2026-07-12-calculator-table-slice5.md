```yaml
record:
  date: 2026-07-12
  topic: calculator-table-slice5
  tags: calculator, tkinter, treeview, detail, trace, migration
  memory_review: no-change
  memory_reason: Existing table-family memory already states that large detail tables retain Treeview through a shared style adapter.
change_gate:
  new_source: small
  hotspot_delta: none
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

# Change Reason

Approved Slice 5 required large detail/trace tables to retain Treeview while
adopting the shared Calculator table visual language.

# Contract / Behavior Changed

A small table-package adapter now owns the detail Treeview style name, body and
heading typography, row height, restrained border, and selection binding.
`BinTraceTable` applies that adapter without moving column definitions, row
insertion, scrollbars, source selection, copy/CSV, visibility, refit, or graph
ownership.

# Evidence And Verification

- 130 focused detail schema, formatter, source, visibility, copy/CSV, and refit tests passed.
- Targeted Python compilation and whitespace checks passed.
- Style lookup tests cover the shared body/header/selection bindings.
- Structure guard completed with only unchanged legacy warnings.

# Changed Files

- `apps/calculator/ui/table/treeview_style.py`
- `apps/calculator/ui/sections/bin_trace_table.py`
- focused detail Treeview adapter tests
- `docs/WORK_PLAN.md`

# Known Risks

Some OS-native Tk themes may ignore individual Treeview heading options even
though the shared style remains configured. No manual platform visual smoke was
performed; schema, selection mapping, scrolling, source switching, copy/CSV,
visibility, and refit behavior remain automatically guarded. Graphs were not
changed.
