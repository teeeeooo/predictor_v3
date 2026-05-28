# Lightweight Calculator — macOS Tkinter Manual Smoke Checklist

> Companion to
> `docs/designs/2026-05-22-lightweight-calculator-ui-feasibility.md`
> and `docs/guides/lightweight_calculator_packaging_check.md`. This
> document covers **manual GUI verification on macOS** for the
> Tkinter calculator-only MVP. PyInstaller packaging and Windows
> size measurement are out of scope here — see the packaging guide.
> The input-matrix and summary-result checks below exercise the first
> concrete application of
> `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md`, including the
> task-166 bordered matrix/result visible-surface refinement and task-168
> ISO Hong Kong layout correction, followed by task-169 alignment and
> task-170 responsive table architecture refinement.

## Purpose

Confirm that the Tkinter calculator-only MVP launches, reaches the
ISO 16358 / Hong Kong screen, produces the expected CSPF / HSPF
smoke values, and renders corrected section-local result surfaces on macOS
**before** spending Windows-host time on a PyInstaller measurement
run. The checklist captures a small, repeatable manual pass so the
Tkinter direction has a verified behaviour baseline.

## Scope

- Manual GUI verification on macOS only.
- Targets the current Tkinter MVP: `app_calculator_tk.py` →
  `ui_tk.calculator_app.CalculatorTkApp` → `ui_tk.tabs.iso16358_tab.
  Iso16358Tab` with Hong Kong CSPF / HSPF sections (118 clean
  foundation reset).
- Pre-launch static checks (compile, structure guard, targeted
  pytest) included as optional commands.

## Non-goals

- PyInstaller `.exe` / one-folder dist build (Windows guide
  `docs/guides/lightweight_calculator_packaging_check.md`).
- Windows-specific verification.
- Automated GUI / screenshot / pixel-perfect tests.
- Graph/detail surface verification; that is a later lightweight design phase,
  not part of this summary-surface smoke.
- New helper scripts under `tools/` or `scripts/`.
- Touching the PyQt calculator UI (`app_calculator.py`,
  `ui/calc_window.py`, etc.).
- Resolving the macOS Python 3.14 + PyQt5 fatal-abort issue in 4
  PyQt clipboard / table tests (tracked separately; see Known
  Issue Separation below).

## Environment

Run on a macOS host. Tested locally with the following setup; other
combinations are acceptable as long as Tkinter loads and the
calculator core tests pass.

- macOS Darwin
- Python: `/Library/Frameworks/Python.framework/Versions/3.14/bin/python3`
  (Python 3.14.x). Other Python 3.10+ versions are fine.
- Tkinter / Tcl/Tk: bundled with the Python.org installer.
- No PyQt5 dependency for the Tkinter path (PyQt5 may still be
  installed for the PyQt UI but must not be loaded by
  `app_calculator_tk.py`).

Verify the Python interpreter from the repo root:

```bash
python3 -V
python3 -c "import tkinter; print('Tcl/Tk', tkinter.TclVersion, tkinter.TkVersion)"
```

## Before you start (optional static checks)

These commands are static — no GUI. They are not strictly required
for the manual smoke but catch obvious regressions in seconds.

```bash
# 1. Byte-compile every Tkinter MVP module.
python3 -B -m py_compile \
  app_calculator_tk.py \
  ui_tk/__init__.py \
  ui_tk/calculator_app.py \
  ui_tk/profile_resolver.py \
  ui_tk/result_panel.py \
  ui_tk/input_widgets.py \
  ui_tk/tabs/__init__.py \
  ui_tk/tabs/iso16358_tab.py \
  ui_tk/sections/__init__.py \
  ui_tk/sections/iso_cspf_section.py \
  ui_tk/sections/iso_hspf_section.py

# 2. Layer-boundary structure guard.
python3 -B tools/check_code_structure.py

# 3. Targeted pytest covering the Tkinter foundation and the
#    calculator profile / dispatcher / schema boundary it depends on.
python3 -B -m pytest -q \
  tests/test_ui_tk_profile_resolver.py \
  tests/test_ui_tk_calculator_foundation.py \
  tests/test_calculator_schema_boundaries.py \
  tests/test_calculator_profiles.py \
  tests/test_calculator_dispatcher.py
```

Expected (current branch):

- `py_compile`: silent success.
- structure guard: `code structure guard: OK (no findings)`.
- pytest: `58 passed`.

## Launch command

From the repo root:

```bash
python3 -B app_calculator_tk.py
```

