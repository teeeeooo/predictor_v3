# 189-b ISO/ISEER 2-point Result Visual Refinement

Date: 2026-05-29

## Goal

Implement the 189-a Candidate B design: improve only the Tkinter `ISO / ISEER 2-point` result display with a section-local read-only comparison table.

## Scope

Changed:

- `ui_tk/sections/iso_iseer_2point_section.py`
- `ui_tk/sections/iso_iseer_2point_result_table.py`
- `tests/test_ui_tk_iso_table_autocalc.py`
- `docs/WORK_PLAN.md`
- `result_reports/active/189b_iso-iseer-2point-result-visual-refinement.md`

Read-only references:

- `docs/designs/2026-05-29-tkinter-iso-iseer-2point-result-visual-refinement.md`
- Relevant `AGENT_TASK_ROUTER.md` sections
- Relevant table UX/Tkinter adapter excerpts

## Non-goals

- No `ResultPanel` implementation changes.
- No `ui_tk/result_models.py`, `ui_tk/profile_resolver.py`, `ui_tk/tabs/iso16358_tab.py`, scroll, geometry, core calculator, profile/config, golden/fixture, PyQt source, SASO, multi/batch, detail/trace, graph, EN/AHRI, `project_log.md`, memory seed, summary, or archive changes.

## Implementation

- Added `IsoIseer2PointResultTable`, a section-local read-only `ttk.Treeview` surface for 2-point primary results.
- Rendered success results as rows:
  - `ISO 16358-1`
  - `India ISEER`
- Rendered columns:
  - `Region/Profile`
  - `EER Full`
  - `EER Half`
  - `CSPF/ISEER`
  - `CSTL [kWh]`
  - `CSEC [kWh]`
- Kept existing numeric formatting helpers for EER, metric, CSTL, and CSEC display.
- Added TSV-style section-local text export/copy compatibility through the new result surface.
- Kept `IsoIseer2PointSection.result_panel` as a compatibility alias to the new read-only result surface so `Iso16358Tab` and app smoke do not need changes.
- Invalid input now clears the comparison rows and displays a safe status message, avoiding stale success values.

## Tests

Updated focused Tkinter tests to cover:

- 2-point comparison table columns and rows.
- Input edit recalculation updating both profile rows without append growth.
- Invalid input status with no stale rows and successful recovery after valid input.
- Existing Hong Kong CSPF/HSPF `ResultPanel` summary behavior unchanged.
- Full app subprocess widget tree smoke unchanged.

## Verification

Commands run:

- `ps -axo pid,args | rg 'pytest|python3 -B -m pytest|Python -B'` -> no leftover pytest process after verification
- `python3 -B tools/check_code_structure.py` -> OK (`code structure guard: OK (no findings)`)
- `python3 -B -m py_compile ui_tk/sections/iso_iseer_2point_section.py ui_tk/sections/iso_iseer_2point_result_table.py tests/test_ui_tk_iso_table_autocalc.py tests/test_ui_tk_calculator_foundation.py` -> OK
- `python3 -B -m pytest tests/test_ui_tk_iso_table_autocalc.py::test_iso_iseer_2point_mode_renders_default_summaries tests/test_ui_tk_calculator_foundation.py::test_calculator_tk_app_builds_widget_tree -q -rxXs` -> 2 passed
- `python3 -B -m pytest tests/test_ui_tk_profile_resolver.py tests/test_ui_tk_iso_table_autocalc.py tests/test_ui_tk_calculator_foundation.py -q -rxXs` -> 42 passed
- `git diff --check` -> OK
- `git status --short`, `git diff --name-only`, `git diff --stat` -> reviewed before commits

Full pytest was intentionally not run.

## Manual Check Needed

- Manual UI smoke should confirm that the 2-point comparison table is visually readable at normal app size.
- Manual UI smoke should confirm Ctrl/Cmd+C from the result table copies readable TSV text if focus is on the table.

## Excluded Scope

- SASO
- multi/batch
- detail/trace table
- graph
- core calculator
- golden/fixture
- PyQt retirement
- window geometry / scroll
- Hong Kong CSPF/HSPF result redesign

## Next Suggested Action

Run manual smoke, then choose the next Design First Gate slice. Do not treat SASO, multi/batch, detail/trace, or graph as implemented by this work.

## Scope Compliance

- `ResultPanel`, result model, profile resolver, ISO tab shell, scroll, geometry, core, configs, fixtures, PyQt source, `project_log.md`, and memory seed were not modified.
- The comparison surface is local to the ISO/ISEER 2-point section.

## Commit / Push

- Source/test commit: `e5cc77b feat: refine iso iseer 2point result table`
- Docs/report commit: pending at report write time
- Push: pending at report write time

## Project Memory Delta

- none
