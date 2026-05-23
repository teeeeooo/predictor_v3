# Design Gate — Tkinter Calculator Final UX Contract

> **Scope note.** This document defines the **final calculator-only UX
> contract** for the Tkinter direction. It does not replace the feasibility
> spike design doc (`docs/designs/2026-05-22-lightweight-calculator-ui-
> feasibility.md`), which remains the authoritative record of the MVP scope
> and decision criteria. This doc is the **next-design-gate** that gates
> whether the Tkinter feasibility foundation evolves into a production-
> candidate calculator-only UI.
>
> This doc inherits the global UI/UX SSOT:
> - `docs/ui_ux/00_UI_UX_SYSTEM.md`
> - `docs/ui_ux/02_DESIGN_TOKENS_AND_LAYOUT.md`
> - `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md`
> - `docs/ui_ux/04_VISUAL_DESIGN_ARCHITECTURE.md`
> - `docs/ui_ux/adapters/TKINTER_TABLE_ADAPTER.md`
>
> It does not redefine calculator core, profile dispatcher, region config,
> unit adapter, or ML.

## Background

The Tkinter calculator-only direction started as a **feasibility spike**
(116~118) to evaluate whether a lightweight, PyQt5-free calculator-only
bundle could be shipped. The spike produced:

- `app_calculator_tk.py` — thin entrypoint (16 LOC).
- `ui_tk/calculator_app.py` — minimal shell (~54 LOC).
- `ui_tk/profile_resolver.py` — pure Python region/metric → `profile_id`.
- `ui_tk/input_widgets.py` — `NumericEntryRow` helper.
- `ui_tk/sections/iso_cspf_section.py` + `iso_hspf_section.py` — Hong Kong
  CSPF / HSPF inputs using `Entry` rows + a **calculate button per section**.
- `ui_tk/sections/iso16358_helpers.py` — pure input-build / result-format
  helpers.

The spike confirmed:
1. No PyQt5 import anywhere in the Tkinter shell.
2. Hong Kong CSPF = **4.939** and HSPF = **3.643** smoke values match the
   PyQt calculator for the same input points.
3. `core/` reuse without modification is possible.
4. `profile_id` / `calculator_id` / `config_path` are not exposed in the UI.

This doc answers: **What does the Tkinter calculator UI look like if the
spike survives and becomes the production calculator-only path?**

## Feasibility MVP vs Final UX

| Dimension | Feasibility MVP (current) | Final UX (this contract) |
| --- | --- | --- |
| Input shape | `NumericEntryRow` (single `Entry` per field) | Editable table/grid with rows = measure points, columns = capacity / power / declared |
| Calculation trigger | Explicit button per section (`CSPF 계산`, `HSPF 계산`) | Auto-calc on every valid input change |
| Result surface | Plain text callback into a shared text panel | Per-section result panel auto-updates; status/error inline |
| Keyboard workflow | Tab navigates between `Entry` widgets | Spreadsheet-like Tab/Enter navigation inside the grid |
| Copy/paste | Not supported | TSV copy/paste candidate for later slice |
| Undo/redo | Not supported | Undo stack candidate for later slice |
| Theme/design system | Tk defaults; no token usage | Follows `00_UI_UX_SYSTEM.md` principles and `02_DESIGN_TOKENS_AND_LAYOUT.md` where applicable |
| Table UX contract | Intentionally out of scope | Follows `03_SPREADSHEET_TABLE_UX_CONTRACT.md` through `adapters/TKINTER_TABLE_ADAPTER.md` |

The MVP intentionally used simpler `Entry`/grid input because the spike's
primary goal was to validate **packaging size delta** and **core reuse**, not
to rebuild the full calculator UX. The MVP succeeded at that goal. The final
UX now rebuilds the input surface to match the PyQt calculator's user-visible
behavior while keeping the PyQt runtime out.

## Final UX Principles

1. **PyQt UX philosophy without PyQt runtime.** The PyQt calculator's
   spreadsheet-like input, auto-calc, and per-tab result panels are the
   reference UX. The Tkinter implementation replicates what the user sees and
   does, using Tkinter widgets and event patterns.
2. **UI/UX SSOT compliance.** All behavior decisions defer to
   `00_UI_UX_SYSTEM.md`. Forbidden patterns (§10), button rules (§4), error
   feedback (§6), and numeric display (§8) apply to Tkinter exactly as they
   apply to PyQt.
3. **No internal identifiers in the UI.** The user sees standards, regions,
   and metric names. `profile_id`, `calculator_id`, and `config_path` are
   resolved internally and never displayed.
4. **Immediate feedback.** Valid input changes trigger recalculation within
   a bounded delay. Invalid or incomplete input shows a status message, not
   a raw exception.
5. **Keyboard-first workflow.** The user can fill inputs, navigate, trigger
   copy/paste, and see results without touching the mouse.

## Information Architecture

The IA is unchanged from the feasibility doc; the final UX only changes the
**widget shape** inside each metric section.

- Top level: **standard tabs** (ISO 16358, EN 14825, AHRI 210/240, KS C 9306,
  …).