A Tk window titled `Calculator (Tkinter)` should appear. No
terminal output is expected on the happy path.

## Manual checklist

Default inputs are pre-filled by `ui_tk/sections/iso_cspf_section.py`
and `ui_tk/sections/iso_hspf_section.py`. Run each step in order
without changing inputs unless the step says so.

1. **App launch** — Run the launch command. Confirm the Tk window
   appears with the title `Calculator (Tkinter)`.
   Confirm the window appears near the screen center, or at least fully
   inside the visible screen with the title bar reachable.
2. **Single standard tab** — The window shows exactly one tab
   labeled `ISO 16358`. No other top-level tabs (`EN 14825`, `AHRI
   210/240`, `KS C 9306`) appear yet — they are out of scope for the
   MVP.
3. **Region selector** — Inside the ISO 16358 tab, a `지역` combobox
   labeled with `Hong Kong` is visible at the top. The combobox is
   read-only (cannot be edited by typing).
4. **CSPF + HSPF sections together** — Below the region row, both
   `CSPF 입력 (Hong Kong)` and `HSPF 입력 (Hong Kong)` sections are visible
   at the same time. Within the page the visible order is `CSPF 입력` →
   `CSPF 결과` → `HSPF 입력` → `HSPF 결과`. `profile_id`,
   `calculator_id`, and `config_path` are not displayed anywhere in
   the UI.
5. **CSPF table default values** — In the CSPF input section:
   - A separate compact `정격 표기치` surface contains `능력 [W]` = `3500`
     only; it contains no `전력 [W]` row or cell.
   - The trial-input matrix has only `35 Full` and `35 Half` columns, with
     `능력 [W]` and `전력 [W]` rows.
   - `35 Full` / `능력 [W]` = `3600`
   - `35 Full` / `전력 [W]` = `900`
   - `35 Half` / `능력 [W]` = `1700`
   - `35 Half` / `전력 [W]` = `380`
   - Cells appear as compact bordered matrices and numeric values are centered.
   - The `정격 표기치`, trial-input, and CSPF result tables have the same
     left edge and visual width with regular vertical spacing.
   - Resize the window wider: all three surfaces expand together while
     preserving their common left edge and width alignment.
   - Numeric/header text is comfortably readable and row padding remains
     compact rather than oversized.
   - No `CSPF 계산` button is shown.
6. **CSPF auto-calc** — Without changing inputs, wait briefly for
   auto-calc. A compact bordered result table should show a distinct header
   row, value row, and small status line:
   ```
   CSPF | CSTL [kWh] | CSEC [kWh]
   4.939 | 1769.6 | 358.3
   ```
   No `None` value is visible.
7. **HSPF table default values** — In the HSPF input section:
   - A separate compact `정격 표기치` surface contains `능력 [W]` = `6300`
     only; it contains no `전력 [W]` row or cell.
   - The trial-input matrix has only `7 Full` and `7 Half` columns, with
     `능력 [W]` and `전력 [W]` rows.
   - `7 Full` / `능력 [W]` = `6300`
   - `7 Full` / `전력 [W]` = `1500`
   - `7 Half` / `능력 [W]` = `3200`
   - `7 Half` / `전력 [W]` = `800`
   - Numeric values are centered in the bordered cells.
   - The `정격 표기치`, trial-input, and HSPF result tables have the same
     left edge and visual width with the same spacing rhythm as CSPF.
   - After resizing, these three surfaces expand together and remain aligned.
   - No `HSPF 계산` button is shown.
8. **HSPF auto-calc** — After the initial auto-calc, the result
   surface directly below HSPF input should contain a compact bordered table:
   ```
   HSPF | HSTL [kWh] | HSEC [kWh]
   3.643 | 273.2 | 75.0
   ```
   No long raw floating-point value is visible.
