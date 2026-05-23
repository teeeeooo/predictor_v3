# Lightweight Calculator — macOS Tkinter Manual Smoke Checklist

> Companion to
> `docs/designs/2026-05-22-lightweight-calculator-ui-feasibility.md`
> and `docs/guides/lightweight_calculator_packaging_check.md`. This
> document covers **manual GUI verification on macOS** for the
> Tkinter calculator-only MVP. PyInstaller packaging and Windows
> size measurement are out of scope here — see the packaging guide.

## Purpose

Confirm that the Tkinter calculator-only MVP launches, reaches the
ISO 16358 / Hong Kong screen, produces the expected CSPF / HSPF
smoke values, and supports the basic result-panel actions on macOS
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
2. **Single standard tab** — The window shows exactly one tab
   labeled `ISO 16358`. No other top-level tabs (`EN 14825`, `AHRI
   210/240`, `KS C 9306`) appear yet — they are out of scope for the
   MVP.
3. **Region selector** — Inside the ISO 16358 tab, a `지역` combobox
   labeled with `Hong Kong` is visible at the top. The combobox is
   read-only (cannot be edited by typing).
4. **CSPF + HSPF sections together** — Below the region row, both
   `CSPF (Hong Kong)` and `HSPF (Hong Kong)` `LabelFrame` sections are
   visible at the same time in the same screen. `profile_id`,
   `calculator_id`, and `config_path` are not displayed anywhere in
   the UI.
5. **CSPF table default values** — In the single CSPF input table:
   - `정격` / `능력 [W]` = `3500`
   - `35 Full` / `능력 [W]` = `3600`
   - `35 Full` / `전력 [W]` = `900`
   - `35 Half` / `능력 [W]` = `1700`
   - `35 Half` / `전력 [W]` = `380`
   - `정격` / `전력 [W]` is shown as non-editable `-`.
   - No `CSPF 계산` button is shown.
6. **CSPF auto-calc** — Without changing inputs, wait briefly for
   auto-calc. A summary result card should show:
   ```
   CSPF | CSTL [kWh] | CSEC [kWh]
   4.939 | 1769.6 | 358.3
   ```
   No `None` value is visible.
7. **HSPF table default values** — In the single HSPF input table:
   - `정격 난방` / `능력 [W]` = `6300`
   - `7 Full` / `능력 [W]` = `6300`
   - `7 Full` / `전력 [W]` = `1500`
   - `7 Half` / `능력 [W]` = `3200`
   - `7 Half` / `전력 [W]` = `800`
   - `정격 난방` / `전력 [W]` is shown as non-editable `-`.
   - No `HSPF 계산` button is shown.
8. **HSPF auto-calc** — After the initial auto-calc, the result
   panel should contain a second summary card:
   ```
   HSPF | HSTL [kWh] | HSEC [kWh]
   3.643 | 273.2 | 75.0
   ```
   No long raw floating-point value is visible.
9. **Latest result composition** — After steps 6 and 8 both latest
   blocks are visible in the result panel with a blank line between
   them. Edit one valid cell and wait briefly: its metric block
   updates without adding duplicate result history.
10. **Copy result** — Click `결과 복사`. Open a text editor (or any
    text input) outside the app and paste with Cmd+V. The pasted
    text should contain both the `[CSPF]` and `[HSPF]` blocks.
11. **Clear result** — Click `결과 지우기`. The result panel is now
    empty. The window remains responsive.
12. **Region re-selection does not corrupt the tab** — Click the
    region combobox. Re-select `Hong Kong` (currently the only
    option). The CSPF and HSPF sections re-render without
    duplication and auto-calc repopulates the result panel with
    CSPF `4.939` and HSPF `3.643`.
13. **PyQt5 stays unloaded** — Optional verification. With the app
    still running, open a second terminal at the repo root and run:
    ```bash
    python3 -B -c "import ui_tk.calculator_app, sys; \
      print([m for m in sys.modules if m.startswith('PyQt5')])"
    ```
    The printed list must be empty (`[]`). This mirrors the
    `tests/test_ui_tk_calculator_foundation.py::test_pyqt5_not_
    imported_via_ui_tk_calculator_app` assertion.
14. **Clean shutdown** — Close the window via the macOS window close
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
| Result panel buttons | `결과 복사`, `결과 지우기` |

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
- Region selector shows "Hong Kong": OK/NG
- CSPF + HSPF sections together: OK/NG
- CSPF single table defaults / static power cell / no calculate button: OK/NG
- CSPF summary card = 4.939 / 1769.6 / 358.3: OK/NG
- HSPF single table defaults / static power cell / no calculate button: OK/NG
- HSPF summary card = 3.643 / 273.2 / 75.0: OK/NG
- Latest result composition (no duplicate history): OK/NG
- Copy result (Cmd+V paste shows both blocks): OK/NG
- Clear result empties the panel: OK/NG
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
