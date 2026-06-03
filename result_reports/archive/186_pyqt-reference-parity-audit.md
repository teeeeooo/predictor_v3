# 186 PyQt Reference Parity Audit

## Goal

Audit the ISO16358 calculator features that still exist in the
PyQt/reference calculator path and compare them with the current
Tkinter calculator implementation before choosing the next Tkinter
feature slice.

## Scope

- Read-only parity audit.
- Identify PyQt/reference ISO16358 feature owners.
- Identify current Tkinter calculator coverage.
- Classify parity gaps and next candidate slices.

## Non-goals

- No Python source or test changes.
- No implementation of ISO/ISEER 2-point, SASO, multi calculation,
  detail/trace/graph, EN/AHRI expansion, or PyQt retirement.
- No `project_log.md`, `result_reports/memory/project_memory_seed.md`,
  lifecycle summary, or archive work.

## Context

Recent source cleanup completed the Tkinter shell geometry and scroll
foundation:

- 184: portable window geometry rule documentation.
- 185-b: `ui_tk/window_geometry.py` extraction.
- 185-c: `ui_tk/scrollable_frame.py` extraction.
- 185-d: `ScrollableFrame` wheel binding cleanup.
- 185-e: shell geometry/scroll cleanup report catch-up.
- User follow-up commit `e7cdff2` corrected the 185 report commit hash.

The next target is not EN/AHRI expansion. The next target is checking
which existing PyQt/app_calculator ISO16358 reference features have not
yet been migrated to Tkinter.

## Checked Files And Ranges

PyQt/reference:

- `app_calculator.py`: entrypoint only.
- `ui/calc_window.py`: `init_ui()`, `init_iso_tab()`, profile loading,
  and ISO no-op calculate path.
- `ui/calculators_2point.py`: `TwoPointTableModel`,
  `TwoPointTableView`, `TraceTableModel`, `BinGraphWidget`,
  `TraceDetailPanel`, `ProfileInputGridModel`,
  `ProfileInputGridDelegate`, `ProfileInputGridView`,
  `RegionResultTableModel`, `RegionDetailTab`,
  `BatchTwoPointDialog`, and `IsoCspfSingleWidget`.
- `core/calculator_profiles.py`: ISO profile registry entries.
- `data/region_configs/iso_t1_default_2point.json`,
  `data/region_configs/india_iseer.json`,
  `data/region_configs/hong_kong.json`,
  `data/region_configs/saso.json`: profile/config evidence only.
- `tests/test_iso16358_table_excel_like_behavior.py`: PyQt table
  behavior contract evidence.

Tkinter:

- `app_calculator_tk.py`
- `ui_tk/calculator_app.py`
- `ui_tk/profile_resolver.py`
- `ui_tk/tabs/iso16358_tab.py`
- `ui_tk/sections/iso_cspf_section.py`
- `ui_tk/sections/iso_hspf_section.py`
- `ui_tk/metric_input_table.py`
- `ui_tk/excel_like_table_controller.py`
- `ui_tk/result_panel.py`
- `ui_tk/window_geometry.py`
- `ui_tk/scrollable_frame.py`
- `tests/test_ui_tk_calculator_foundation.py`
- `tests/test_ui_tk_iso_table_autocalc.py`
- `tests/test_ui_tk_excel_like_table_controller.py`
- `tests/test_ui_tk_profile_resolver.py`

## PyQt / Reference Feature Inventory

