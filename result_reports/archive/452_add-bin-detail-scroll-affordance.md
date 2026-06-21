# 452 Add Bin Detail Scroll Affordance

## Goal

Make additional rows and horizontally overflowed columns discoverable and
navigable on the shared read-only bin-detail table, especially on macOS where
overlay scrollbars can otherwise be easy to miss.

## Scope

- Keep the existing vertical scrollbar connection.
- Add an always-present horizontal scrollbar and connect Treeview x-scrolling.
- Stabilize Treeview/scrollbar placement inside the common table owner.
- Add focused widget-contract coverage and retain SEER/SCOP detail behavior.

## Non-goals

- No calculation, detail payload, formatter/schema, profile-specific sizing,
  fixed geometry, batch, sample-data, or AHRI change.
- No yview/top-position reset behavior change.

## Root Cause and Result

- `BinTraceTable` previously packed the Treeview beside only a vertical
  scrollbar. Wide schemas had no horizontal navigation affordance, and macOS
  scrollbar styling made overflow difficult to discover.
- The table frame now uses a stable grid: Treeview at the upper-left, vertical
  scrollbar at the right, and an always-present horizontal scrollbar below the
  Treeview. Neither scrollbar can displace the other outside this local frame.
- `yscrollcommand`/vertical command remain connected; `xscrollcommand` and the
  horizontal command are added. Column sizes and all data paths are unchanged.
- Existing status behavior continues hiding the complete table frame when no
  rows exist; copy/export continue to use the same normalized row model.

## Verification

- `python3 -B -m pytest tests/test_ui_tk_bin_detail_schema.py tests/test_ui_tk_en14825_seer_detail.py tests/test_ui_tk_en14825_scop_detail.py`
  — 31 passed after adapting two test assertions to Tk's Tcl object/callback
  representations.
- `python3 -B tools/check_code_structure.py` — no errors; unchanged legacy
  EN14825 soft warnings and a code-map freshness reminder only.
- `python3 -B tools/code_checker/build_reference_map.py --check` — checked;
  stale commit metadata noted, but no function/module structure changed, so the
  map was not regenerated.
- `git diff --check` — passed.
- `python3 -B tools/check_agent_change_gate.py --cached` — passed.

## Reference Parity

- The existing `BinTraceTable` remains the common owner; no profile-local
  workaround was added.
- Treeview uses the standard bidirectional scrollbar command contract, while
  the existing read-only selection/copy/export/status paths are untouched.

## Changed Files

- `apps/calculator/ui/sections/bin_trace_table.py`
- `tests/test_ui_tk_bin_detail_schema.py`
- `docs/WORK_PLAN.md`
- `result_reports/active/452_add-bin-detail-scroll-affordance.md`

## Known Risks

- Native scrollbar contrast and always-visible styling still depend on the
  operating-system Tk theme; local macOS visual smoke remains required.
- This change provides navigation but does not alter main-window fitting or
  force all columns to be visible simultaneously.

## Change Gate

```yaml
change_gate:
  new_source: none
  hotspot_delta: none
  code_map_check: checked
  ui_literal_exemption: none
  report_exemption: none
  read_ledger: included
```

Read Ledger:

- `AGENT_TASK_ROUTER.md`: UI/source/report routes already reviewed this
  session; reason: applicable implementation/report gates.
- `bin_trace_table.py`: full compact owner; reason: scrollbar/layout and
  copy/export/status preservation.
- Bin detail schema tests and EN14825 SEER/SCOP detail tests: matching widget,
  export, and status ranges; reason: focused regression coverage.
- `docs/WORK_PLAN.md`: current/next ranges; reason: execution-board sync.
- broad read: none
- repeated read: none

## Next Action

EN14825 SEER visual smoke, then AHRI HSPF2 detail view implementation.
