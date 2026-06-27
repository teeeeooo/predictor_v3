# 479 Detail Toggle Lifecycle Boundary Audit

## Goal

Decide whether repeated detail-toggle mechanics should share an owner without
bypassing `ProfileVisibleContentLifecycleController` or moving view behavior
into profile tabs.

## Evidence

- Eight sections keep `_detail_visible` only for their local toggle method.
- Every method shows/removes `BinDetailPanel`, updates the same two button
  labels, and then invokes a visibility callback.
- Four profiles refresh detail sources immediately before showing; four rely on
  recalculation to keep the panel current. Grid row differs by section.
- Tabs pass callbacks into sections; the lifecycle controller owns settled
  measurement/refit scheduling through `on_detail_visibility_changed()`.
- Focused lifecycle and detail suites: 91 tests passed.

## Decision

**Accept a section-layer view helper as a later implementation candidate, but
do not put toggle mechanics in the visible-content lifecycle controller.**

A possible `DetailPanelVisibility` helper may own visible state, panel
`grid`/`grid_remove`, button text, configured grid row/options, optional
`before_show`, and the post-change callback. Sections retain detail source/data
refresh. The callback must continue to terminate at the tab-composed
`ProfileVisibleContentLifecycleController` named trigger.

The lifecycle controller must not learn `BinDetailPanel`, buttons, grid rows,
or profile data. Tabs must not manipulate detail widgets or instantiate
measurement/refit primitives.

## Implementation Prompt Requirement

Before implementation, specify:

- one section/view helper owner, no lifecycle-package expansion;
- optional `before_show` callback preserving the four refresh-before-show
  profiles;
- section-supplied grid options and unchanged Korean labels;
- guard tests for one callback per toggle, refresh ordering, repeated show/hide,
  and controller coalescing;
- no public section/tab interface, payload, schema, or geometry-cycle changes.

This candidate should follow, not precede, the smaller detail coercion helper
slice selected as the immediate next action.

## Changed Files

- `docs/WORK_PLAN.md`
- `result_reports/active/479_detail-toggle-lifecycle-boundary-audit.md`

## Architecture Judgment

The boundary separates view state from geometry lifecycle orchestration:
sections compose a reusable detail visibility view helper; tabs forward events;
the existing controller remains the only refit owner. Moving widget toggling
into the lifecycle controller would violate MVC/SoC, while a base section class
would couple unrelated profile views and is rejected as overengineering.

## Known Risks

- Refresh-before-show ordering differs and must be explicit, not inferred.
- Large EN sections would benefit from line reduction, but hotspot pressure is
  not authorization to skip the helper's Design Gate.
- Active reports exceed the normal review threshold; lifecycle cleanup remains
  explicitly excluded from this arc.

## Verification

- Focused lifecycle/detail suites: 91 tests passed.
- Diff check passed; cached gate recorded at commit closeout.

## Change Gate

```yaml
change_gate:
  new_source: none
  hotspot_delta: none
  code_map_check: not_required
  ui_literal_exemption: none
  report_exemption: none
  read_ledger: included
```

Read Ledger:

- eight `_toggle_detail` ranges and `_detail_visible` usage search; reason:
  compare state, refresh, grid, labels, and callback ordering.
- lifecycle controller: complete 123-line owner file; reason: confirm named
  trigger and primitive composition boundary.
- approved lifecycle design: complete owner/responsibility/invariant sections;
  reason: prevent a proposed helper from bypassing the controller.
- focused lifecycle/detail tests: selected trigger and visibility assertions;
  reason: behavior evidence.
- broad read: none.
- repeated read: none.

## Commit / Push

Audit-only commit; published with the complete arc.

## Next Suggested Action

Implement the pure detail formatting coercion helper defined by report 476.
