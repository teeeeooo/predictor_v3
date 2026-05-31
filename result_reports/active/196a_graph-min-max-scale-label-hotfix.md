# 196-a Graph Min/Max Scale Label Hotfix

## Goal

- Make the detail graph easier to interpret after input changes by showing the selected y-series min/max scale.
- Keep graph data mapping and autoscale behavior unchanged.

## Scope

- Updated `ui_tk/sections/bin_detail_panel.py` only within the Canvas graph drawing/min-max path.
- Updated focused tests in `tests/test_ui_tk_iso_table_autocalc.py`.
- Updated `docs/WORK_PLAN.md` next action and graph status.

## Non-goals

- No calculator, detail table, CSV, copy, geometry, profile/config, core, PyQt, or Hong Kong HSPF changes.
- No graph export or HTML export.
- No x-axis mapping change: x-axis remains `tj` / `Outdoor Temp [°C]`.
- No y-axis mapping change: y-axis remains the selected graph series; `Bin Hours [h]` remains backed by `nj`.
- No autoscale policy change and no fixed zero baseline.

## Changed Files

- `ui_tk/sections/bin_detail_panel.py`
  - `_plot_points()` now returns the selected y-series original `min_y/max_y` alongside points and x-scale.
  - `_draw()` displays y max near the top of the y-axis, y min near the bottom, and includes `min/max` in the selected-series label.
  - Equal-value autoscale expansion remains internal to coordinate calculation only.
- `tests/test_ui_tk_iso_table_autocalc.py`
  - Added headless coverage for selected-series y-scale return and EER min/max formatting.
  - Added Canvas text assertion coverage for graph scale labels when Tk is available.
- `docs/WORK_PLAN.md`
  - Updated current focus and next action to `196-a manual smoke`.

## Verification

- Process check: no leftover pytest/python test process beyond the check command itself.
- `python3 -B tools/check_code_structure.py`
  - Passed with existing soft-limit warning: `ui_tk/sections/bin_detail_panel.py` exceeds 400 LOC.
- `python3 -B -m py_compile ui_tk/sections/bin_detail_panel.py tests/test_ui_tk_iso_table_autocalc.py tests/test_ui_tk_calculator_foundation.py`
  - Passed.
- Quick smoke:
  - `python3 -B -m pytest tests/test_ui_tk_iso_table_autocalc.py::test_bin_detail_graph_returns_y_scale_for_selected_series tests/test_ui_tk_iso_table_autocalc.py::test_iso_iseer_detail_graph_scale_label_updates_with_selected_series tests/test_ui_tk_calculator_foundation.py::test_calculator_tk_app_builds_widget_tree -q -rxXs`
  - Result: 1 passed, 2 skipped because Tk display is unavailable in Codespaces.
- Final focused:
  - `python3 -B -m pytest tests/test_ui_tk_profile_resolver.py tests/test_ui_tk_iso_table_autocalc.py tests/test_ui_tk_calculator_foundation.py -q -rxXs`
  - Result: 31 passed, 45 skipped because Tk display is unavailable in Codespaces for GUI tests.
- `git diff --check`
  - Passed.

## Manual Check Needed

- Smartphone + Codespaces environment cannot run manual GUI smoke.
- Tk Canvas GUI assertions skip without a display; headless min/max calculation and label formatting coverage passed.
- Next action: `196-a manual smoke`.

## Known Risks

- The source file remains over the 400 LOC soft limit; no split was done because this was a small readability hotfix.
- Actual rendered label placement still needs manual GUI smoke.

## Scope Compliance

- Graph data mapping preserved.
- Autoscale policy preserved.
- Detail table/copy/CSV unchanged.
- Geometry/window code unchanged.
- No summary/archive/project log/memory lifecycle work performed.

## Commit / Push

- Source/test and docs/report commits are intended to be separated.
- Push target: `origin work/ui-ux-ssot-adoption`.

## Project Memory Delta

- none
