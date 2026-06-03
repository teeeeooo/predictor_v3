# 167 PyQt Calculator Reference Feature Migration Contract

## Goal

Reorganize the existing PyQt calculator-only retirement audit evidence into a
Tkinter migration contract that states which user-facing capabilities must be
migrated, redesigned, deferred, rejected as direct ports, or held outside the
Tkinter migration boundary.

## Scope

- Added
  `docs/designs/2026-05-24-pyqt-calculator-reference-feature-migration-contract.md`.
- Registered the new active design record in `ACTIVE_DOCUMENTS.md`.
- Reordered the calculator follow-up sequence in `docs/WORK_PLAN.md`.
- Used the existing 154 audit and 165 summary as primary decision evidence,
  with limited source-symbol confirmation for the named PyQt/Tkinter paths.

## Non-goals

- No new feature parity audit.
- No PyQt or Tkinter source implementation, test change, source retirement,
  graph/table behavior implementation, or packaging execution.
- No changes to Predict/Train, core, profile/dispatcher/config/schema,
  `project_log.md`, or `result_reports/memory/project_memory_seed.md`.
- No lifecycle archive/summary movement.

## Project Memory Recall Gate

`result_reports/memory/project_memory_seed.md` was keyword-searched only for
`PyQt retirement`, `Tkinter calculator`, `graph detail`, `input matrix`,
`result surface`, `Hong Kong`, `calculator-only`, `visual design`, and
`packaging`. The relevant entries confirm:

- PyQt calculator-only assets were audited separately from retained
  Predict/Train assets.
- Tkinter Hong Kong matrix/summary/auto-calc exists while PyQt retirement
  remains held behind UX and packaging judgment.
- Graph/detail and full dependency decisions remain deferred.

The seed was treated as evidence and was not modified.

## Task Results

### Task 1: Existing Reference Boundary

This task used
`result_reports/archive/154_pyqt-calculator-retirement-audit.md` and
`result_reports/summaries/165_summary-pyqt-retirement-tkinter-ui-matrix-rules.md`
instead of repeating their audit.

The existing boundary remains:

- `app_calculator.py` is a thin entrypoint that launches
  `ui.calc_window.CalculatorWindow`.
- `ui/calc_window.py`, `ui/calculators_2point.py`, and the calculator error
  path are the substantive calculator-only PyQt reference/source-retirement
  candidates.
- `ui/spreadsheet_table.py`, shared visual/test support, and environment
  support remain hold assets pending separate ownership decisions.
- PyQt Predict/Train remains outside calculator-only retirement scope.

Limited code reads confirmed the reference feature locations without creating
a new inventory: ISO/ISEER/SASO, batch and graph/detail are exposed through
`ui/calculators_2point.py`; EN and AHRI standard tabs and result paths are
exposed through `ui/calc_window.py`; and common PyQt table behavior evidence
exists in `ui/spreadsheet_table.py`.

### Task 2: Migration Contract

The new design record groups migration requirements into five decision
classes:

1. Must migrate before PyQt calculator retirement.
2. Must redesign lightweight rather than port Qt widget structure.
3. Defer until an explicit implementation or scope-decision phase.
4. Do not migrate PyQt/runtime structure as-is.
5. Keep/hold outside Tkinter calculator migration.

Its feature matrix covers the required functional families:

| Feature group | Migration decision |
| --- | --- |
| ISO 16358 Hong Kong | Existing Tkinter surface must complete the pending layout correction while preserving auto-calc/result behavior. |
| ISO/ISEER 2-point and SASO T3 | Plan and migrate later, or explicitly descope, before retirement. |
| EN 14825 | Migrate as a lightweight matrix/summary standard surface if retained in supported scope. |
| AHRI 210/240 | Migrate as a lightweight matrix/summary standard surface if retained in supported scope. |
| Excel-like table behavior | Redesign in Tkinter under the active interaction contract; required for editable matrix surfaces. |
| Auto-calc/action model | Preserve the Tkinter auto-calc direction rather than porting manual PyQt action composition. |
| Result summary/detail | Summary is required; detail receives a lightweight design decision before retirement. |
| Graph/detail | Use PyQt as reference UX, defer implementation/dependency choice to its design phase. |
| Validation/error feedback | Use inline Tkinter feedback; do not port modal/Qt styling as-is. |
| Batch/multi input | Migrate or explicitly descope if the existing ISO/ISEER multi workflow remains supported. |
| Packaging/retirement gate | Retirement remains held until migration and packaging judgment are complete. |

