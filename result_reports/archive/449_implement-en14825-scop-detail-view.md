# 449 Implement EN14825 SCOP Detail View

## Goal

Expose EN14825 SCOP declared/tested bin diagnostics in the main UI through the
existing calculator detail-panel pattern without changing the core result or
calculation contract.

## Scope

- Preserve each completed declared/tested `bin_details` payload additively in
  `ScopResultSummary`.
- Normalize raw core rows through an EN14825 SCOP UI schema/formatter.
- Add dynamic climate/source selection, detail visibility, status clearing,
  copy/CSV ownership, and visible-content refit notification to the SCOP section.
- Add focused adapter, formatter, lifecycle, no-data, and error-state tests.

## Non-goals

- No core/config/schema/fixture/golden, EN14825 SEER, AHRI, batch, sample-data,
  public-result, or common panel behavior change.
- No test-point contribution or seasonal-summary table.

## Task Results

- The adapter copies valid core bin rows into separate declared/tested tuple
  payloads while preserving every existing summary field and status path.
- The SCOP schema exposes prioritized bin evidence: Tj, hours, Ph, Pdh, COPpl,
  equivalent power, ELBU, operating case, capacity source, and COP source. Raw
  diagnostic-only keys are not passed to the table.
- Only sources with completed bin rows enter the selector. Active-climate
  changes rebuild that source set; invalid input and calculation errors clear
  stale rows and show an explicit status.
- The shared `BinDetailPanel`, read-only trace table, graph, copy, and CSV paths
  are reused. The toggle invokes the existing visible-content refit callback.

## Table / Surface Parity

- Reused owner: `BinDetailPanel` and `BinTraceTable`; no new table interaction
  controller or export implementation was created.
- Read-only selection/copy/export/status behavior therefore remains on the
  established toolkit adapter path. No paste/edit/undo contract applies to
  this read-only diagnostic surface.

## Verification

- `python3 -B -m pytest tests/test_apps_calculator_ui_en14825_scop.py tests/test_ui_tk_en14825_scop_detail.py`
  — 34 passed.
- `python3 -B tools/check_code_structure.py` — no errors; existing EN14825
  section soft-LOC warnings remained, and the new map freshness reminder was
  resolved by regeneration.
- `python3 -B tools/code_checker/build_reference_map.py --check` — stale before
  regeneration because of prior commit metadata and the new source; regenerated
  once with `python3 -B tools/code_checker/build_reference_map.py`.
- `git diff --check` — passed.
- `python3 -B tools/check_agent_change_gate.py --cached` — passed.

## Soft-Limit Triage

- `en14825_scop_section.py` remains a legacy large owner for climate widget
  composition, input state, result cards, batch lifecycle, and detail surface
  wiring. The profile-specific row normalization was extracted instead of
  adding it to the section. The remaining toggle/source coordination belongs
  to this section lifecycle for this slice.
- `scop_adapter.py` crossed the soft line threshold only through the additive
  result-copy boundary. A broad adapter split would exceed this focused scope.
- Accepted for this slice. The next code slice targets EN14825 SEER rather than
  adding another responsibility to the SCOP owners.

## Manual Check

Required: open EN14825 SCOP, verify Average Declared/Tested source switching,
detail graph/table/copy/CSV, climate activation invalidation, and main-window
refit while opening and closing the detail surface.

## Changed Files

- `apps/calculator/ui/en14825/scop_adapter.py`
- `apps/calculator/ui/en14825/scop_models.py`
- `apps/calculator/ui/sections/bin_detail_schema.py`
- `apps/calculator/ui/sections/en14825_scop_detail.py`
- `apps/calculator/ui/sections/en14825_scop_section.py`
- `tests/test_apps_calculator_ui_en14825_scop.py`
- `tests/test_ui_tk_en14825_scop_detail.py`
- `docs/WORK_PLAN.md`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `result_reports/active/449_implement-en14825-scop-detail-view.md`

## Known Risks

- Geometry and source-selection usability still require local GUI visual smoke.
- The user-provided detail design file was present as a pre-existing untracked
  workspace file and was used as evidence only; it is not part of this change.
- Sample/default performance values remain intentionally unchanged.

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

- `AGENT_TASK_ROUTER.md`: UI/source/report routes only; reason: requested gate
  and report ownership.
- Detail design and empty-state policy: SCOP/detail and dependency ranges only;
  reason: implementation contract and retained-sample boundary.
- SCOP adapter/model/core return: calculation return and summary boundaries;
  reason: preserve existing bin diagnostics without core changes.
- Hong Kong HSPF detail, shared detail panel/schema/table: matching lifecycle,
  schema, status, copy, and export ranges; reason: required reference parity.
- SCOP section/tests: constructor, recalculation, action, and matching focused
  test ranges; reason: profile-local wiring and regression coverage.
- UI surface/table owner docs: result/detail/export and read-only table parity
  ranges; reason: completion gate.
- `docs/WORK_PLAN.md`: current/next ranges; reason: execution-board sync.
- broad read: none
- repeated read: none

## Next Action

EN14825 SCOP visual smoke, then EN14825 SEER detail view implementation.
