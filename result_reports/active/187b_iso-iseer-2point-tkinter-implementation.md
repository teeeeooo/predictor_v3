# 187-b ISO/ISEER 2-point Tkinter Implementation

## Goal

Implement the focused Tkinter ISO/ISEER 2-point single calculation slice from `docs/designs/2026-05-29-tkinter-iso-iseer-2point-single-design.md`.

## Scope

- Add a top-level ISO tab calculation mode selector with `Hong Kong` and `ISO / ISEER 2-point`.
- Keep Hong Kong as the default mode with the existing region selector and CSPF/HSPF metric sub-tabs.
- Add a separate `IsoIseer2PointSection` for ISO 16358-1 and India ISEER 2-point single calculations.
- Reuse `MetricInputTable`, `ExcelLikeTableController`, `DebouncedAutoCalc`, and `ResultPanel`.
- Add focused resolver, ISO tab, 2-point auto-calc, invalid-input, mode-switch, and app-shell hang regression coverage.

## Non-goals

- No SASO T3 implementation.
- No multi/batch calculation.
- No detail/trace table.
- No graph surface.
- No EN/AHRI extension.
- No core calculator, profile registry, region config, golden, fixture, PyQt source, `ResultPanel`, `AutoCalc`, or `ScrollableFrame` changes.

## Changed Files

- `ui_tk/profile_resolver.py`
- `ui_tk/tabs/iso16358_tab.py`
- `ui_tk/sections/iso_iseer_2point_section.py`
- `tests/test_ui_tk_profile_resolver.py`
- `tests/test_ui_tk_iso_table_autocalc.py`
- `tests/test_ui_tk_calculator_foundation.py`
- `docs/WORK_PLAN.md`
- `result_reports/active/187b_iso-iseer-2point-tkinter-implementation.md`

## Implementation

- `profile_resolver.py` now owns UI-safe mode/profile labels and resolves:
  - `ISO 16358-1` -> `iso_t1_default_2point_cspf`
  - `India ISEER` -> `india_iseer_cspf`
- `Iso16358Tab` now renders a top-level `계산 모드` selector:
  - `Hong Kong` mode keeps the existing region selector and CSPF/HSPF metric tabs.
  - `ISO / ISEER 2-point` mode renders only the new 2-point section.
- `IsoIseer2PointSection` renders a 35 Full / 35 Half capacity-power matrix with default sample values, attaches Excel-like behavior, auto-calculates both profiles, and renders two stacked `ResultSummary` tables in the existing `ResultPanel`.
- Invalid numeric input renders a status-only summary without traceback, raw dict, or long diagnostic output.

## Hang Stabilization

The earlier combined focused pytest hang was traced to macOS Tk/Python same-process multi-root lifecycle behavior when a full `CalculatorTkApp` root was created after prior Tk roots in the same pytest process.

The following discarded workarounds were removed and are not part of the implementation:

- `_ResultTitle(str)` / `lower()` override in the 2-point section.
- Direct `root.winfo_children()` destruction in the ISO table fixture.
- Test-hang-specific `destroy()` lifecycle additions in `Iso16358Tab` / `IsoIseer2PointSection`.

The app-shell smoke test is now isolated in a subprocess so the production source does not carry a test-only Tk lifecycle workaround.

## Verification

- `ps -axo pid,args | rg 'pytest|python3 -B -m pytest|Python -B'` — no leftover pytest/python process.
- `rg "_ResultTitle|def lower|root\\.winfo_children\\(|bind_all|unbind_all" ui_tk tests` — no matches.
- `python3 -B tools/check_code_structure.py` — passed.
- `python3 -B -m py_compile ui_tk/tabs/iso16358_tab.py ui_tk/profile_resolver.py ui_tk/sections/iso_iseer_2point_section.py tests/test_ui_tk_profile_resolver.py tests/test_ui_tk_iso_table_autocalc.py tests/test_ui_tk_calculator_foundation.py` — passed.
- `python3 -B -m pytest tests/test_ui_tk_iso_table_autocalc.py::test_iso_iseer_2point_mode_renders_default_summaries tests/test_ui_tk_calculator_foundation.py::test_calculator_tk_app_builds_widget_tree -q -rxXs` — `2 passed`.
- `python3 -B -m pytest tests/test_ui_tk_profile_resolver.py tests/test_ui_tk_iso_table_autocalc.py tests/test_ui_tk_calculator_foundation.py -q -rxXs` — `43 passed`.
- `git diff --check` — clean.

Full pytest was not run by request.

## Manual Check Needed

- Launch the Tkinter calculator and confirm mode switching between `Hong Kong` and `ISO / ISEER 2-point`.
- Confirm the 2-point input matrix, summary labels, auto-calc refresh, and invalid-input status surface visually.
- Confirm Hong Kong CSPF/HSPF table edit/copy/paste/undo/navigation still behave as expected after returning from 2-point mode.

## Next Action

Run manual smoke, then decide whether a 187-c visual/result refinement slice is needed. SASO, multi/batch, detail/trace, graph, and EN/AHRI remain deferred.

## Commit / Push

- source/test commit: `4cdd3115b77493aa026f705ebae24fc36a89a935`
- report/WORK_PLAN commit: pending
- push: pending

## Project Memory Delta

- none