- Inside a standard tab: **region selector** (`ttk.Combobox`).
- Region selection drives which **metric sections** are visible together.
  - ISO 16358 / **Hong Kong** → CSPF section + HSPF section in the same
    view.
  - EN 14825 → SEER section + SCOP section together.
  - AHRI 210/240 → SEER2 section + HSPF2 section together.
- Internal resolution: `(region, metric_section)` → `profile_id` via
  `ui_tk/profile_resolver.py`.

Rejected alternatives remain rejected (no per-region tabs, no nested tabs, no
KS C 9306 merged into ISO).

## Table/Grid Input Contract

Each metric section that currently uses `NumericEntryRow` entries is replaced
by a **table-shaped grid**.

### Required in the first vertical slice

- **Editable grid/table form**: rows = measure points (e.g., `35_full`,
  `35_half`), columns = numeric fields (e.g., `capacity [W]`, `power [W]`),
  with a header row labeling each column.
- **Numeric validation**: each editable cell accepts numeric input and rejects
  non-numeric characters or out-of-range values. Invalid cells are visually
  marked (border or background tint) but do not block further editing.
- **`values_changed` signal/callback**: the grid emits a high-level
  "something changed" event after any edit, paste, clear, or undo. This is
  the Tkinter equivalent of `SpreadsheetTableModel.values_changed`.
- **Auto-calc trigger**: the grid's `values_changed` callback is wired to the
  auto-calc helper (see below).
- **Keyboard navigation**:
  - `Tab` → next cell to the right; wrap to next row at end.
  - `Shift+Tab` → previous cell to the left; reverse wrap.
  - `Enter` / `Return` → next cell down; wrap to next column at bottom.
  - `Shift+Enter` → previous cell up; reverse wrap.
  - Arrow keys → one cell in the corresponding direction.

### Deferred to later slices

- **TSV copy/paste** (`Ctrl+C` / `Ctrl+V`): desirable final UX behavior per
  `03_SPREADSHEET_TABLE_UX_CONTRACT.md` §4, but the first vertical slice may
  ship without it to limit scope.
- **Undo/redo** (`Ctrl+Z` / `Ctrl+Y`): desirable per §7, but the first
  vertical slice may ship without it.
- **Multi-cell selection, drag, Shift+click, Ctrl+click**: desirable per §2,
  but the first slice may limit selection to single-cell.

### Explicitly out of scope for final UX (same as MVP)

- Re-implementing the full `QAbstractTableModel` / `QStyledItemDelegate`
  architecture inside Tkinter. The Tkinter grid is a lightweight adapter,
  not a clone of the PyQt model/view stack.

## Auto-calc Contract

### Required

- **No calculate button**: the primary action is automatic. There is no
  per-section "계산" button in the final UX.
- **Debounce or idle scheduling**: after a valid `values_changed` event, the
  tab schedules recalculation on a short delay (e.g., 150–300 ms) or on the
  next idle event-loop tick. Multiple rapid edits coalesce into one compute.
- **Insufficient/invalid input handling**: when required cells are empty or
  invalid, the result panel shows a concise status message (e.g.,
  "입력을 확인하세요") instead of a stack trace or a silent blank.
- **Exception surfacing**: core calculator exceptions are caught by the UI
  shell, logged if a log path exists, and rendered as a short user-facing
  error in the result/status area. Stack traces are never shown to the user
  (`00_UI_UX_SYSTEM.md` §10).

### Alignment with PyQt action model

This contract is the Tkinter equivalent of the PyQt **Option A — Auto-calc
unified** decision (`docs/designs/2026-05-22-calculator-action-model-
alignment.md`). The PyQt calculator's `계산 실행` button is removed/demoted;
the Tkinter calculator never introduces one.

## Result Surface Contract

- **Per-section result panel**: each metric section (CSPF, HSPF, SEER, SCOP,
  SEER2, HSPF2) owns its own read-only result/status panel inside the same
  view. Results update automatically when auto-calc fires.
- **Result content**: primary metric value (e.g., `CSPF = 4.939`) plus a small
  set of intermediate values drawn from the calculator result dict, matching
  the PyQt ISO result panel shape.
- **Status banner**: a small label below the result panel shows "계산 완료",
  "입력 부족", or a short error message. It is never a modal popup for
  routine validation errors.
- **Copy affordance**: either a "Copy result" button or native text-widget
  selection + `Ctrl+C` copies the result text to the clipboard.

## Non-goals

- Replacing `app_calculator.py` / `ui/calc_window.py` or retiring PyQt
  calculator source in this doc. (Retirement is gated on Tkinter final UX
  vertical slice verification; see *Retirement Dependency*.)
- Rebuilding the full PyQt `SpreadsheetTableModel` / `SpreadsheetTableView`
  architecture inside Tkinter.
- Adding AHRI, EN, or KS tabs in the first vertical slice. The slice stays
  ISO 16358 / Hong Kong only.
- ML / inverse-search integration.
- Packaging optimization (UPX, exclude-modules). Size measurement uses the
  default PyInstaller baseline.
- TSV copy/paste, undo/redo, or multi-cell selection in the first vertical
  slice. They are deferred follow-ups, not rejected.