The contract does not prescribe new implementation APIs and explicitly states
that it is not source-retirement authorization.

### Task 3: Active Docs And Work Plan

`ACTIVE_DOCUMENTS.md` now registers the migration contract as an active
design record consumed by calculator migration and retirement-gate tasks.

`docs/WORK_PLAN.md` now places future work in this sequence:

1. Tkinter ISO HK layout correction: rated display separation; CSPF
   input/result followed by HSPF input/result; remove bottom copy/clear
   buttons; center numbers; fix invalid-input gray-block appearance.
2. Tkinter Excel-like table behavior: selection, TSV copy/paste, clear,
   undo, and Tab/Enter navigation.
3. Tkinter graph/detail surface design, preserving the large-dependency hold.
4. Tkinter standard/region expansion planning for ISO/ISEER, SASO T3, EN,
   and AHRI.
5. Windows PyInstaller size measurement.
6. PyQt calculator source retirement reconsideration only after UX,
   feature-migration, and packaging judgment.

`project_log.md` and `project_memory_seed.md` were deliberately not updated,
as instructed. No lifecycle work was performed.

### Documentation Sync Judgment

- `ACTIVE_DOCUMENTS.md`: updated because task 167 creates a new active design
  record.
- `docs/WORK_PLAN.md`: updated because the requested implementation and
  retirement-gate execution order changes.
- `project_log.md`: not updated because this task reorganizes existing
  154/165 decisions and the prompt prohibits modification.
- `docs/REFACTOR_PLAN.md`, `project_brief.md`, and standard notes/dev notes:
  not updated because no structural implementation plan, handoff state, or
  standard interpretation changes.

### Task 4: Report And Verification

This report captures the documentation-only contract organization, the held
retirement state, and one memory-delta candidate. Verification executed:

```text
python3 -B tools/check_code_structure.py
code structure guard: OK (no findings)

git diff --check
passed
```

The full pytest suite was not run because this task changes documentation
only and modifies no source or tests.

## Changed Files

- `docs/designs/2026-05-24-pyqt-calculator-reference-feature-migration-contract.md`
  - new reference-to-migration requirement contract.
- `ACTIVE_DOCUMENTS.md` - registers the active design record.
- `docs/WORK_PLAN.md` - reorders next migration/retirement-gate actions.
- `result_reports/active/167_pyqt-calculator-reference-feature-migration-contract.md`
  - this report.

## Known Failures / Risks

- The migration contract organizes existing reference evidence and current
  user-directed next actions; it does not demonstrate that pending Tkinter
  surfaces are implemented or accepted.
- Supported-scope decisions for ISO/ISEER, SASO, EN, AHRI, batch, and
  graph/detail must be resolved through later explicit phases before a source
  retirement decision is defensible.
- Full-suite regression evidence is unchanged because no code/test path was
  modified and the suite was intentionally not run for this docs-only task.

## Next Suggested Action

Implement the narrowly scoped Tkinter ISO Hong Kong layout correction listed
as S1 in the migration contract and first in `docs/WORK_PLAN.md`.

## Scope Compliance

- Added or modified only the requested design/work-plan/active-doc/report
  documents.
- Did not modify PyQt or Tkinter code, tests, expected/golden/fixture files,
  Predict/Train, core/config/routing, `project_log.md`, or
  `result_reports/memory/project_memory_seed.md`.
- Did not retire source, run packaging, implement graph/table features, or
  perform report lifecycle maintenance.

## Commit / Push

- Documentation commit: `b571b95`
  (`docs: define PyQt calculator migration contract`).
- Report commit: this report is committed separately after the documentation
  commit.
- Push target: `origin/work/ui-ux-ssot-adoption`.

## Project Memory Delta

```yaml
- type: decision
  topic: pyqt-calculator-reference-feature-migration-contract
  content: "The audited PyQt calculator-only reference surface is organized as a held Tkinter migration gate: supported calculator input/result/action/validation and retained standard capabilities must migrate or be explicitly descoped, while Qt widget structure is not ported as-is and Predict/Train plus shared PyQt assets remain outside calculator-only migration."
  keywords:
    - PyQt calculator
    - Tkinter migration
    - retirement gate
    - feature contract
    - Predict/Train
  assertionStatus: observed
  source: docs/designs/2026-05-24-pyqt-calculator-reference-feature-migration-contract.md; result_reports/archive/154_pyqt-calculator-retirement-audit.md; result_reports/summaries/165_summary-pyqt-retirement-tkinter-ui-matrix-rules.md
```
