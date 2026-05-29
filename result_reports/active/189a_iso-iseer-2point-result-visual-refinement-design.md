# 189-a ISO/ISEER 2-point Result Visual Refinement Design

Date: 2026-05-29

## Goal

Audit the existing PyQt/reference and Tkinter 2-point result displays, compare refinement candidates, and define a small 189-b implementation slice.

## Scope

Checked:

- `ui/calculators_2point.py`
- `ui_tk/sections/iso_iseer_2point_section.py`
- `ui_tk/result_panel.py`
- `ui_tk/result_models.py`
- `ui_tk/sections/result_formatting.py`
- `tests/test_ui_tk_iso_table_autocalc.py`
- `tests/test_ui_tk_profile_resolver.py`
- `docs/WORK_PLAN.md` related checkpoint section

Changed:

- `docs/designs/2026-05-29-tkinter-iso-iseer-2point-result-visual-refinement.md`
- `docs/WORK_PLAN.md`
- `result_reports/active/189a_iso-iseer-2point-result-visual-refinement-design.md`

## Non-goals

- No Python source changes.
- No test changes.
- No core calculator, fixture, golden, PyQt source, `ResultPanel`, SASO, multi/batch, detail/trace, graph, scroll, or geometry changes.
- No `project_log.md`, `result_reports/memory/project_memory_seed.md`, summary, or archive changes.

## Task Results

### Task 1: PyQt/reference audit

Result: OK.

PyQt reference summary:

- `TwoPointTableModel` includes result columns for `EER Full`, `EER Half`, `ISO CSPF`, `India ISEER`, and `India CSEC [kWh]`.
- `IsoCspfSingleWidget._recalculate_two_point()` uses a comparison table with rows `ISO 16358-1` and `India ISEER`, and columns `Region/Profile`, `EER-Full`, `EER-Half`, `CSPF/SEER`, `CSTL [kWh]`, `CSEC [kWh]`.
- `RegionDetailTab` separately owns detail summary, graph selector/graph, and trace table. Primary result summary and detail/trace/graph are separate surfaces.

Main evidence:

- `ui/calculators_2point.py` `TwoPointTableModel.__init__`
- `ui/calculators_2point.py` `IsoCspfSingleWidget._init_ui`
- `ui/calculators_2point.py` `_recalculate_two_point`
- `ui/calculators_2point.py` `RegionDetailTab`

### Task 2: Current Tkinter audit

Result: OK.

Current Tkinter summary:

- `IsoIseer2PointSection` uses `MetricInputTable` for `35 Full` and `35 Half` capacity/power input.
- It calculates both `ISO 16358-1` and `India ISEER`, then emits one `ResultSummary` per profile.
- Each summary includes `EER Full`, `EER Half`, `CSPF/ISEER`, `CSTL [kWh]`, and `CSEC [kWh]`.
- `ResultPanel.set_summaries()` renders those summaries as stacked compact tables and stores text copy output through `ResultSummary.as_text()`.
- Existing Hong Kong CSPF/HSPF result display also uses `ResultPanel`; it must remain unchanged.

Main evidence:

- `ui_tk/sections/iso_iseer_2point_section.py` `recalculate_now`
- `ui_tk/sections/iso_iseer_2point_section.py` `_summarize_two_point_result`
- `ui_tk/result_panel.py` `set_summaries` and `_render_summary_table`
- `ui_tk/result_models.py` `ResultSummary.as_text`
- `tests/test_ui_tk_iso_table_autocalc.py` 2-point and Hong Kong result assertions

### Task 3: Candidate comparison

Result: OK.

Candidates:

- A: keep stacked `ResultSummary`, refine labels/order. Lowest risk, but does not solve comparison readability.
- B: add 2-point-only comparison table surface. Best fit for PyQt reference shape, localized impact, low Hong Kong risk.
- C: add comparison-style rendering option to `ResultPanel`. More reusable, but broadens shared component risk.

Recommendation: Candidate B.

Reason: It addresses the specific 2-point comparison issue while avoiding a shared `ResultPanel` redesign and keeping Hong Kong CSPF/HSPF protected.

### Task 4: 189-b scope

Result: OK.

189-b implementation scope:

- Improve only `ISO / ISEER 2-point` result display.
- Keep selector/input/calculation behavior unchanged.
- Render a read-only comparison table with profile rows and metric columns.
- Preserve safe invalid-input output and copy-compatible text.
- Keep Hong Kong CSPF/HSPF result display unchanged.

Excluded from 189-b:

- SASO
- multi/batch
- detail/trace
- graph
- core calculator
- golden/fixture
- PyQt retirement
- window geometry / scroll
- `ResultPanel` large redesign

Split needed only if implementation requires a generic reusable comparison API, `ResultPanel` changes, shared copy/export abstraction, or broader visual token/layout ownership changes.

### Task 5: Design doc

Result: OK.

Created `docs/designs/2026-05-29-tkinter-iso-iseer-2point-result-visual-refinement.md` with background, audit summary, candidate comparison, recommendation, implementation scope, tests proposal, excluded scope, and risks/open questions.

### Task 6: Active report

Result: OK.

Created this active report with audit scope, candidate summary, recommendation, next implementation slice, excluded scope, and verification.

### Task 7: WORK_PLAN checkpoint

Result: OK.

Added a short 189-a checkpoint to `docs/WORK_PLAN.md`. It records design completion only and recommends `189-b ISO/ISEER 2-point result visual refinement implementation`.

### Task 8: Verification / commit / push

Result: OK.

## Verification

Commands run:

- `python3 -B tools/check_code_structure.py` -> OK (`code structure guard: OK (no findings)`)
- `git diff --check` -> OK
- `git status --short` -> showed only the allowed modified/new files before commit
- `git diff --name-only` -> showed `docs/WORK_PLAN.md`; untracked new design/report files were confirmed via `git status --short`
- `git diff --stat` -> showed `docs/WORK_PLAN.md | 2 ++`; untracked new design/report files were confirmed via `git status --short`

Full pytest was intentionally not run.

## Changed Files

- `docs/designs/2026-05-29-tkinter-iso-iseer-2point-result-visual-refinement.md`
- `docs/WORK_PLAN.md`
- `result_reports/active/189a_iso-iseer-2point-result-visual-refinement-design.md`

## Known Failures / Risks

- This is a design-only slice; no runtime UI screenshot or manual smoke was performed.
- 189-b still needs implementation tests to ensure the new 2-point comparison surface does not affect Hong Kong CSPF/HSPF `ResultPanel` behavior.

## Next Suggested Action

189-b ISO/ISEER 2-point result visual refinement implementation.

## Scope Compliance

- Source files were read only and not modified.
- Test files were read only and not modified.
- PyQt source was read only and not modified.
- `project_log.md`, `result_reports/memory/project_memory_seed.md`, summary, and archive files were not modified.

## Commit / Push

- Source/docs/report commit: pending at report write time.
- Push: pending at report write time.

## Project Memory Delta

- none