| Feature | PyQt/reference status | Owner / evidence |
| --- | --- | --- |
| App shell | Present. `app_calculator.py` starts `CalculatorWindow`; `CalculatorWindow.init_iso_tab()` mounts `IsoCspfSingleWidget`. | `app_calculator.py`, `ui/calc_window.py:init_iso_tab()` |
| ISO / ISEER 2-point single calculation | Present. Profile selector option `ISO / ISEER 2점식`; two measured points `35 Full`, `35 Half`; calculates ISO 16358-1 and India ISEER side by side. | `IsoCspfSingleWidget.PROFILE_TWO_POINT`, `TWO_POINT_REGIONS`, `_build_two_point_inputs()`, `_recalculate_two_point()` |
| Hong Kong CSPF | Present. Profile selector option `Hong Kong CSPF`; declared/rated capacity field plus 35 Full/Half measured inputs. | `PROFILE_HONG_KONG`, `_build_hong_kong_inputs()`, `_recalculate_hong_kong()` |
| SASO T3 | Present. Profile selector option `SASO T3`; measured 46 Full, 35 Full, 35 Half, and optional 35 Min. | `PROFILE_SASO_T3`, `SASO_INPUTS_REQUIRED`, `SASO_INPUTS_WITH_MIN`, `_build_saso_inputs()`, `_recalculate_saso()` |
| SASO required/minimum input difference | Present. Checkbox toggles required-only vs optional minimum input. When minimum is not used, `_saso_calculator(False)` overrides config `cspf_test_profile.test_selection` to `required_only`; default config is `with_optional_test`. | `_on_saso_min_toggled()`, `_saso_calculator()`, `data/region_configs/saso.json` |
| Multi input / batch dialog | Present for ISO/ISEER 2-point only. Batch dialog uses `TwoPointTableModel` with row add/delete and paste-driven automatic calculation. Disabled for Hong Kong and SASO. | `BatchTwoPointDialog`, `TwoPointTableModel`, `_open_batch_dialog()`, `_apply_profile()` |
| Result summary table | Present. Single-profile and multi-region results render into `RegionResultTableModel` / `ReadOnlyCopyTableView`. | `RegionResultTableModel`, `IsoCspfSingleWidget._recalculate_*()` |
| Detail tab | Present. Toggleable detail panel builds per-profile `RegionDetailTab` instances. Legacy `TraceDetailPanel` also exists for the two-point table model path. | `RegionDetailTab`, `_build_detail_tabs()`, `_toggle_detail()`, `TraceDetailPanel` |
| Bin trace table | Present. `TraceTableModel` exposes bin number, temperature, hours, load, capacity, power, EER, CSTL, and CSEC. | `TraceTableModel`, `RegionDetailTab.table_model` |
| Graph / load-capacity graph | Present. `BinGraphWidget` draws `bin_hours` and `load_capacity` modes; `RegionDetailTab` exposes a graph selector. | `BinGraphWidget`, `RegionDetailTab.graph_combo` |
| Profile selector | Present. `IsoCspfSingleWidget.combo_profile` switches ISO/ISEER 2-point, Hong Kong CSPF, and SASO T3. Core registry also has `iso_t1_default_2point_cspf`, `india_iseer_cspf`, `hong_kong_cspf`, `hong_kong_hspf`, and `saso_t3_cspf`. | `IsoCspfSingleWidget._init_ui()`, `core/calculator_profiles.py` |
| Copy/paste/undo/navigation table behavior | Present for profile input grids. `ProfileInputGridView` handles Ctrl/Cmd+C, paste, undo, Delete/Backspace, Enter/Tab navigation; delegate handles commit-and-navigate. `TwoPointTableView` supports copy/paste for batch table. | `ProfileInputGridModel`, `ProfileInputGridDelegate`, `ProfileInputGridView`, `TwoPointTableView`, `tests/test_iso16358_table_excel_like_behavior.py` |

## Tkinter Feature Inventory