## Implementation Slices

Ordered. Each slice ships independently with its own report.

1. **Tkinter table/grid input foundation**
   - Added the reusable pure model `ui_tk/table_grid_model.py` and Tkinter
     Entry-grid adapter `ui_tk/table_grid.py` for schema, numeric validation,
     and a high-level `values_changed` callback.
   - This foundation remains alongside `NumericEntryRow`; ISO section
     replacement and calculator wiring are deferred to slice 3.
   - Verification: model/adapter tests plus existing Tkinter foundation smoke;
     no calculator behavior is changed in this slice.

2. **Tkinter auto-calc debounce/helper foundation**
   - Completed as part of slice 3 in `ui_tk/auto_calc.py` with the small
     Tkinter `after`-based `DebouncedAutoCalc` helper.
   - It subscribes to grid `values_changed` callbacks without owning
     calculator or result-formatting logic.
   - Verification: callback scheduling, flush, cancellation, and disposal
     tests.

3. **ISO Hong Kong CSPF/HSPF table + auto-calc vertical slice**
   - Completed in task 162: `IsoCspfSection` and `IsoHspfSection` now use
     `TableGrid` inputs and contain no per-section calculate buttons.
   - Both metrics calculate automatically after valid changes; initial Hong
     Kong defaults show CSPF `4.939` and HSPF `3.643`.
   - The shared result panel displays the latest result for each metric
     instead of appending duplicate auto-calc history.
   - Verification: automated vertical-slice tests + full pytest baseline;
     manual smoke remains slice 4.

4. **macOS manual UX smoke**
   - Run the 14-item manual smoke checklist from
     `docs/guides/lightweight_calculator_tk_manual_smoke.md` against the
     slice-3 build.
   - Record OK/NG for each item.
   - If any item fails, fix in a follow-up slice before proceeding.

5. **Windows PyInstaller size measurement**
   - Measure one-folder and one-file `.exe` sizes for `app_calculator_tk.py`
     on a Windows host using the commands in
     `docs/guides/lightweight_calculator_packaging_check.md`.
   - Compare against the PyQt5 baseline (recorded or newly measured).
   - If the delta is < 20 %, pause and re-evaluate the Tkinter direction.
   - If the delta is ≥ 40 %, continue.
   - **Prerequisite:** Windows host available.

6. **PyQt calculator-only source retirement — 재개**
   - Only after slice 3 (vertical slice) is verified and slice 5 (size) meets
     the continue criteria.
   - Resume the retirement sequence from reports 154~156:
     - S1 mixed ISO table test split or retirement.
     - S3 PyQt calculator-only source retirement.
     - S4 active docs update.
     - S5 support matrix guide narrowing.

7. **Tkinter standard/region expansion**
   - Add EN 14825, AHRI 210/240, KS C 9306 tabs using the same grid + auto-
     calc pattern.
   - Reuse `ui_tk/profile_resolver.py` and the slice-1 grid widget.
   - Each new tab/region is its own small slice.

## Retirement Dependency

**PyQt calculator-only source retirement remains on hold after the Tkinter
vertical slice, pending Windows packaging size measurement or an explicit
usability decision.**

- The PyQt calculator (`app_calculator.py`, `ui/calc_window.py`, and related
  modules) remains the **reference UX and reference source** until the Tkinter
  implementation demonstrates equivalent user-visible behavior.
- Reports 154~156 identified the retirement candidates and ordered the slices.
  Task 162 satisfies the Hong Kong vertical-slice prerequisite but does not
  authorize S3 (source retirement).
- If slice 3 fails or slice 5 shows insufficient size benefit, the Tkinter
  direction falls back and the PyQt calculator UI workstream resumes from
  the held slices (ε → ζ → η → β → γ → δ) as originally planned.

## Verification Strategy

- **Unit/grid**: tests for the reusable grid widget (numeric validation,
  `values_changed` callback, keyboard navigation) without Tkinter event-loop
  timing where possible.
- **Helper**: pure tests for `iso16358_helpers.py` and `profile_resolver.py`
  already exist; they remain unchanged.
- **Smoke**: manual macOS checklist for the full app; automated import/smoke
  for `app_calculator_tk.py`.
- **Baseline**: full pytest suite must not regress. Pre-slice-3 baseline:
  `622 passed, 32 skipped, 19 xfailed`.
- **Structure guard**: `python3 -B tools/check_code_structure.py` must stay
  green for every slice.

## Status

- **Feasibility MVP**: completed (118, 130).
- **Final UX contract**: defined in this doc.
- **Table/grid foundation**: completed in
  `ui_tk/table_grid_model.py` and `ui_tk/table_grid.py`; wired to the Hong
  Kong ISO CSPF/HSPF vertical slice in task 162.
- **Auto-calc vertical slice**: completed in task 162 using
  `ui_tk/auto_calc.py`, with button-free CSPF/HSPF inputs and latest-result
  composition.
- **Next action**: Implementation slice 4 — macOS manual UX smoke.
- **PyQt retirement**: held pending Windows packaging size measurement or an
  explicit usability decision.
