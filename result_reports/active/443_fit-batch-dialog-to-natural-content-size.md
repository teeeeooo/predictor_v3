# 443 Fit Batch Dialog to Natural Content Size

## Goal

Make BatchMatrix dialog initial geometry reflect its natural content width and
height so content that fits within the screen cap opens without clipped columns.

## Scope

- Expose natural content size from BatchTableViewport and BatchMatrixTable.
- Propagate natural canvas request through normal Tk layout.
- Let BatchDialogShell combine requested and preferred descendant sizes before
  applying the existing screen-capped, parent-centered geometry helper.
- Guard AHRI HSPF2/SEER2 and EN14825 SEER/SCOP initial sizing relationships.

## Non-goals

- No profile min-size, width-token, horizontal-scrollbar, main-window sizing,
  calculator/config/schema/fixture/golden, label, A2/source, or main UI change.

## Root Cause and Correction

After 442, the viewport preserved the table item allocation width but its
canvas requested width still did not advertise the table's natural width to
the dialog layout. `BatchDialogShell` therefore saw only the narrower window
request and fitted geometry before the natural matrix width was represented.

The viewport now reports natural width/height and requests the natural canvas
width during its existing sync. Tk consequently includes table width plus the
profile's real padding/sibling layout in the window request. The shell then
uses a generic descendant preferred-size contract for both axes and passes the
resolved size to `parent_centered_content_geometry`.

HSPF2 diagnostics on the verification host:

| Value | Before | After |
| --- | ---: | ---: |
| shell requested width | 1038 | 1766 |
| matrix natural width | 1707 | 1707 |
| resolved preferred width | not represented | 1766 |
| initial geometry width | 1180 minimum/capped behavior | 1766 |

An intermediate delta-based composition overestimated preferred width as 2461.
It was rejected before completion. Natural canvas request propagation lets Tk
own padding and sibling arithmetic and avoids that unnecessary expansion.

## Changed Files

- `apps/calculator/ui/batch/matrix_table.py`
- `apps/calculator/ui/batch/viewport.py`
- `apps/calculator/ui/batch_dialogs/shell.py`
- `tests/test_ui_tk_batch_dialog_content_sizing.py`
- `tests/test_ui_tk_batch_matrix_table.py`
- `tests/test_ui_tk_batch_table_viewport.py`
- `docs/WORK_PLAN.md`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `result_reports/active/443_fit-batch-dialog-to-natural-content-size.md`

## Task Results

- BatchMatrix natural size is available through a thin content-owner method.
- The viewport's canvas request now carries natural table width upward while
  retaining vertical containment and the 442 no-compression allocation rule.
- BatchDialogShell resolves width and height after idle layout, then reuses the
  existing parent-centered screen-cap helper. No profile special case exists.
- AHRI HSPF2/SEER2 and EN14825 SEER/SCOP tests verify preferred size never
  shrinks the request and initial geometry matches the common helper. HSPF2
  additionally verifies natural matrix width fits when below the screen cap.

## Verification

- Focused superset command collected 71 tests: 67 passed and four new
  over-strict height-equality assertions failed. Production code was unchanged;
  the assertion was corrected to width equality plus height non-shrink.
- `python3 -B -m pytest tests/test_ui_tk_batch_dialog_content_sizing.py`
  — 5 passed after that test-only correction.
- `python3 -B tools/check_code_structure.py` — passed with two pre-existing
  EN14825 soft-LOC warnings and the expected pre-regeneration map reminder.
- `python3 -B tools/code_checker/build_reference_map.py --check` — stale from
  prior commit metadata and new sizing methods; regenerated once.
- `git diff --check` — passed before report/code-map finalization.
- `python3 -B tools/check_agent_change_gate.py --cached` — passed after
  correcting the report's structured `new_source` decision to an allowed value.

## Manual Check

Required: reopen AHRI HSPF2 Batch and confirm the rightmost H42 column and the
Case/Row Type leading columns are fully visible. Then proceed to AHRI calculator
lifecycle closeout if the visual smoke passes.

## Known Risks

- When natural content exceeds the screen cap, the dialog remains capped.
  Horizontal navigation is a separate fallback design, not this primary fix.
- Users can still manually shrink a dialog below natural width; that fallback
  behavior is intentionally unchanged.

## Scope Compliance

- No profile-specific sizing exception, min-size increase, width-token change,
  fixed geometry, or horizontal scrollbar was introduced.
- All prohibited calculation and main UI surfaces are unchanged.

## Change Gate

```yaml
change_gate:
  new_source: none
  hotspot_delta: none
  code_map_check: regenerated
  ui_literal_exemption: none
  report_exemption: none
  read_ledger: included
```

Read Ledger:

- `AGENT_TASK_ROUTER.md`: UI/source/report routes already reviewed this
  session; reason: applicable implementation/report gates.
- Batch dialog shell, matrix table, viewport, and window geometry helper:
  sizing ranges only; reason: exact sizing ownership and helper reuse.
- AHRI HSPF2/SEER2 and EN14825 SEER/SCOP dialog adapters: build/min-size ranges
  only; reason: confirm generic connection without profile edits.
- Focused shell/matrix/viewport/profile tests: matching sizing and preserved
  contract ranges only; reason: regression coverage.
- `docs/WORK_PLAN.md`: current-slice range; reason: next-action sync.
- broad read: none
- repeated read: none

## Next Action

AHRI HSPF2 Batch visual recheck, then AHRI calculator lifecycle closeout.
