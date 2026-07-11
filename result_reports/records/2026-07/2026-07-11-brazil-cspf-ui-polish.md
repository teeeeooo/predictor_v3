```yaml
record:
  date: 2026-07-11
  topic: Brazil CSPF UI polish
  tags: calculator, brazil, cspf, detail, rule-table, batch, tkinter
  memory_review: updated
  memory_reason: Preserve the Brazil single-detail presentation boundary, rule-table semantics, and batch-only result-column policy.

change_gate:
  new_source: none
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

# Change Reason

Complete the Brazil CSPF result UX before the next audit: add shared bin-detail
inspection to the single surface, replace sentence-style Rule labels with a
structured decision table, and reduce only the batch 2-point result columns.

# Contract / Behavior Changed

- The Brazil application result model now supplies 3-point/2-point bin detail
  sources and display summaries, plus explicit compact rule condition text;
  core `BrazilCspfComplianceResult`, raw results, formulas, and golden values
  remain unchanged.
- Brazil single reuses `BinDetailPanel` and `DetailPanelVisibility` for source
  selection, graph/table rendering, detail copy/CSV export, stale clearing, and
  the existing tab lifecycle/refit callback.
- Brazil Rule 1 and Rule 2 render as `Rule | 조건 | 대상값 | 기준값 | 판정`,
  while final status remains a separate semantic result area. Rule values and
  status are consumed from the application/core result rather than recomputed
  in Tk.
- Brazil batch removes only `2-point CSTL` and `2-point CSEC` from its matrix
  result schema, row output, snapshot filtering, Copy All, and CSV export.
  Compatibility constants remain publicly importable; single rows and raw
  2-point results still include CSTL/CSEC.

# Evidence And Verification

- Brazil application/single UI/batch tests passed: `13 passed`.
- Affected Brazil core/golden, shared detail/visibility, lifecycle, and batch
  infrastructure tests passed: `149 passed`.
- Final full active suite passed: `1667 passed, 2 xfailed` in 42.95 seconds.
- Structure guard, calculator/application/UI `py_compile`, and `git diff --check`
  passed. Structure output contained only the existing ten soft warnings.
- The Computer Use smoke launched the Tk window and captured the rendered
  screen, but the accessibility tree exposed only the window/menu and
  coordinate/keyboard events did not reach the widgets. Manual mode/detail
  interaction is therefore skipped; automated Tk smoke covers the same
  states.

# Changed Files

- `apps/calculator/application/brazil_cspf/`
- `apps/calculator/ui/sections/brazil_cspf_section.py`
- `apps/calculator/ui/sections/brazil_cspf_result_table.py`
- `apps/calculator/ui/tabs/iso16358_tab.py`
- `apps/calculator/ui/batch_dialogs/profiles/brazil_cspf/`
- `apps/calculator/ui/layout_constants.py`
- Brazil application/UI tests and `docs/WORK_PLAN.md`

# Known Risks

The result-table owner now renders both the existing comparison table and the
compact rule table (266 LOC); that is one cohesive Brazil result surface and is
accepted for this slice. A broader result-surface expansion should perform a
split audit before adding more responsibilities. Main merge, packaging, and
deployment remain outside this branch.
