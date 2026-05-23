# 163. Tkinter ISO Hong Kong Input/Output UI Correction

## Goal

Refine the functional Hong Kong CSPF/HSPF table and auto-calc slice into a
calculator-facing input/output surface aligned with the project-wide visual
architecture: coherent metric input tables and concise summary result cards.

## Scope

- Inspect the actual ISO Hong Kong result keys and correct display-layer
  mapping/formatting without changing calculator output schema.
- Replace separated rated/point grids in each metric section with one compact
  trial-input table.
- Render latest CSPF/HSPF outputs as summary cards while preserving auto-calc,
  copy, clear, and default smoke values.
- Add focused UI/formatter tests and minimally update the final UX contract,
  manual smoke guide, and work plan.

## Non-goals

- No core calculator, profile/dispatcher, region config, golden, fixture,
  xfail, or skip-marker changes.
- No EN/AHRI/KS or region expansion.
- No PyQt UI or retirement work, Predict/Train changes, packaging, or visual
  token full adoption.
- No TSV copy/paste, undo/redo, or full spreadsheet selection model.
- No `ACTIVE_DOCUMENTS.md`, `project_log.md`,
  `result_reports/memory/project_memory_seed.md`, or lifecycle moves.

## Project Memory Recall Gate

Only the requested keyword searches were run against
`result_reports/memory/project_memory_seed.md`; the seed was neither read in
full nor modified. Relevant evidence confirms that auto-calc is the selected
calculator action direction and that Tkinter calculator work remains separate
from retained PyQt Predict/Train surfaces and gated PyQt calculator
retirement. The active UI/UX documents and report 162 remain the direct owners
for this display correction.

The user's changed input values visible in a screenshot were explicitly
excluded from fault analysis: altered user input may legitimately alter the
result. The correction is based on default-input output display and widget
structure only.

## Design Gate Summary

- The UI-to-core boundary remains unchanged: CSPF/HSPF sections continue to
  call the existing resolver, dispatcher, and calculator methods.
- `MetricInputTable` owns only table/card layout, editable-cell mapping, and
  numeric text reads; it does not know profiles or calculations.
- Pure summary formatting owns raw-result alias mapping and display units;
  `ResultPanel` owns rendering/copy/clear only.
- Existing `TableGrid` foundation remains available; the visible Hong Kong
  sections use the small mapped-table wrapper because each table contains one
  intentional static power cell.

## Task Results

### Task 1 - Current Gap And Raw Keys

- The 162 screen used separate declared/rated and measurement grids, leaving
  each metric visually fragmented rather than showing one trial-input table.
- The 162 result panel presented formatted text in a large text widget rather
  than a summary surface.
- Targeted default-input inspection found these actual core result keys:
  - CSPF: `cspf`, `annual_cooling_kwh`, `annual_power_kwh`, `bin_details`.
  - HSPF: `hspf`, `hstl_wh`, `hsec_wh`,
    `heat_pump_energy_wh`, `auxiliary_energy_wh`, `bin_details`.
- Existing CSPF formatting looked for `cstl_wh`/`csec_wh`, producing
  user-visible `None`; HSPF displayed Wh raw floats directly.

### Task 2 - Result Mapping And Formatting

- Added pure `ui_tk/sections/result_formatting.py` and toolkit-neutral
  `ui_tk/result_models.py`.
- CSPF summary uses `annual_cooling_kwh` and `annual_power_kwh`, with
  compatibility aliases for named CSTL/CSEC variants.
- HSPF summary uses `hstl_wh` and `hsec_wh`, converted from Wh to kWh.
- Formatting policy is consistent:
  - `CSPF` / `HSPF`: three decimals.
  - `CSTL`, `CSEC`, `HSTL`, `HSEC`: kWh, one decimal.
  - unavailable value: `-`, never string `None`.
- Retained `format_cspf_result()` and `format_hspf_result()` now expose the
  same compact, copy-compatible policy without changing builders or core
  results.

### Task 3 - Result Summary UI

- `ui_tk/result_panel.py` now renders latest `ResultSummary` instances as
  compact metric cards with column labels, values, and status text.
- `Iso16358Tab` stores latest summaries per metric and calls
  `set_summaries()`; repeated auto-calc still replaces current results rather
  than accumulating history.
- The existing `append()` and `set_text()` APIs remain for compatibility.
  `copy()` copies a compact textual representation of current summary cards,
  and `clear()` removes both visible summaries and copy text.
- Validation displays a concise card status such as
  `입력 오류: 숫자 입력을 확인하세요.`; stack traces are not displayed.

### Task 4 - Input Table/Card Layout

- Added `ui_tk/metric_input_table.py`, a Tkinter-only mapped input-table
  adapter with no core, profile, PyQt, or token dependency.
- CSPF now displays one table with columns `정격`, `35 Full`, `35 Half` and
  rows `능력 [W]`, `전력 [W]`; the unused `정격` power cell is static `-`.
- HSPF now displays one table with columns `정격 난방`, `7 Full`, `7 Half`
  and the same two rows; the unused rated-heating power cell is static `-`.
