# 461 Implement AHRI SEER2 Detail View

## Goal

Expose the existing AHRI SEER2 core bin diagnostics through the shared detail
surface while preserving equations, totals, batch behavior, and lifecycle owner
boundaries.

## Result

- `AhriSeer2Summary` now additively preserves validated `bin_details`.
- Missing or malformed bin rows fail explicitly at the adapter boundary.
- Added an AHRI SEER2 formatter and schema for bin, temperature, operating case,
  load, low/intermediate/full capacity and EER, bin EER, cooling, and energy.
- Raw core dictionaries do not flow directly into the table.
- Added a hidden single-source selector detail panel with existing table, graph,
  copy, CSV, status, and scroll behavior.
- Input changes clear stale rows immediately; incomplete, invalid, calculation
  error, empty detail, and success paths set explicit states.
- AHRI tab wiring routes the SEER2 toggle through the common controller's named
  detail trigger. HSPF2 and batch behavior remain unchanged.

## Verification

- Final focused contract set: SEER2 adapter/main 11, SEER2 detail 5, AHRI window
  lifecycle 3, HSPF2 detail regression 6 — 25 tests passed.
- The first run exposed a one-row fake that could not form a graph line; the fake
  was corrected to match the real core's multi-bin contract without changing the
  shared graph owner.
- `python3 -B tools/check_code_structure.py` — no errors; three existing source
  soft warnings plus code-map freshness reminder only.
- Code-map check was stale after new source/schema structure; regenerated once.
- `git diff --check` — passed.
- `python3 -B tools/check_agent_change_gate.py --cached` — passed.

## Contract Preservation

- Core calculation and return keys are unchanged.
- Seasonal total scaling and required result validation remain unchanged.
- SEER2 batch and HSPF2 main/detail/batch behavior are unchanged.
- Sample/default performance values remain until task 8.
- No contribution or seasonal summary table was added.

## Changed Files

- `apps/calculator/ui/ahri/seer2_adapter.py`
- `apps/calculator/ui/sections/ahri_seer2_detail.py`
- `apps/calculator/ui/sections/ahri_seer2_section.py`
- `apps/calculator/ui/sections/bin_detail_schema.py`
- `apps/calculator/ui/tabs/ahri210240_tab.py`
- `tests/test_apps_calculator_ui_ahri_seer2.py`
- `tests/test_ui_tk_ahri_seer2_detail.py`
- `docs/WORK_PLAN.md`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `result_reports/active/461_implement-ahri-seer2-detail-view.md`

## Change Gate

```yaml
change_gate:
  new_source: small
  hotspot_delta: accepted-for-slice
  code_map_check: regenerated
  ui_literal_exemption: none
  report_exemption: none
  read_ledger: included
```

Hotspot reason: the SEER2 section gained only detail view composition and state
wiring; formatter/schema transformation stays outside the section and the file
remains below the soft limit.

Read Ledger:

- detail design and HSPF2/EN reference pattern: adapter/formatter/panel lifecycle;
  reason: parity without raw-schema copying.
- SEER2 core return bin range only; reason: confirm existing payload keys without
  core modification.
- SEER2 adapter/section and focused tests: matching result and lifecycle ranges;
  reason: bounded additive implementation.
- shared detail schema/panel public contracts; reason: reuse existing owner.
- broad read: none
- repeated read: fake calculator row shape after graph failure.

## Next Action

EN14825/AHRI detail arc closeout.