9. **Excel-like input interactions** — In a CSPF or HSPF trial-input table:
   - Click one cell, then Shift-click or drag to select a rectangular range.
   - Copy the selected range and paste it into a plain-text editor; the
     contents are TSV in the visible row/column order.
   - Paste a rectangular numeric TSV block into the selected anchor and
     verify all affected cells update together.
   - Paste a block containing a non-number and verify none of its cells are
     applied.
   - Press Delete or Backspace on a range, then undo once; all cleared cells
     restore together.
   - Use Tab / Shift+Tab and Enter / Shift+Enter to move through cells.
   - **Click a populated cell: the cell highlights but no typing caret is
     visible** (Excel-like selection mode, not immediate edit mode).
   - **While in selection mode, press Left/Right/Up/Down arrow keys to move
     the active cell** without leaving the table boundary.
   - **Press keypad Enter (KP_Enter) to move down like Return.**
   - **Press Esc; the active highlight disappears immediately.**
   - **Click a blank area inside the table frame (header, row header,
     static cell, or empty space between cells); the active highlight
     disappears. The clickable blank area should be the entire table surface,
     not just a 1-pixel gap.**
   - **Click another table/card cell; the previous table's active highlight
     disappears and editable cells return to their default background.**
   - **While in edit mode, change a value and click another table/card cell;
     the changed value commits instead of restoring the pre-edit value.**
   - **macOS: Command+C, Command+V, and Command+Z work the same as
     Ctrl+C/V/Z.**
   - **After moving with Tab/Enter/arrow, type a digit; the prior value is
     replaced rather than appended.**
   - **Once typing has started in a cell, subsequent keystrokes append
     naturally.**
   - **After the first click selects a populated cell, type a digit and
     confirm the whole existing cell value is replaced.**
   - **Click the same already-selected cell again; a visible caret appears
     and typing appends/inserts without clearing the existing value.**
   - **Double-click a populated cell and press F2 on a selected populated
     cell; each path shows a visible caret and preserves the existing value.**
   - **In edit mode, Arrow/Delete/Backspace edit text within the existing
     value rather than navigating or clearing the whole cell.**
   - **In selection mode, Arrow moves the active cell and
     Delete/Backspace clears the selected editable cell(s), with no caret.**
   - **In edit mode, press Enter/Tab/KP_Enter and confirm the edit commits
     before navigation.**
   - **In edit mode, press Esc and confirm the in-progress text edit is
     cancelled while the cell remains selected; in selection mode, press Esc
     and confirm the selection visual clears.**
   - **In edit mode, move focus outside the table and confirm the edited
     value commits before the selection visual clears.**
10. **Latest result composition** — Edit one valid CSPF cell and wait briefly:
   only the CSPF result surface updates; it does not add duplicate result
   history or replace the HSPF result surface.
11. **Invalid input surface** — Type a non-number in one CSPF trial cell.
    The CSPF result changes to a clear input-error status line only. No gray
    header/value block, `None`, raw dictionary, long float, or traceback is
    displayed. Restore the default value and verify the normal summary returns.
12. **No bottom result actions** — There is no shared bottom result region and
    no visible `결과 복사` or `결과 지우기` button.
13. **Region re-selection does not corrupt the tab** — Click the
    region combobox. Re-select `Hong Kong` (currently the only
    option). The CSPF and HSPF sections re-render without
    duplication and auto-calc repopulates the result panel with
    CSPF `4.939` and HSPF `3.643`.
14. **PyQt5 stays unloaded** — Optional verification. With the app
    still running, open a second terminal at the repo root and run:
    ```bash
    python3 -B -c "import ui_tk.calculator_app, sys; \
      print([m for m in sys.modules if m.startswith('PyQt5')])"
    ```
    The printed list must be empty (`[]`). This mirrors the
    `tests/test_ui_tk_calculator_foundation.py::test_pyqt5_not_
    imported_via_ui_tk_calculator_app` assertion.
15. **Clean shutdown** — Close the window via the macOS window close
    button. The Python process exits with no error.

## Expected values

| Item | Expected |
| --- | --- |
| Hong Kong CSPF (defaults) | **4.939** |
| Hong Kong HSPF (defaults) | **3.643** |
| CSPF summary seasonal values | CSTL `1769.6 kWh`, CSEC `358.3 kWh` |
| HSPF summary seasonal values | HSTL `273.2 kWh`, HSEC `75.0 kWh` |
| Top-level tabs | exactly 1 (`ISO 16358`) |
| Hong Kong metric sections | CSPF and HSPF, same screen |
| `profile_id` exposed in UI | NO |
| PyQt5 loaded into `sys.modules` | NO |
| Window title | `Calculator (Tkinter)` |
| Result panel buttons | none |

These are the same values exercised by the automated tests
`test_hong_kong_cspf_smoke_via_resolver` and
`test_hong_kong_hspf_smoke_via_resolver` in
`tests/test_ui_tk_calculator_foundation.py`; the manual checklist
covers the user-facing path that the unit tests cannot reach.

## Pass / Fail recording format

Copy this block into the run notes / report; mark each step
`OK` or `NG` and add a one-line cause for any `NG`.

