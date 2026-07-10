# PyQt Calculator Reference Feature Migration Contract

## Purpose

This document translates the already-audited PyQt calculator-only reference
surface into migration requirements for the lightweight Tkinter calculator.
It does not run a new feature parity audit and does not approve PyQt source
retirement.

The governing evidence is:

- `result_reports/legacy/archive/154_pyqt-calculator-retirement-audit.md`, which
  classified calculator-only retirement candidates, retained Predict/Train
  assets, and shared PyQt hold assets.
- `result_reports/legacy/summaries/165_summary-pyqt-retirement-tkinter-ui-matrix-rules.md`,
  which confirmed the Tkinter direction and kept retirement held behind UX
  and packaging judgment.
- `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md` and
  `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md`, which own table
  behavior and input/result shape.
- `docs/designs/2026-05-23-tkinter-calculator-final-ux-contract.md`, which
  owns the Tkinter calculator interaction direction.

## Boundary

`app_calculator.py` is a thin PyQt entrypoint that launches
`ui.calc_window.CalculatorWindow`. The substantive calculator reference
surfaces are in `ui/calc_window.py` and `ui/calculators_2point.py`;
`ui/spreadsheet_table.py` is a held shared-utility reference for table
behavior, not a calculator-only deletion decision.

The migration target is the calculator-only workflow. It excludes PyQt
Predict/Train applications and their required UI dependencies. This document
does not change or retire any source, calculator route, profile, config,
schema, or packaging entrypoint.

## Decision Classes

### Must Migrate Before PyQt Calculator Retirement

Features that are currently part of the PyQt calculator user workflow must be
available in Tkinter, or be explicitly removed from the supported calculator
scope in a separate approved decision, before calculator-only PyQt source can
be retired.

- A calculator entrypoint and standard/region navigation for retained
  supported calculator surfaces.
- Matrix-shaped numeric input, automatic calculation, summary output, and
  user-facing validation feedback.
- Existing standard/metric surfaces that remain supported: ISO/ISEER and SASO
  references, EN 14825 SEER/SCOP, and AHRI 210/240 SEER2/HSPF2.
- Batch/multi input if the ISO/ISEER multi workflow remains a supported
  calculator capability.

### Must Redesign Lightweight

These are user capabilities, not PyQt widget designs. Their Tkinter form must
be designed around the lightweight application, UI/UX SSOT, and packaging
constraints.

- Spreadsheet-like editing behavior on Tkinter matrix widgets.
- Read-only result detail and trace inspection surfaces.
- Graph/detail review surfaces, using PyQt behavior as UX evidence only.
- Standard-specific input panels where PyQt layout is tied to Qt widgets or
  modal/dialog composition.

### Defer Until Explicit Phase

- Additional ISO/ISEER 2-point, SASO T3, EN 14825, and AHRI 210/240 Tkinter
  implementation is sequenced after the current Hong Kong layout and table
  behavior work.
- Graph/detail implementation follows an explicit lightweight design step.
- Any large graph dependency decision follows Windows packaging-size
  evidence.
- Windows PyInstaller measurement follows the UX/migration planning steps and
  requires a Windows host.
- PyQt calculator source retirement remains a later reconsideration gate.

### Do Not Migrate As-Is

- Do not copy `QTableView`, `QAbstractTableModel`, `QStyledItemDelegate`,
  `QTabWidget`, modal message-box, Qt stylesheet, or PyQt runtime structure
  into the Tkinter application.
- Do not preserve a raw result-label/text-dump presentation when the active
  result-surface rule requires summary tables and concise status.
- Do not make Tkinter UI matrix layout part of core, profile, dispatcher, or
  calculator result-schema contracts.
- Do not bring `matplotlib` or another large graph dependency into the
  lightweight runtime without the packaging decision gate.

### Keep / Hold Outside Tkinter Migration

- PyQt Predict/Train entrypoints and their direct UI dependencies remain
  retention candidates outside calculator-only migration.
- `ui/spreadsheet_table.py`, `ui/theme.py`, dedicated retained tests, PyQt
  environment guard support, and the PyQt support-matrix guide remain held
  assets pending their own ownership decisions.
- Historical design/audit/report records remain evidence; migration does not
  rewrite them as current implementation state.

## Feature Migration Matrix

