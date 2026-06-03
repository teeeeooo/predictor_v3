# 187 ISO/ISEER 2-Point Tkinter Design Slice

## Goal

Define the no-source-change design boundary for implementing
ISO 16358-1 / India ISEER 2-point single calculation in the Tkinter
calculator after the 186 PyQt reference parity audit.

## Scope

- Reconfirm the PyQt/reference 2-point single calculation flow.
- Compare placement options in the current Tkinter ISO tab.
- Write the implementation design document for the next slice.
- Add a short WORK_PLAN checkpoint.

## Non-goals

- No Python source or test changes.
- No ISO/ISEER 2-point implementation.
- No SASO, multi/batch, detail/trace table, graph, EN/AHRI, or PyQt
  retirement work.
- No `project_log.md`, `result_reports/memory/project_memory_seed.md`,
  lifecycle summary, or archive work.

## Checked Ranges

- `ui/calculators_2point.py`
  - `IsoCspfSingleWidget.PROFILE_TWO_POINT`
  - `TWO_POINT_REGIONS`
  - `TWO_POINT_INPUTS`
  - `_load_calculators()`
  - `_build_two_point_inputs()`
  - `_recalculate_two_point()`
- `core/calculator_profiles.py`
  - `iso_t1_default_2point_cspf`
  - `india_iseer_cspf`
- `data/region_configs/iso_t1_default_2point.json`
- `data/region_configs/india_iseer.json`
- `ui_tk/tabs/iso16358_tab.py`
- `ui_tk/profile_resolver.py`
- `ui_tk/sections/iso_cspf_section.py`
- `ui_tk/sections/iso_hspf_section.py`
- `ui_tk/metric_input_table.py`
- `ui_tk/excel_like_table_controller.py`
- `ui_tk/result_panel.py`
- `result_reports/active/186_pyqt-reference-parity-audit.md`

## Design Direction

Final recommendation: **add a top-level profile/mode selector inside
`Iso16358Tab` and render ISO/ISEER 2-point as a separate section**.

Rejected alternatives:

- Extending the existing region selector: rejected because
  `ISO / ISEER 2-point` is a comparison mode, not one region.
- Adding a profile selector inside the CSPF metric tab: rejected because
  it would couple generic ISO/ISEER comparison behavior to the current
  Hong Kong CSPF section and leave the HSPF sibling tab semantically
  confusing.

The recommended shape keeps Hong Kong behavior stable:

- Hong Kong remains the default mode.
- Current Hong Kong region selector and CSPF/HSPF metric sub-tabs remain
  unchanged in Hong Kong mode.
- ISO/ISEER 2-point mode renders a new independent section.

## Next Implementation Slice

Next action: **187-b ISO/ISEER 2-point single calculation implementation**.

Candidate 187-b files:

- New `ui_tk/sections/iso_iseer_2point_section.py`
- `ui_tk/tabs/iso16358_tab.py`
- `ui_tk/profile_resolver.py` or a small UI-safe profile-mode registry
- `ui_tk/sections/result_formatting.py`
- Focused Tkinter UI tests and resolver tests

187-b should:

- Reuse `MetricInputTable`, `ExcelLikeTableController`,
  `DebouncedAutoCalc`, and `ResultPanel`.
- Use input points `35 Full` and `35 Half`, each with capacity and power.
- Call `iso_t1_default_2point_cspf` and `india_iseer_cspf` with the same
  measured input.
- Render ISO 16358-1 and India ISEER results together with EER Full,
  EER Half, CSPF/ISEER, CSTL, and CSEC.
- Keep full pytest out of scope unless a later prompt widens
  verification.

## Excluded Scope

187-b must not include:

- SASO T3.
- SASO required/minimum toggle.
- Multi/batch calculation.
- Detail panel.
- Bin trace table.
- Graph / load-capacity graph.
- EN/AHRI extension.
- PyQt retirement.
- Core calculator/profile/config/golden/fixture changes.

## Verification

- Source inspection only: `rg`, `wc -l`, and targeted `sed -n` ranges.
- `python3 -B tools/check_code_structure.py`: recorded during task
  verification.
- `git diff --check`: recorded during task verification.
- Full pytest was not run.

## Changed Files

- `docs/designs/2026-05-29-tkinter-iso-iseer-2point-single-design.md`
  - New design document with Design Gate Summary.
- `result_reports/active/187_iso-iseer-2point-tkinter-design-slice.md`
  - New active report for this no-source-change design slice.
- `docs/WORK_PLAN.md`
  - Added a short 187-a checkpoint and next recommended action.

## Known Risks

- The design recommends `ResultPanel` with two `ResultSummary` objects
  for 187-b. A literal horizontal comparison table may become a later
  visual refinement if stacked summaries are insufficient.
- Profile/mode resolver naming must avoid exposing raw `profile_id`
  values in the UI.
- `ACTIVE_DOCUMENTS.md` was read for owner context but not updated
  because this task explicitly allowed only the design doc, active
  report, and `docs/WORK_PLAN.md`.

## Scope Compliance

- Python source and tests were not modified.
- Only the allowed design doc, active report, and WORK_PLAN files were
  modified.
- `project_log.md`, `result_reports/memory/project_memory_seed.md`, and
  lifecycle summary/archive maintenance were not touched.

## Commit / Push

- Source change: none.
- Design/report/docs commit: recorded in final terminal summary.
- Push target: `origin/work/ui-ux-ssot-adoption`.

## Project Memory Delta

- none
