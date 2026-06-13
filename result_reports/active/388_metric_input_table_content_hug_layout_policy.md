# 388 MetricInputTable content-hug layout policy

## Goal

Stop small `MetricInputTable` form tables from stretching to the full parent
width when the window grows, without changing table controller behavior or
calculation logic.

## Scope

- Added `layout_policy` to `MetricInputTable`.
  - `responsive` remains the default and preserves existing table/frame
    weights and `sticky="ew"`.
  - `content_hug` uses zero outer/table column weights and left-aligned table
    frame placement.
- Applied `content_hug` to EN14825 small/form tables:
  - common Pto/Psb/Pck/Poff input tables,
  - SEER design specs table,
  - SCOP Cd table,
  - SCOP per-climate auxiliary input tables.
- Kept SEER and SCOP main condition matrix tables on the default responsive
  policy.
- Changed SEER/SCOP appliance selector labels to `Type`.

## Non-Goals

- No core/data/calculation changes.
- No EN14825 adapter/model/table model changes.
- No copy/paste/selection/undo/controller behavior changes.
- No large main matrix table was converted to content-hug.

## Table Parity Evidence

- Reused existing `MetricInputTable` and `TkTableController`; no new helper,
  controller, or table adapter was introduced.
- Controller-facing cell metadata, editable widgets, values, row/column
  addressing, and callbacks remain unchanged.
- Focused tests cover default responsive behavior, `content_hug` weight/sticky
  behavior, and EN14825 small-table vs main-matrix policy separation.
- ISO/HK scan found no separate small auxiliary/form `MetricInputTable` owner
  requiring conversion; existing ISO/HK main matrices remain responsive.

## Validation

- `python3 -B -m py_compile apps/calculator/ui/metric_input_table.py`
- `python3 -B -m pytest tests/test_ui_tk_metric_input_table_adapter.py -q`
- `python3 -B -m pytest tests/test_apps_calculator_ui_en14825.py -q`
- `python3 -B -m pytest tests/test_apps_calculator_ui_en14825_scop.py -q`
- `python3 -B -m pytest tests/test_ui_tk_iso_table_autocalc.py -q`

Full final validation is recorded in the terminal closeout for this slice.

## Result

Small EN14825 input tables now hug their requested content width and remain
left-aligned inside their sections. Main condition matrices keep the previous
responsive behavior.

## Next

Run target desktop manual smoke for EN14825 common/design/auxiliary table
width, selector label text, and main matrix responsiveness.
