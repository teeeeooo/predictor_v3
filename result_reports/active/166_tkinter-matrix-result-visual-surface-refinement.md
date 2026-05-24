# 166 Tkinter Matrix / Result Visual Surface Refinement

## Goal

Apply the project-wide matrix/result surface rule to the visible Tkinter
ISO 16358 / Hong Kong CSPF and HSPF screen so that inputs read as bordered
matrix tables and outputs read as compact summary result tables.

## Scope

- Refined the widget surface in `ui_tk/metric_input_table.py` and
  `ui_tk/result_panel.py`.
- Added focused widget-role coverage in
  `tests/test_ui_tk_iso_table_autocalc.py`.
- Updated the Tkinter final UX contract, manual smoke guide, and work plan
  for task 166 and its next manual verification step.
- Kept the existing section input schema, formatter/result model, auto-calc
  path, profile routing, dispatcher, and calculator core unchanged.

## Non-goals

- No calculator/core/profile/dispatcher/config/fixture/golden changes.
- No EN/AHRI/KS or region expansion.
- No PyQt modification or retirement.
- No graph/detail surface, chart adapter, `matplotlib`, or Canvas chart.
- No visual-token full wiring, TSV copy/paste, undo/redo, or full selection
  behavior.
- No manual macOS UX smoke, packaging run, result-report lifecycle
  maintenance, `project_log.md`, `ACTIVE_DOCUMENTS.md`, or memory seed update.

## Project Memory Recall Gate

`result_reports/memory/project_memory_seed.md` was searched only for the
requested keywords (`input matrix`, `result surface`, `Tkinter`, `table grid`,
`matrix table`, `visual design`, `Hong Kong`, `CSPF`, `HSPF`,
`graph detail`, `PyQt retirement`). The relevant entries state that:

- `docs/ui_ux/04_VISUAL_DESIGN_ARCHITECTURE.md` and
  `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md` own the
  project-wide matrix/summary direction.
- Tkinter Hong Kong CSPF/HSPF already retained auto-calc and the smoke values,
  while PyQt retirement and graph/detail remain held.

The related ranges in
`result_reports/summaries/165_summary-pyqt-retirement-tkinter-ui-matrix-rules.md`
confirmed that visible refinement must occur before manual smoke. These
records were used as evidence only; `project_memory_seed.md` was not changed.

## Task Results

### Task 1: Existing Gap And Implementation Boundary

Task 163 had established the correct content arrangement, but
`MetricInputTable` rendered plain `Label` and `Entry` widgets in a grid with
per-widget padding and no enclosing/cell borders. It therefore remained
visually similar to a form. `ResultPanel` similarly used a `LabelFrame` with
loose header/value labels rather than a visibly bounded mini table.

The relevant `05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md` clauses require one
structured surface, visible row/column headers, visually distinct editable
and static cells, and summary output rather than raw text. The implementation
boundary was limited to `MetricInputTable`, `ResultPanel`, one targeted UI
test, and the requested minimal docs.

### Task 2: Input Matrix Surface

`MetricInputTable` now owns a single `matrix_surface` outer frame with grid
line/background borders. It builds contiguous cell frames for:

- column headers and the corner cell (`header_cell`);
- row headers (`row_header_cell`);
- editable white cells containing flat, aligned entry editors
  (`editable_cell` / `editable_entry`);
- static/not-applicable cells with a muted background and `-`
  (`static_cell`).

The widget exposes role-bearing frame mappings for structure tests while
retaining `set_value`, `set_values`, `get_numeric_values`,
`get_text_values`, callback behavior, and Return focus traversal. CSPF and
HSPF section input definitions and defaults were not modified.

### Task 3: Result Summary Surface

`ResultPanel.set_summaries()` now renders each latest metric into a bordered
compact summary table containing:

- a small metric title strip;
- distinct header cells (`summary_header_cell`);
- distinct value cells (`summary_value_cell`);
- a separate small status line (`summary_status`).

The visible CSPF and HSPF header/value content still comes from the existing
formatted `ResultSummary` fields, so `CSPF / CSTL [kWh] / CSEC [kWh]` and
`HSPF / HSTL [kWh] / HSEC [kWh]` are unchanged. `append`, `set_text`,
copy, clear, latest-result replacement, and validation-status rendering
remain compatible.

### Task 4: Tests

`tests/test_ui_tk_iso_table_autocalc.py` now verifies that:

- each metric input has one table frame with header, row-header, editable,
  and static cell roles;
- the static `-` cell remains part of the same matrix;
- the existing visible column/row labels and absence of calculation buttons
  remain intact;
- each result summary exposes header/value/status table roles;
- defaults still show CSPF `4.939` and HSPF `3.643`;
- repeat auto-calc does not append result history;
- result text does not expose `None`, raw long float content, raw dict
  representation, or `Traceback`;
- invalid CSPF input appears in the result status line.

