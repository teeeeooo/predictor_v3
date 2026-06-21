# 453 Implement AHRI HSPF2 Detail View

## Goal

Expose the existing AHRI HSPF2 core bin diagnostics through the shared detail
surface without changing equations, public results, source mapping, A2 input,
batch behavior, or sample data.

## Scope

- Preserve core `bin_details` additively in `AhriHspf2Summary`.
- Normalize first-pass HSPF2 rows through a profile schema/formatter.
- Add a single-source detail toggle/panel and stale-row clearing lifecycle.
- Connect detail visibility to the existing AHRI visible-content refit path.
- Add focused adapter, formatter, section, refit, and batch regression tests.

## Non-goals

- No core/config/schema/fixture/golden, SEER2, EN14825, sample, source mapping,
  A2, batch result, fixed geometry, token cleanup, contribution, or seasonal
  summary change.

## Task Results

- The adapter now requires and copies valid core bin rows after reading the
  unchanged HSPF2/totals/source fields. Missing or malformed detail payloads
  fail explicitly at the adapter boundary rather than producing plausible UI.
- The HSPF2 schema exposes Tj, hours, case, building load, low/intermediate/full
  capacities, COPbin, compressor/auxiliary/total heat and energy. `debug_info`
  and other raw diagnostics are excluded by the formatter.
- The shared `BinDetailPanel` uses one hidden selector source named HSPF2 and
  inherits the common vertical/horizontal scrollbar, graph, copy, CSV, and
  status behavior.
- Input edits and optional-point toggles clear stale detail immediately before
  debounce. Incomplete, invalid, and calculation-error paths leave explicit
  status rows; successful recalculation repopulates detail.
- AHRI tab construction passes its existing visible-lifecycle refit callback
  into the section. This is thin parent wiring only; tab sizing policy is
  unchanged.

## Verification

- `python3 -B -m pytest tests/test_apps_calculator_ui_ahri_hspf2.py tests/test_ui_tk_ahri_hspf2_detail.py tests/test_ui_tk_ahri_hspf2_batch.py`
  — 23 passed.
- `python3 -B tools/check_code_structure.py` — no errors; unchanged legacy
  EN14825 soft warnings and code-map freshness reminder only.
- `python3 -B tools/code_checker/build_reference_map.py --check` — stale from
  prior commit metadata and new structural sources; regenerated once.
- `git diff --check` — passed.
- `python3 -B tools/check_agent_change_gate.py --cached` — passed.

## Contract Preservation

- Existing A2 capacity-only placeholder behavior is unchanged.
- H12/H22/H42 measured/calculated/not-provided mapping is unchanged.
- HSPF2 batch remains HSPF2-only and its optional snapshot lifecycle tests pass.
- Core result keys/equations and DEV sample ownership are unchanged.

## Reference Parity

- Reused the EN14825/Hong Kong detail lifecycle and shared panel rather than
  creating an AHRI-local table/export implementation.
- The HSPF2-specific formatter owns units and column selection; raw core rows
  never flow directly into the UI table.

## Structure Triage

- `ahri_hspf2_section.py` gained bounded composition/lifecycle wiring and
  remains below the section soft limit. Row transformation was split into the
  new profile formatter.
- `hspf2_adapter.py` remains below the source soft limit and owns only the
  additive core-result boundary.

## Manual Check

Required: open AHRI HSPF2, verify the hidden single-source selector, wide-table
horizontal navigation, vertical scrolling, optional-point invalidation,
copy/CSV, and main-window refit while opening/closing detail.

## Changed Files

- `apps/calculator/ui/ahri/hspf2_adapter.py`
- `apps/calculator/ui/sections/ahri_hspf2_detail.py`
- `apps/calculator/ui/sections/ahri_hspf2_section.py`
- `apps/calculator/ui/sections/bin_detail_schema.py`
- `apps/calculator/ui/tabs/ahri210240_tab.py`
- `tests/test_apps_calculator_ui_ahri_hspf2.py`
- `tests/test_ui_tk_ahri_hspf2_detail.py`
- `docs/WORK_PLAN.md`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `result_reports/active/453_implement-ahri-hspf2-detail-view.md`

## Known Risks

- Wide-table discoverability and geometry still require local macOS visual smoke.
- The selector is intentionally hidden for the single HSPF2 source; future
  multiple source support requires a separate contract.

## Change Gate

```yaml
change_gate:
  new_source: split
  hotspot_delta: accepted-for-slice
  code_map_check: regenerated
  ui_literal_exemption: none
  report_exemption: none
  read_ledger: included
```

Read Ledger:

- `AGENT_TASK_ROUTER.md`: UI/source/report routes already reviewed; reason:
  implementation and report gates.
- Detail design, empty-state policy, reports 449/451/452: HSPF2 schema,
  lifecycle, retained-sample, and scrollbar decisions; reason: approved parity.
- HSPF2 core: v3 bin row and return ranges only; reason: confirm existing data
  without changing calculation/public results.
- HSPF2 adapter/section/tab and focused tests: matching result, lifecycle,
  optional, refit, source, A2, and batch ranges; reason: bounded wiring.
- Shared detail schema/panel/table: public constructor/status/scroll contracts;
  reason: reuse common owners.
- `docs/WORK_PLAN.md`: current/next ranges; reason: execution-board sync.
- broad read: none
- repeated read: none

## Next Action

AHRI HSPF2 visual smoke, then AHRI SEER2 detail view implementation.