| Feature | Tkinter status | Owner / evidence |
| --- | --- | --- |
| App shell | Present. Thin Tkinter entrypoint builds `CalculatorTkApp`; shell owns root, notebook, one ISO tab, initial centering, and one-shot overflow correction. | `app_calculator_tk.py`, `ui_tk/calculator_app.py` |
| Region selector | Present but Hong Kong-only. Resolver maps only `Hong Kong` to `hong_kong`. | `ui_tk/profile_resolver.py`, `Iso16358Tab._region_combo` |
| Metric sub-tabs | Present for current Hong Kong region. Region rendering builds `CSPF` and `HSPF` tabs from supported metric sections. | `Iso16358Tab._metric_notebook`, `_SECTION_FACTORIES`, `_render_region()` |
| Hong Kong CSPF input/calculation | Present. Rated/declared capacity plus 35 Full/Half measured input; auto-calculates with `hong_kong_cspf`. | `IsoCspfSection`, `build_cspf_input()`, `resolve_profile_id(..., "CSPF")` |
| Hong Kong HSPF input/calculation | Present. Rated heating capacity plus 7 Full/Half measured input; auto-calculates with `hong_kong_hspf`. | `IsoHspfSection`, `build_hspf_input()`, `resolve_profile_id(..., "HSPF")` |
| Default result immediate render | Present. Sections seed default values and call `_auto_calc.flush_now()` on construction; tests assert default CSPF/HSPF summaries are rendered and section-local. | `IsoCspfSection.__init__()`, `IsoHspfSection.__init__()`, `tests/test_ui_tk_iso_table_autocalc.py` |
| Excel-like table behavior | Present for `MetricInputTable`. Controller supports selection/edit modes, copy, paste, Delete/Backspace clear, undo, type-to-replace, F2/double-click edit, arrows, Tab/Enter navigation, and atomic invalid-paste rejection. | `MetricInputTable`, `ExcelLikeTableController`, `tests/test_ui_tk_excel_like_table_controller.py` |
| Result summary panel | Present as compact metric-local summary tables and retained copy text compatibility. No PyQt-style region comparison table. | `ResultPanel`, `summarize_cspf_result()`, `summarize_hspf_result()` |
| Window geometry / scroll container | Present. Geometry helpers are separate, and `ScrollableFrame` owns canvas/scrollbar/content/mousewheel behavior. | `ui_tk/window_geometry.py`, `ui_tk/scrollable_frame.py`, foundation tests |
| ISO / ISEER 2-point single calculation | Missing from Tkinter UI. Core profiles exist, but Tkinter resolver does not expose ISO T1 or India ISEER. | `ui_tk/profile_resolver.py` only maps Hong Kong CSPF/HSPF |
| SASO T3 | Missing from Tkinter UI. Core profile/config exist, but no Tkinter region/profile section exposes SASO. | `core/calculator_profiles.py`, `data/region_configs/saso.json`, no `ui_tk` mapping |
| Multi input / batch dialog | Missing. No Tkinter batch dialog or multi-row ISO/ISEER input surface. | no `ui_tk` owner found |
| Detail tab / bin trace table / graph | Missing. Tkinter result panels render summaries only; no bin detail table or graph surface. | no `ui_tk` owner found |

## Parity Gap Table

| Feature | PyQt/reference status | Tkinter status | Gap | Suggested next slice | Risk / notes |
| --- | --- | --- | --- | --- | --- |
| App shell and ISO tab mounting | Present | Present | Already covered | None | Tk shell is intentionally narrower and PyQt-free. |
| Hong Kong CSPF | Present | Present | Already covered | None | Tk version uses metric-local summary panel and auto-calc instead of PyQt profile result table. |
| Hong Kong HSPF | Not a PyQt ISO UI parity target found in `IsoCspfSingleWidget`; core profile exists | Present | Already covered, extra Tk coverage | None | Keep separate from CSPF parity; do not let HSPF hide missing CSPF reference features. |
| Region/profile selector breadth | PyQt profile selector exposes ISO/ISEER, Hong Kong CSPF, SASO T3 | Tk selector exposes only Hong Kong and metric sub-tabs | Partially covered | ISO profile navigation design inside Tk ISO tab | Avoid exposing raw `profile_id`; decide whether region selector or profile/standard segmented navigation owns this. |
| ISO / ISEER 2-point single calculation | Present | Missing | Missing | First priority: ISO/ISEER 2-point single calculation slice | This is the highest parity gap. Build separately from Hong Kong-specific CSPF/HSPF sections. |
| SASO T3 single calculation | Present | Missing | Missing | SASO T3 single calculation after generic 2-point input shape exists | Needs required-only vs optional minimum design; do not fold into Hong Kong section. |
| SASO required/minimum toggle | Present | Missing | Missing / Needs design decision | SASO-specific option slice | Requires preserving `required_only` vs `with_optional_test` behavior without mutating shared config globally. |
| Multi / batch calculation | Present for ISO/ISEER 2-point only | Missing | Missing | Batch/multi slice after single 2-point path is stable | Different interaction surface and validation risk from single calculation; keep separate. |
| Result summary table | Region result table in PyQt | Metric-local summary tables in Tk | Partially covered | Decide per-feature result surface during 2-point slice | Tk summary is good for Hong Kong sections, but ISO/ISEER side-by-side comparison needs a distinct table or summary surface. |
| Detail tab | Present | Missing | Missing | Detail/trace/graph audit/design slice after single result object is available | Avoid implementing graph before data ownership and lightweight rendering choice are settled. |
| Bin trace table | Present | Missing | Missing | Detail/trace table slice | Read-only copy behavior can reuse table contract, but result schema and bin detail availability must be explicit. |
| Graph / load-capacity graph | Present | Missing | Needs design decision | Lightweight Canvas graph design slice | Do not introduce `matplotlib`; current PyQt graph is custom-painted and can be translated later if needed. |
| Input table copy/paste/undo/navigation | Present | Present for current metric tables | Partially covered | Reuse/extend `MetricInputTable` or define generic input grid for 2-point/SASO | Existing Tk controller is strong, but new dynamic point sets need an owner API. |
| Window geometry / scroll behavior | Present by PyQt default layout | Present in Tk | Already covered | None | Recent cleanup addressed this foundation. |
| Hong Kong skeleton risk | PyQt reference was profile-driven and multi-feature | Tk ISO tab is currently Hong Kong-driven | Needs design decision | Do 2-point as a separate generic ISO profile slice, not as ad hoc code inside Hong Kong sections | Main audit finding: the current Tk ISO surface can look complete while still missing PyQt ISO reference features. |

