# 389 Calculator table bounded-width layout correction

## Goal

Keep calculator input and result tables at appropriate content width when the
window is expanded, leaving extra horizontal space blank instead of stretching
tables indefinitely.

## Scope

- Changed `MetricInputTable` default `layout_policy` to `content_hug`.
- Kept `responsive` as an explicit supported option.
- Updated ISO, Hong Kong, and EN14825 calculator input table placements to
  left-aligned content-width placement.
- Updated compact result surfaces:
  - `ResultPanel` summary tables,
  - ISO/ISEER 2-point result table,
  - SASO T3 result table,
  - bin trace result table,
  - EN14825 SCOP per-climate result surface.
- Updated focused tests to verify content-width default behavior, retained
  responsive behavior, and resize-invariant ISO/HK table widths.

## Non-Goals

- No core/data/calculation logic changes.
- No EN14825 adapter/model/table model responsibility changes.
- No `MetricInputTable` controller, copy/paste, undo, or selection changes.
- No new layout framework.

## Cause

The prior fix introduced `content_hug` only for small EN14825 form tables.
Main matrices and result tables still used a combination of `sticky="ew"`,
`fill=tk.X`, nonzero column weights, and Treeview column `stretch=True`, so
visible table surfaces expanded with the parent.

## Result

Calculator table surfaces now use content-width behavior by default. Remaining
container-level responsive behavior can still make surrounding frames or tabs
grow, but visible input/result table surfaces keep their requested width and
left alignment.

## Validation

- `python3 -B -m py_compile apps/calculator/ui/metric_input_table.py`
- `python3 -B -m pytest tests/test_ui_tk_metric_input_table_adapter.py -q`
- `python3 -B -m pytest tests/test_ui_tk_iso_table_autocalc.py -q`
- `python3 -B -m pytest tests/test_apps_calculator_ui_en14825.py -q`
- `python3 -B -m pytest tests/test_apps_calculator_ui_en14825_scop.py -q`
- Additional focused result-surface check:
  `python3 -B -m pytest tests/test_ui_tk_result_panel_stable_update.py tests/test_ui_tk_bin_detail_schema.py -q`

Full final validation is recorded in the terminal closeout.

## Next

Run target desktop manual smoke for ISO/HK/EN14825 table and result surface
width behavior after window expansion.
