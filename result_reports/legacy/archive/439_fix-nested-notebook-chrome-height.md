# 439 Fix Nested Notebook Chrome Height

## Goal

Correct sticky nested-notebook chrome-height arithmetic without changing tab
layout, widget allocation, window geometry policy, or profile UI structure.

## Scope

- Derive height chrome from the tallest requested tab, matching the existing
  widest-tab width philosophy.
- Correct `nested_max_tab_height` diagnostics semantics.
- Extend relationship-based AHRI, EN14825, and ISO Hong Kong diagnostics.
- Preserve AHRI round-trip and HSPF2 Batch lifecycle checks.

## Non-goals

- No window shell/geometry/refit/scrollable-frame, tab/section layout, fixed
  geometry/minsize, table/token, A2/source, batch label, calculator, core,
  config, fixture, golden, or unrelated refactor change.

## Changed Files

- `apps/calculator/ui/window_measurement.py`
- `tests/test_ui_tk_window_measurement_side_effect_free.py`
- `tests/test_ui_tk_visible_sizing_diagnostics.py`
- `docs/WORK_PLAN.md`
- `result_reports/active/439_fix-nested-notebook-chrome-height.md`

## Task Results

- `_measure_nested_notebook()` now collects requested widths and heights for
  every tab without selecting hidden tabs.
- `widest_tab_width` remains unchanged; `tallest_tab_height` now owns the
  height counterpart.
- The one-time height chrome estimate is
  `max(0, notebook_height - tallest_tab_height)`.
- `NestedNotebookMeasurement.max_tab_height` and its diagnostic now report the
  actual tallest requested child rather than the current child.
- Snapshot replacement continues to use chrome plus the current tab request;
  no widget size is configured or forced.

## Before / After Diagnostics

macOS Tk values after explicit visible-content fits:

| State | Chrome before | Chrome after | Snapshot before | Snapshot after |
|---|---:|---:|---:|---:|
| AHRI SEER2 | 365 | 62 | 999x723 | 999x420 |
| AHRI HSPF2 | 365 | 62 | 1290x1026 | 1290x723 |
| EN SEER | 140 | 62 | 803x973 | 803x895 |
| EN SCOP | 140 | 62 | 1389x1051 | 1389x973 |

AHRI SEER2 -> HSPF2 -> SEER2 returns exactly to 999x420. HSPF2 Batch
open/close leaves the main root geometry unchanged. ISO Hong Kong CSPF/HSPF
uses a 62px chrome estimate and its CSPF round trip is stable.

## Correction Judgment

The arithmetic correction is accepted: the contaminated sibling-height portion
is removed and all three profile families satisfy
`chrome = notebook request - tallest tab request`.

Final visible white-space acceptance remains manual. AHRI SEER2 vertical
overflow increases from 44 to 347 because the corrected target is smaller while
the scrollregion still reflects the sticky notebook request. The existing
policy intentionally excludes overflow from the fit; changing that or syncing
selected-child allocation is outside this slice. If manual smoke still shows
the defect or unacceptable scrolling, selected-child allocation sync is the
next sizing design candidate; no speculative second patch was added here.

## Verification

- Focused sizing/measurement suites: 14 passed.
- `python3 -B tools/check_code_structure.py` — passed with only two pre-existing
  EN14825 soft-LOC warnings and the expected code-map metadata reminder.
- `python3 -B tools/code_checker/build_reference_map.py --check` — stale only
  by parent-SHA/dirty-tree metadata; no top-level symbol or file structure
  changed, so regeneration was not required.
- `git diff --check` — passed.
- `python3 -B tools/check_agent_change_gate.py --cached` — passed.

## Manual Check Required

- AHRI SEER2/HSPF2 lower white space and scrolling usability.
- AHRI metric-switch geometry stability.
- HSPF2 Batch open/close root-size stability.
- EN14825 SEER/SCOP and ISO Hong Kong CSPF/HSPF sizing regression.

## Known Risks

- Exact sizes vary by theme/display scale; tests assert relationships and
  round-trip stability.
- Correct snapshot arithmetic does not itself change Tk notebook requested
  allocation inside the scrollregion.

## Scope Compliance

- Only nested measurement arithmetic, focused diagnostics/tests, work plan,
  and this report changed.
- No UI literal exemption is needed; no new presentation literal was added.
- No top-level production symbol changed, so code-map regeneration is not
  expected unless the required check finds a structural delta.

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
- `apps/calculator/ui/window_measurement.py`: snapshot and nested measurement
  ranges only; reason: arithmetic owner.
- focused measurement/side-effect/visible diagnostic tests: matching ranges;
  reason: diagnostics semantics and profile regressions.
- reports 435/436: values and rejected wrapper conclusion already established
  in this session; reason: before/after baseline without reread.
- `docs/WORK_PLAN.md`: current-slice range; reason: next-action sync.
- broad read: none
- repeated read: none

## Next Action

HSPF2 A2 capacity-only and source mapping polish.