```
- App launch: OK/NG
- Single ISO 16358 tab: OK/NG
- Initial window appears centered or fully inside visible screen: OK/NG
- Region selector shows "Hong Kong": OK/NG
- CSPF + HSPF sections together: OK/NG
- CSPF separate rated surface / trial matrix / centered values / defaults: OK/NG
- CSPF rated / trial / result left edge, width, and spacing alignment: OK/NG
- CSPF responsive resize / readable font / compact row density: OK/NG
- CSPF compact result table = 4.939 / 1769.6 / 358.3: OK/NG
- HSPF separate rated surface / trial matrix / centered values / defaults: OK/NG
- HSPF rated / trial / result left edge, width, and spacing alignment: OK/NG
- HSPF responsive resize / readable font / compact row density: OK/NG
- HSPF compact result table = 3.643 / 273.2 / 75.0: OK/NG
- Rectangular select / TSV copy and numeric paste: OK/NG
- Invalid TSV paste leaves all cells unchanged: OK/NG
- Delete/Backspace grouped clear and single undo restore: OK/NG
- Tab/Enter navigation: OK/NG
- Click selection hides caret until first key: OK/NG
- Arrow key moves active cell in selection mode: OK/NG
- Keypad Enter navigates like Return: OK/NG
- Esc clears selection visual: OK/NG
- Blank area (header/row header/static/gap) click clears selection: OK/NG
- Other table/card cell click clears previous selection: OK/NG
- Edit mode then other table/card cell click commits value: OK/NG
- macOS Command+C/V/Z shortcut works: OK/NG
- Tab/Enter/arrow then type replaces existing value: OK/NG
- First click then printable key replaces whole cell: OK/NG
- Same selected cell second click enters edit mode without clearing value: OK/NG
- Double click enters edit mode without clearing value: OK/NG
- F2 enters edit mode without clearing value: OK/NG
- Edit mode shows caret and printable keys append/insert text: OK/NG
- Edit mode Arrow/Delete/Backspace edits text: OK/NG
- Edit mode Enter/Tab/KP_Enter commits before navigation: OK/NG
- Selection mode Arrow moves cell and Delete/Backspace clears cell: OK/NG
- Edit mode Esc cancels edit; selection mode Esc clears selection: OK/NG
- Edit mode focus-out commits value: OK/NG
- Latest section-local result update (no duplicate history): OK/NG
- Invalid input renders status only without gray block/raw output: OK/NG
- No bottom copy/clear result buttons: OK/NG
- Region re-selection re-renders cleanly: OK/NG
- PyQt5 not imported: OK/NG
- Clean shutdown: OK/NG
```

A run with all `OK` is sufficient to call the macOS manual smoke
pass. Any `NG` should be filed as a follow-up before the Windows
PyInstaller measurement starts — a regression here would invalidate
that baseline measurement.

## Known macOS / PyQt issue separation

This checklist is **independent of** the macOS + Python 3.14 + PyQt5
fatal-abort behaviour observed in the following PyQt clipboard /
table tests:

- `tests/test_iso16358_result_table_copy_tsv.py`
- `tests/test_iso16358_table_excel_like_behavior.py`
- `tests/test_app_calculator_ui_smoke.py`
- `tests/test_spreadsheet_table_view.py`

Those tests exercise the PyQt calculator UI (`ui/calc_window.py` and
friends) and crash on the current macOS + PyQt5 combination. The
Tkinter MVP does not import PyQt5 and is not affected. Do not try to
resolve the PyQt crash as part of this checklist; the PyQt
calculator UI workstream is on hold (see WORK_PLAN 4c–4g and the
4z pivot note).

## Next step after passing

Once every checklist item is `OK` on macOS:

1. If a Windows host is available — proceed to
   `docs/guides/lightweight_calculator_packaging_check.md` and
   record measured PyInstaller dist sizes for both
   `app_calculator.py` (PyQt baseline) and `app_calculator_tk.py`
   (Tkinter spike). The macOS smoke output gives you a behavioural
   baseline to compare against the Windows build's runtime output.
2. If no Windows host is available — Windows PyInstaller size
   measurement stays **pending**. Keep the macOS smoke result handy;
   the next eligible work items are listed in `docs/WORK_PLAN.md`
   item 4z.

Do not retroactively edit the design doc
(`docs/designs/2026-05-22-lightweight-calculator-ui-feasibility.md`)
to record the smoke result; record it in the run's result report
instead so the design doc keeps describing the *intent*.
