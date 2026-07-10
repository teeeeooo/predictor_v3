# 441 Compact AHRI Batch Labels and Token Widths

## Goal

Compact the AHRI SEER2/HSPF2 batch display contract and route touched batch
column widths through the UI layout token owner.

## Scope

- Remove temperature text from SEER2/HSPF2 batch point headers only.
- Format HSPF2 batch source results as `meas.`, `calc.`, and `n/a`.
- Replace AHRI batch point/result width literals with meaning-based tokens.
- Update focused batch contract tests and the near-term work plan.

## Non-goals

- No core/config/schema/fixture/golden, main UI, source mapping, A2 contract,
  window-sizing, EN14825/ISO, or unrelated refactor change.

## Changed Files

- `apps/calculator/ui/ahri/seer2_batch.py`
- `apps/calculator/ui/ahri/hspf2_batch.py`
- `apps/calculator/ui/layout_constants.py`
- `tests/test_ui_tk_ahri_seer2_batch.py`
- `tests/test_ui_tk_ahri_hspf2_batch.py`
- `docs/WORK_PLAN.md`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `result_reports/active/441_compact-ahri-batch-labels-and-token-widths.md`

## Task Results

- SEER2 and HSPF2 batch headers now use point names without temperatures.
  Main UI temperature labels remain unchanged.
- HSPF2 batch formatting converts the stable full source labels to `meas.`,
  `calc.`, and `n/a` at the batch handler boundary. The adapter/main UI full
  label contract remains unchanged.
- AHRI batch point, primary result, and source result widths now reference
  semantic constants in `layout_constants.py`; touched batch specs contain no
  raw width values.
- Focused tests cover compact headers, compact source output, token-backed
  widths, and the unchanged main adapter full-label contract.

## Verification

- `python3 -B -m pytest tests/test_ui_tk_ahri_seer2_batch.py tests/test_ui_tk_ahri_hspf2_batch.py tests/test_apps_calculator_ui_ahri_hspf2.py`
  — 23 passed.
- `python3 -B tools/check_code_structure.py` — passed with two pre-existing
  EN14825 soft-LOC warnings and the expected pre-regeneration map reminder.
- `python3 -B tools/code_checker/build_reference_map.py --check` — stale from
  the prior commit and new top-level symbols; the map was regenerated once.
- `git diff --check` — passed before report/code-map finalization.
- `python3 -B tools/check_agent_change_gate.py --cached` — passed.

## Known Risks

- Compact source labels are deliberately batch-only. Any future source value
  must first join the adapter's stable full-label contract and then receive an
  explicit batch formatter entry.

## Scope Compliance

- All prohibited calculator, layout, and framework surfaces are unchanged.
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
- AHRI SEER2/HSPF2 batch spec/handler files: label, width, and source-result
  ranges only; reason: exact production owners.
- `apps/calculator/ui/layout_constants.py`: token definitions only; reason:
  required width owner.
- AHRI SEER2/HSPF2 batch focused tests and HSPF2 adapter tests: matching
  contract ranges only; reason: focused regression coverage.
- `docs/WORK_PLAN.md`: current-slice range; reason: next-action sync.
- broad read: none
- repeated read: none

## Next Action

AHRI calculator lifecycle closeout.
