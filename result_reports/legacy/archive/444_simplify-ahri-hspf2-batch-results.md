# 444 Simplify AHRI HSPF2 Batch Results

## Goal

Reduce the AHRI HSPF2 Batch result surface to the primary HSPF2 value while
preserving optional inputs, adapter source mapping, main UI display, and dialog
natural-size fitting.

## Scope

- Keep only the `HSPF2` result metric in the HSPF2 batch matrix.
- Return only `hspf2` from successful and blank batch handler results.
- Remove the now-unused batch-only compact source formatter.
- Update focused batch and natural-sizing regression expectations.

## Non-goals

- No adapter/core source mapping, main UI, optional point, session/rebuild, A2,
  SEER2, EN14825/ISO, width token, min-size, shell/viewport, or geometry change.

## Changed Files

- `apps/calculator/ui/ahri/hspf2_batch.py`
- `tests/test_ui_tk_ahri_hspf2_batch.py`
- `docs/WORK_PLAN.md`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `result_reports/active/444_simplify-ahri-hspf2-batch-results.md`

## Task Results

- `BatchMatrixSpec.result_metrics` now contains only
  `("hspf2", "HSPF2", BATCH_MATRIX_RESULT_PRIMARY_WIDTH_CHARS)`.
- Successful handler results are `{"hspf2": "..."}` and pending/error results
  are `{"hspf2": ""}`. Adapter calculation and options construction are
  unchanged; source summary fields are intentionally ignored by batch output.
- The obsolete batch source compaction mapping/helper and source-width import
  were removed. Main adapter source normalization and main UI full labels were
  not changed.
- Focused tests retain optional H42/H12/H22, superset snapshot/rebuild, A2
  capacity-only, header/export, and natural initial-size coverage.

## Verification

- `python3 -B -m pytest tests/test_ui_tk_ahri_hspf2_batch.py tests/test_ui_tk_batch_dialog_content_sizing.py`
  — 12 passed.
- `python3 -B tools/check_code_structure.py` — passed with two pre-existing
  EN14825 soft-LOC warnings and the expected pre-regeneration map reminder.
- `python3 -B tools/code_checker/build_reference_map.py --check` — stale from
  prior commit metadata and removed batch formatter; regenerated once.
- `git diff --check` — passed before final staging.
- `python3 -B tools/check_agent_change_gate.py --cached` — passed.

## Known Risks

- Source metadata remains available from the adapter/main UI but is no longer
  visible in batch exports by design.

## Scope Compliance

- All prohibited calculation, main UI, session, sizing, and cross-profile
  surfaces are unchanged.
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
- `apps/calculator/ui/ahri/hspf2_batch.py`: result spec, formatter, handler, and
  blank-result ranges only; reason: exact production owner.
- HSPF2 batch and batch dialog content-sizing focused tests: result/header and
  sizing ranges only; reason: requested regression coverage.
- HSPF2 main adapter tests: source-contract references located only; reason:
  confirm unchanged full-label owner without modifying it.
- `docs/WORK_PLAN.md`: current-slice range; reason: next-action sync.
- broad read: none
- repeated read: none

## Next Action

AHRI HSPF2 Batch visual recheck, then AHRI calculator lifecycle closeout.
