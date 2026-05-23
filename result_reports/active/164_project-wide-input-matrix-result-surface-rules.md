# 164. Project-wide Input Matrix and Result Surface Rules

## Goal

Close the UI/UX rule gap revealed by tasks 162 and 163 by adopting a
project-wide SSOT for shaping repeated input data into matrix surfaces and
user-facing results into summary surfaces.

## Scope

- Add a new active UI/UX SSOT owner for input matrix and result surface rules.
- Connect that owner to existing UI/UX SSOT, toolkit adapters, the Tkinter
  calculator final UX contract, active document inventory, and work plan.
- Record graph/detail surfaces as a later lightweight design phase rather than
  an implicit requirement of the existing summary UI.

## Non-goals

- No code, UI widget, visual styling, token wiring, or test changes.
- No calculator, profile/dispatcher, expected/golden, fixture, standard, or
  region changes.
- No PyQt retirement, graph/chart implementation, `matplotlib`, packaging,
  `project_log.md`, `project_memory_seed.md`, or lifecycle move.

## Project Memory Recall Gate

Only the requested keyword searches were run against
`result_reports/memory/project_memory_seed.md`; the seed was not read in full
and was not modified. Relevant evidence confirms the retained PyQt/Tkinter
direction split, the auto-calc direction, and the existing table UX owner.
The current prompt, active UI/UX documents, and task-162/163 reports provide
the direct evidence for this rule adoption.

## Task Results

### Task 1 - Existing Owners And Rule Gap

- Confirmed existing role boundaries:
  - `03_SPREADSHEET_TABLE_UX_CONTRACT.md` owns spreadsheet-like table
    interaction behavior.
  - `adapters/TKINTER_TABLE_ADAPTER.md` and
    `adapters/PYQT_TABLE_IMPLEMENTATION.md` own toolkit implementation
    constraints.
  - `04_VISUAL_DESIGN_ARCHITECTURE.md` owns project-wide visual philosophy
    and semantic-role direction.
  - The Tkinter final UX contract owns the calculator-specific direction.
- Tasks 162 and 163 exposed a separate missing rule: a table behavior
  contract alone did not say that comparable repeated values must first be
  shaped into one matrix, or that primary results must be summary surfaces
  rather than raw text.
- Task 163 is treated as a valid first concrete application. Task 164 promotes
  its generalizable surface decision to project-wide policy rather than
  evaluating or reversing the implementation.

### Task 2 - New 05 UI/UX Rule Document

- Added `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md`.
- Input matrix rule:
  - repeated measurements, conditions, and comparisons are not scattered
    label-entry controls;
  - two or more comparable instances with two or more repeated variables
    default to one matrix table;
  - row and column headers are mandatory;
  - singleton reference values fold into the matrix when semantically valid;
  - not-applicable cells may remain as static/disabled/blank cells rather
    than fragmenting the matrix;
  - UI matrix schema remains in the UI layer, outside core/ML/profile/
    dispatcher contracts.
- Result summary rule:
  - primary outputs use a metric/value table or compact summary cards;
  - raw text dumps, raw dictionaries, `None`, long float noise, and
    tracebacks fail the user-visible result rule.
- Detail/graph rule:
  - graph/detail surfaces supplement, not replace, summary surfaces;
  - existing PyQt graph/detail UI remains reference UX;
  - any Tkinter graph is a later lightweight chart/detail design;
  - large graph dependencies such as `matplotlib` are deferred until Windows
    packaging size evidence exists.
- Included calculator, Predictor, Trainer, and result-summary examples, plus
  acceptance criteria and anti-patterns.

### Task 3 - Existing UI/UX SSOT Connections

- `00_UI_UX_SYSTEM.md` now points to `05` for `predictor_v3` repeated-input
  matrix and result-summary surface shaping.
- `03_SPREADSHEET_TABLE_UX_CONTRACT.md` now explicitly separates table
  behavior ownership from `05` surface-shaping ownership.
- `04_VISUAL_DESIGN_ARCHITECTURE.md` now links table-first/result-surface
  philosophy to `05`'s concrete matrix and summary rules.
- `TKINTER_TABLE_ADAPTER.md` now requires `05` shape selection before
  selecting Entry-grid or Treeview implementation.
