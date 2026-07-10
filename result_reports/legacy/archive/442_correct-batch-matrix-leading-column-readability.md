# 442 Correct Batch Matrix Leading Column Readability

## Goal

Prevent shared BatchMatrix Case/Row Type content from being compressed below
its readable requested width and replace AHRI-specific width tokens with a
common batch matrix taxonomy.

## Scope

- Add common BatchMatrix leading, point, primary, secondary, and source width
  tokens.
- Apply one leading-column width policy to header and body widgets.
- Preserve content requested width in the vertical-only batch viewport.
- Migrate AHRI and EN14825 BatchMatrixSpec widths to common tokens.
- Add focused matrix, viewport, AHRI, and EN14825 regression coverage.

## Non-goals

- No core/config/schema/fixture/golden, main UI, A2/source mapping, compact
  label, window sizing/refit, dialog geometry, ISO/SASO, or broad legacy change.

## Changed Files

- `apps/calculator/ui/layout_constants.py`
- `apps/calculator/ui/batch/matrix_table.py`
- `apps/calculator/ui/batch/viewport.py`
- `apps/calculator/ui/ahri/seer2_batch.py`
- `apps/calculator/ui/ahri/hspf2_batch.py`
- `apps/calculator/ui/en14825/seer_batch.py`
- `apps/calculator/ui/en14825/scop_batch.py`
- `tests/test_ui_tk_batch_matrix_table.py`
- `tests/test_ui_tk_batch_table_viewport.py`
- `tests/test_ui_tk_ahri_seer2_batch.py`
- `tests/test_ui_tk_ahri_hspf2_batch.py`
- `tests/test_apps_calculator_ui_en14825_batch.py`
- `docs/WORK_PLAN.md`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `result_reports/active/442_correct-batch-matrix-leading-column-readability.md`

## Task Results

- Common tokens now own Case, Row Type, point, primary result, secondary
  result, and source result widths. Prior AHRI-specific width tokens are gone.
- Case width is at least its token/header length. Row Type width is the maximum
  of its token, header length, and every spec-owned row-type label length.
  Header and body widgets use the same computed width.
- Leading grid columns no longer absorb shared expansion weight. The viewport
  content window uses `max(canvas width, content requested width)`, preventing
  a narrow canvas allocation from shrinking the table surface.
- AHRI and EN14825 BatchMatrixSpec width declarations use common tokens.
  Existing AHRI compact header/source and HSPF2 A2 contracts are unchanged.

## Verification

- `python3 -B -m pytest tests/test_ui_tk_batch_matrix_table.py tests/test_ui_tk_batch_table_viewport.py tests/test_ui_tk_ahri_seer2_batch.py tests/test_ui_tk_ahri_hspf2_batch.py tests/test_apps_calculator_ui_en14825_batch.py tests/test_ui_tk_en14825_scop_batch_dialog.py`
  — 62 passed.
- `python3 -B tools/check_code_structure.py` — passed with two pre-existing
  EN14825 soft-LOC warnings and the expected pre-regeneration map reminder.
- `python3 -B tools/code_checker/build_reference_map.py --check` — stale from
  prior commit metadata and the new viewport helper; regenerated once.
- `git diff --check` — passed before report/code-map finalization.
- `python3 -B tools/check_agent_change_gate.py --cached` — passed.

## Manual Check

Required: open AHRI HSPF2 Batch and confirm Case, Row Type, Capacity, and Power
are fully readable without increasing dialog minimum geometry. If successful,
proceed to AHRI calculator lifecycle closeout.

## Known Risks

- This remains a vertical-only viewport by contract. If a future matrix is
  wider than the available dialog after natural sizing, horizontal navigation
  requires a separate design slice rather than reintroducing compression.

## Scope Compliance

- All prohibited calculator, main UI, window-sizing, and dialog geometry files
  are unchanged.
- No UI literal exemption is used.

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
- Batch matrix table/viewport/model and layout constants: relevant sizing and
  spec ranges only; reason: common UI ownership and current behavior.
- AHRI and EN14825 batch specs: width declarations only; reason: requested
  BatchMatrixSpec migration.
- Focused matrix/viewport/AHRI/EN14825 tests: matching contract ranges only;
  reason: regression coverage.
- `docs/WORK_PLAN.md`: current-slice range; reason: next-action sync.
- broad read: none
- repeated read: none

## Next Action

AHRI HSPF2 Batch visual recheck, then AHRI calculator lifecycle closeout.