## Priority Judgment

Recommended next direction: **start with ISO/ISEER 2-point as a
separate design/implementation slice**.

Reasoning:

- It is the broadest missing PyQt/reference capability and the owner of
  the ISO T1 and India ISEER profile path.
- It establishes the generic 2-point input/result shape needed before
  SASO T3 and multi/batch are practical.
- It prevents the current Hong Kong CSPF/HSPF skeleton from becoming
  the only shape of the Tkinter ISO tab.

## Next Candidate Slices

1. **ISO/ISEER 2-point single calculation slice**: define the Tkinter
   navigation and generic 2-point input/result surface, then wire ISO
   T1 default CSPF and India ISEER.
2. **SASO T3 single calculation slice**: add SASO-specific 46 Full /
   35 Full / 35 Half and optional 35 Min handling after the generic
   profile section shape is clear.
3. **Detail / bin trace / graph design slice**: decide a lightweight
   Tkinter table + Canvas surface for bin trace and load-vs-capacity
   graph after single calculation result ownership is stable.
4. **ISO/ISEER multi/batch slice**: port the PyQt batch concept only
   after the single 2-point path and validation surface are stable.

## Do Not Do Now

- Do not pivot to EN/AHRI expansion before ISO16358 parity gaps are
  addressed or explicitly deferred.
- Do not implement ISO/ISEER 2-point, SASO, multi, detail/trace/graph,
  or graph rendering in this audit.
- Do not modify core/profile/config/golden/fixture/schema files.
- Do not start PyQt calculator source retirement from this audit.
- Do not perform lifecycle summary/archive maintenance.

## Verification

- Read-only audit used `rg`, `wc -l`, and targeted `sed -n` ranges only.
- `python3 -B tools/check_code_structure.py`: recorded during task
  verification.
- `git diff --check`: recorded during task verification.
- Full pytest was not run.

## Changed Files

- `result_reports/active/186_pyqt-reference-parity-audit.md`
  - New active no-source-change parity audit report.
- `docs/WORK_PLAN.md`
  - Added a short 186 checkpoint and next recommended action.

## Known Risks

- This is a source inspection audit, not runtime validation.
- Some PyQt calculator code is retained as reference while calculator-only
  PyQt retirement remains deferred; this audit does not change that
  retention decision.
- The audit intentionally does not decide the final Tkinter IA for
  profile navigation; it only identifies that the current Hong Kong-only
  resolver is insufficient for parity.

## Commit / Push

- Source change: none.
- Audit base includes latest user correction commit `e7cdff2`.
- Report/docs commit: recorded in final terminal summary.
- Push target: `origin/work/ui-ux-ssot-adoption`.

## Project Memory Delta

- none