No screenshot, pixel, expected/golden, fixture, PyQt, or xfail/skip-marker
test changes were made.

### Task 5: Docs And Work Plan

- `docs/guides/lightweight_calculator_tk_manual_smoke.md` now checks the
  bordered matrix, distinct static/editable cells, compact bordered result
  table, and separate status line during the next macOS manual smoke.
- `docs/designs/2026-05-23-tkinter-calculator-final-ux-contract.md` records
  task 166 as the visible-widget implementation of the `05` rule.
- `docs/WORK_PLAN.md` records task 166 completion and sets the requested next
  action order: macOS manual UX smoke; optional spacing/style refinement;
  optional graph/detail design; Windows packaging measurement when available;
  optional standard/region expansion; then PyQt retirement reconsideration.

### Task 6: Report And Memory Delta

This report is the new active task-166 artifact after task-165 lifecycle
summary work. Lifecycle archive/summary maintenance is intentionally excluded:
this task creates a current active implementation report and does not meet a
request to fold it into a new summary.

### Task 7: Verification

All requested automated verification commands passed:

```text
python3 -B tools/check_code_structure.py
code structure guard: OK (no findings)

python3 -B -m py_compile ui_tk/metric_input_table.py ui_tk/result_panel.py \
  ui_tk/result_models.py ui_tk/sections/iso_cspf_section.py \
  ui_tk/sections/iso_hspf_section.py tests/test_ui_tk_iso_table_autocalc.py
passed

python3 -B -m pytest tests/test_ui_tk_iso_table_autocalc.py \
  tests/test_ui_tk_iso16358_helpers.py -q -rxXs
14 passed

python3 -B -m pytest -q -rxXs
630 passed, 32 skipped, 19 xfailed
```

The stated recent baseline was `629 passed, 32 skipped, 19 xfailed`; the
delta is `+1 passed` from the added matrix visual-role test. The required
xfail count remains `19`, and the full suite completed without a native abort.
Manual macOS UX smoke is intentionally pending until after this implementation.

## Changed Files

- `ui_tk/metric_input_table.py` - bordered input matrix cell surface and role
  mappings.
- `ui_tk/result_panel.py` - bordered compact result tables and role mappings.
- `tests/test_ui_tk_iso_table_autocalc.py` - structural visual-surface and
  rendered-output coverage.
- `docs/guides/lightweight_calculator_tk_manual_smoke.md` - post-166 visual
  manual checks.
- `docs/designs/2026-05-23-tkinter-calculator-final-ux-contract.md` - task
  166 implementation status.
- `docs/WORK_PLAN.md` - completion and next-action sequence.
- `result_reports/active/166_tkinter-matrix-result-visual-surface-refinement.md`
  - this report.

## Known Failures / Risks

- Automated tests verify widget structure and text/state behavior, not the
  macOS rendered appearance. The scheduled macOS manual UX smoke remains the
  acceptance step for visual spacing and legibility.
- Local surface colors are deliberately minimal and confined to the two
  widgets. Full visual-token wiring was not performed because task 166 is a
  narrow visible-surface correction and the prompt explicitly excludes full
  adoption.
- Graph/detail was not added because the active rule keeps summary results
  primary and defers supplementary surfaces until there is a demonstrated
  review need.
- The broader Tkinter spreadsheet behavior backlog (including TSV
  copy/paste and undo/redo) remains outside this visual-only slice as
  explicitly scoped.

## Next Suggested Action

Run the macOS Tkinter manual UX smoke against the bordered matrix/result
surface, then make a narrow spacing/style adapter refinement only if that
visual run exposes a remaining issue.

## Scope Compliance

- Modified only the requested Tkinter surface, targeted test, minimal docs,
  work-plan, and result-report paths.
- Did not modify core calculator, profile/dispatcher, region config,
  expected/golden, fixture, PyQt, Train/Predict, `ACTIVE_DOCUMENTS.md`,
  `project_log.md`, or `result_reports/memory/project_memory_seed.md`.
- Did not perform manual smoke, packaging, lifecycle maintenance, graph/chart
  work, or full visual-token wiring.

## Commit / Push

- Source/tests/docs commit: `bc22091` (`fix: refine Tkinter matrix and result surfaces`).
- Report commit: this report is committed separately after the source commit.
- Push target: `origin/work/ui-ux-ssot-adoption`.

## Project Memory Delta

```yaml
- type: decision
  topic: tkinter-matrix-result-visual-surface-refinement
  content: "Tkinter ISO Hong Kong CSPF/HSPF input and result widgets apply the project-wide matrix/result surface rule at the visible widget layer: inputs render as bordered matrix tables and outputs render as compact bordered summary tables while auto-calc and calculator routes remain unchanged."
  keywords:
    - Tkinter
    - input matrix
    - result surface
    - Hong Kong
    - CSPF
    - HSPF
  assertionStatus: verified
  source: result_reports/active/166_tkinter-matrix-result-visual-surface-refinement.md
```