| Feature family | PyQt reference source | Current Tkinter status | Migration decision | Required before retirement | Suggested implementation slice |
| --- | --- | --- | --- | --- | --- |
| Calculator entrypoint and standard navigation | `app_calculator.py`; `ui/calc_window.py` `CalculatorWindow.init_ui()` tabs | `app_calculator_tk.py` / `ui_tk.calculator_app` exposes ISO 16358 only | Must migrate retained standard navigation without PyQt runtime | Yes, for each standard kept in supported scope | S4 standard/region expansion plan, then per-standard implementation |
| ISO 16358 Hong Kong CSPF/HSPF surface | `ui/calculators_2point.py` `IsoCspfSingleWidget`; `RegionResultTableModel`; `RegionDetailTab` | Matrix input, auto-calc, and summary result exist; post-166 layout correction items are pending | Must migrate; finish the user-visible layout correction before additional parity work | Yes | S1 ISO HK layout correction |
| ISO/ISEER 2-point and SASO T3 surfaces | `ui/calculators_2point.py` `IsoCspfSingleWidget`, profile switching, `_recalculate_two_point()`, `_recalculate_saso()` | Not implemented in Tkinter | Defer implementation until standard/region expansion plan; must migrate or be explicitly descoped | Yes, unless separately descoped | S4 plan followed by ISO/ISEER and SASO slices |
| EN 14825 SEER/SCOP surface | `ui/calc_window.py` `init_en_tab()`, `calculate_en()`; `ui/spreadsheet_table.py` EN table factories | Not implemented in Tkinter | Must migrate as a lightweight matrix/summary surface if EN remains supported | Yes | S4 plan followed by EN slice |
| AHRI 210/240 SEER2/HSPF2 surface | `ui/calc_window.py` `init_ahri_tab()`, `calculate_ahri()`, `calculate_hspf2_v3()`; `ui/spreadsheet_table.py` AHRI factories | Not implemented in Tkinter | Must migrate as a lightweight matrix/summary surface if AHRI remains supported | Yes | S4 plan followed by AHRI slice |
| Excel-like table behavior | `ui/calculators_2point.py` `ProfileInputGridModel` / `ProfileInputGridView`; `ui/spreadsheet_table.py`; active table contract | Hong Kong matrix exists; full selection, TSV copy/paste, delete/clear, undo, and complete Tab/Enter workflow remain pending | Must redesign lightweight under the Tkinter adapter and common table contract | Yes for editable matrix surfaces | S2 Tkinter Excel-like table behavior |
| Auto-calc/action model | `ui/calculators_2point.py` automatic recalculation; `ui/calc_window.py` retains manual outer button for EN/AHRI | ISO Hong Kong auto-calc exists | Must migrate using the Tkinter auto-calc direction, not the PyQt manual action layout | Yes | S1 preserve for ISO; carry into each later standard slice |
| Result summary and result detail | `ui/calculators_2point.py` result tables, detail tabs, trace table; `ui/calc_window.py` result label | CSPF/HSPF compact summary tables exist; detail surface absent; bottom copy/clear buttons are queued for removal in layout correction | Summary must migrate; detail must be redesigned lightweight and scheduled separately | Summary: yes; detail: gate decision before retirement | S1 summary layout correction; S3 detail design |
| Graph/detail surface | `ui/calculators_2point.py` `BinGraphWidget`, `TraceDetailPanel`, `RegionDetailTab` | Not implemented in Tkinter | Must redesign lightweight; defer implementation and dependency decision | No until explicit UX scope decision; decision itself required before retirement | S3 graph/detail surface design |
| Validation/error feedback | `ui/calc_window.py` validation/message-box and styling path; `ui/calculators_2point.py` invalid-cell display | Concise result status exists; user-reported gray-block error appearance requires correction | Must migrate as inline editable-cell/status feedback; do not port modal/Qt styling as-is | Yes | S1 ISO error-state correction; extend per standard |
| Batch/multi input | `ui/calculators_2point.py` `BatchTwoPointDialog`, row calculation and trace selection | Not implemented in Tkinter | Defer until explicit scope phase; migrate or explicitly descope before retirement | Yes, if ISO/ISEER multi remains supported | S4 expansion plan / later batch slice |
| Packaging and retirement gate | 154 audit retirement slices; 165 held status; PyQt entrypoint as packaging reference | Tkinter path exists; Windows measurement not performed in this phase | Keep retirement held until UX migration and packaging judgment complete | Yes | S5 packaging measurement; S6 retirement reconsideration |

## Ordered Migration Slices

### S1. Tkinter ISO HK Layout Correction

Apply the next visible Hong Kong corrections without expanding standards:

- Separate the rated-display value presentation as specified for the next
  implementation task.
- Present the vertical flow as CSPF input, CSPF result, HSPF input, HSPF
  result.
- Remove the bottom `결과 복사` / `결과 지우기` buttons.
- Center numeric values in matrix/result cells.
- Correct the invalid-input state that currently renders as an unwanted gray
  block.

This slice changes Tkinter presentation only; it must preserve existing
auto-calc and calculator results.

### S2. Tkinter Excel-like Table Behavior

Implement the common spreadsheet baseline for editable Tkinter tables:
selection, TSV copy, TSV paste, Delete/Backspace clear, undo, and Tab/Enter
navigation. This is a lightweight Tkinter implementation of the common
behavior contract, not a port of PyQt model/view classes.

### S3. Tkinter Graph / Detail Surface Design

Use the PyQt result detail table and graph behavior as reference UX. Define a
lightweight Tkinter detail surface, including whether detail is required for
retirement parity. Do not adopt a large plotting dependency before Windows
packaging-size evidence.

### S4. Tkinter Standard / Region Expansion Plan

Decide and then implement the remaining calculator surfaces in an explicit
order: ISO/ISEER 2-point, SASO T3, EN 14825, and AHRI 210/240. Each standard
requires its own input/result/validation acceptance criteria and must not
silently inherit Qt-specific UI composition.

### S5. Windows PyInstaller Size Measurement

Measure the lightweight packaging outcome on a Windows host after sufficient
Tkinter capability exists for a meaningful comparison.

### S6. PyQt Calculator Source Retirement Reconsideration

Re-evaluate retirement only after the Tkinter UX, migration requirements, any
explicit descope decisions, and packaging evidence are available. Retirement
remains held; this contract is not authorization to delete PyQt source.

## Retirement Gate

The PyQt calculator-only source is not retired by documenting migration. A
future retirement task must confirm:

1. Required supported calculator surfaces are implemented in Tkinter or
   explicitly descoped by an approved decision.
2. Required table interaction, auto-calc, result, and validation behavior is
   present in the retained Tkinter scope.
3. Graph/detail and batch/multi requirements have explicit implement-or-
   descope decisions.
4. Windows packaging evidence has been recorded where it is a dependency for
   the lightweight direction.
5. Predict/Train and held shared PyQt assets are excluded from calculator-only
   source retirement unless separately authorized.

## Non-goals

- Implementing any Tkinter feature or modifying PyQt code.
- Repeating the 154 feature/source retirement audit.
- Approving source retirement, shared utility removal, or PyQt
  Predict/Train changes.
- Selecting implementation APIs beyond the migration and sequencing boundary.