- Default values, button-free auto-calc, and public `recalculate_now()` hooks
  are maintained.

### Task 5 - Tests

- Updated `tests/test_ui_tk_iso16358_helpers.py` to verify actual CSPF alias
  mapping, Wh-to-kWh conversion, fixed decimal display, and no `None`
  rendering.
- Updated `tests/test_ui_tk_iso_table_autocalc.py` to verify:
  - one `MetricInputTable` per metric and no calculate buttons;
  - required input table row/column labels;
  - visible summary-card labels;
  - default outputs `4.939 | 1769.6 | 358.3` and
    `3.643 | 273.2 | 75.0`;
  - no `None` or raw long HSPF float display;
  - recompute replacement, clear compatibility, invalid-input status, and
    idempotent input updates.
- These are display/unit tests only; no core expected or fixture changed.

### Task 6 - Documentation And Work Plan

- The final UX contract now records task 163 as the visible input/output
  correction following the functional table/auto-calc slice.
- The manual smoke guide now checks single metric tables, static cells, and
  summary-card kWh output instead of text-dump blocks.
- `docs/WORK_PLAN.md` records task 163 and orders the next recommended work:
  1. macOS manual UX smoke.
  2. Tkinter visual spacing/style adapter adoption, if needed.
  3. Windows PyInstaller size measurement when a Windows host is available.
  4. Tkinter standard/region expansion, if needed.
- PyQt calculator-only retirement remains held.

### Task 7 - Report And Memory Delta

- This full report records display mapping evidence, UI correction scope,
  tests, and the durable decision below.
- Metadata-only lifecycle inspection found 9 active reports before this
  report was added and existing `summaries/` and `archive/` directories.
  Lifecycle maintenance is not performed because this prompt explicitly
  prohibits summary/archive moves and related maintenance.

### Task 8 - Verification

- `python3 -B tools/check_code_structure.py`: PASS (`no findings`).
- `python3 -B -m py_compile ...`: PASS, covering the new summary/input modules
  and modified ISO Tkinter modules/tests.
- Targeted formatter/ISO UI/grid/foundation tests: PASS (`36 passed`).
- `python3 -B -m pytest -q -rxXs`: PASS
  (`629 passed, 32 skipped, 19 xfailed`).
- Compared with the supplied baseline `628 passed, 32 skipped, 19 xfailed`,
  the pass count increases by one due to new formatter coverage; xfail count
  remains 19 and no native abort occurred.

## Changed Files

- `ui_tk/result_models.py`
- `ui_tk/metric_input_table.py`
- `ui_tk/sections/result_formatting.py`
- `ui_tk/sections/iso16358_helpers.py`
- `ui_tk/result_panel.py`
- `ui_tk/tabs/iso16358_tab.py`
- `ui_tk/sections/iso_cspf_section.py`
- `ui_tk/sections/iso_hspf_section.py`
- `tests/test_ui_tk_iso16358_helpers.py`
- `tests/test_ui_tk_iso_table_autocalc.py`
- `docs/designs/2026-05-23-tkinter-calculator-final-ux-contract.md`
- `docs/guides/lightweight_calculator_tk_manual_smoke.md`
- `docs/WORK_PLAN.md`
- `result_reports/active/163_tkinter-iso-hk-input-output-ui-correction.md`

## Known Failures / Risks

- Automated Tkinter coverage is green, but macOS manual UX smoke remains the
  next necessary user-visible validation.
- The correction improves structure and spacing only; it deliberately does
  not wire semantic visual tokens or implement further spreadsheet behaviors.
- PyQt retirement still lacks packaging-size and usability evidence.

## Next Suggested Action

Run the updated macOS manual UX smoke guide against `app_calculator_tk.py`,
then decide whether additional Tkinter spacing/style adapter work is needed
before a Windows packaging measurement.

## Scope Compliance

- No calculation/core/profile/dispatcher/schema/region-config modifications
  were made; actual raw keys are only adapted at the UI display boundary.
- No PyQt, Predict/Train, visual-token wiring, existing color, packaging,
  golden/fixture/test-marker, active-document registry, project-log, memory
  seed, or lifecycle files were changed.

## Commit / Push

- Source/docs/tests commit: `b4d746e` (`fix: refine Tkinter ISO input and result UI`).
- Report commit: this report is committed separately after source verification.
- Push: `origin/work/ui-ux-ssot-adoption` after the report commit.

## Project Memory Delta

- type: decision
  topic: tkinter-iso-hk-input-output-ui-correction
  content: "Tkinter ISO Hong Kong calculator UI presents CSPF/HSPF as integrated metric input tables and kWh summary result cards, adapting raw calculator result keys only in the display layer while preserving auto-calc and core calculation paths."
  keywords:
    - Tkinter
    - Hong Kong
    - CSPF
    - HSPF
    - input table
    - result formatting
  assertionStatus: observed
  source: result_reports/active/163_tkinter-iso-hk-input-output-ui-correction.md