- `PYQT_TABLE_IMPLEMENTATION.md` contained a compatible role boundary, so it
  was minimally linked to `05` before PyQt implementation selection.

### Task 4 - Tkinter Contract And Manual Smoke

- The Tkinter final UX contract now includes `05` as an applied owner and
  identifies task 163 as its first concrete application, without limiting the
  rule to ISO Hong Kong.
- The manual smoke guide now identifies its matrix/summary checks as the
  concrete `05` application and explicitly excludes graph/detail verification
  from the current smoke phase.

### Task 5 - Active Documents And Work Plan

- Registered `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md` in
  `ACTIVE_DOCUMENTS.md` as an active UI/UX SSOT document.
- Added task 164 completion to `docs/WORK_PLAN.md`.
- Next recommended action order is now:
  1. Lifecycle summary/archive maintenance.
  2. macOS Tkinter manual UX smoke.
  3. Tkinter matrix/result visual surface refinement, if needed.
  4. Lightweight graph/detail surface design, if needed.
  5. Windows PyInstaller size measurement when a Windows host is available.
  6. Tkinter standard/region expansion, if needed.
- PyQt calculator source retirement remains held, and large graph
  dependencies remain deferred until Windows packaging size judgment.

### Task 6 - Report And Memory Delta

- This report records the new rule owner, cross-document boundaries, work
  plan outcome, and one durable Project Memory Delta below.
- Metadata-only lifecycle inspection found 10 active reports before this
  report and existing `summaries/` and `archive/` directories. Although this
  meets the maintenance trigger and is correctly ordered as the next action,
  the present prompt explicitly prohibits lifecycle summary/archive movement;
  none was performed.

### Task 7 - Verification

- `python3 -B tools/check_code_structure.py`: PASS (`no findings`).
- `python3 -B -m pytest -q -rxXs`: PASS
  (`629 passed, 32 skipped, 19 xfailed`).
- The result matches the supplied pre-task baseline exactly, as expected for
  a documentation-only change.

## Changed Files

- `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md`
- `docs/ui_ux/00_UI_UX_SYSTEM.md`
- `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md`
- `docs/ui_ux/04_VISUAL_DESIGN_ARCHITECTURE.md`
- `docs/ui_ux/adapters/TKINTER_TABLE_ADAPTER.md`
- `docs/ui_ux/adapters/PYQT_TABLE_IMPLEMENTATION.md`
- `docs/designs/2026-05-23-tkinter-calculator-final-ux-contract.md`
- `docs/guides/lightweight_calculator_tk_manual_smoke.md`
- `ACTIVE_DOCUMENTS.md`
- `docs/WORK_PLAN.md`
- `result_reports/active/164_project-wide-input-matrix-result-surface-rules.md`

## Known Failures / Risks

- The project-wide rule is adopted in documentation, but additional
  Predictor/Trainer or future UI adoption remains later work.
- The updated Tkinter manual smoke has not yet been executed.
- Graph/detail and visual refinement remain intentionally undesigned beyond
  the boundary/defer decision in `05`.

## Next Suggested Action

Perform the explicitly queued lifecycle summary/archive maintenance as a
separate task, then run the updated macOS Tkinter manual UX smoke.

## Scope Compliance

- Only the requested active documentation, SSOT cross-references, work plan,
  and this report were created or modified.
- No code, tests, UI implementation, PyQt/Tkinter styling, graph
  implementation, retirement, log, memory seed, or lifecycle files were
  changed.

## Commit / Push

- Source/docs commit: `b338493` (`docs: add project-wide input matrix surface rules`).
- Report commit: this report is committed separately after document verification.
- Push: `origin/work/ui-ux-ssot-adoption` after the report commit.

## Project Memory Delta

- type: decision
  topic: project-wide-input-matrix-result-surface-rules
  content: "predictor_v3 adopts project-wide input matrix and result surface rules: repeated structured inputs must be normalized into row/column-header matrix tables, while results must be shown as summary surfaces rather than raw text dumps; graph/detail surfaces are deferred to a lightweight dedicated phase."
  keywords:
    - UI/UX SSOT
    - input matrix
    - result surface
    - Tkinter
    - PyQt
    - graph detail
  assertionStatus: observed
  source: result_reports/active/164_project-wide-input-matrix-result-surface-rules.md
