# Lightweight Calculator Packaging Size Check

> Companion to
> `docs/designs/2026-05-22-lightweight-calculator-ui-feasibility.md`.
> This guide documents the **measurement procedure**. It does NOT
> claim measured sizes. Any number that has not been observed locally
> stays labeled `not measured`.
>
> Current project note: Windows calculator packaged size has been
> observed at approximately 11 MB and is acceptable for the current
> deployment candidate; see the active 198-c report for the closeout.

## Purpose

Compare PyInstaller bundle size for:

- **Baseline**: `app_calculator.py` (PyQt5 calculator UI shell).
- **Current Tkinter source**: `app_calculator.py` (canonical wrapper).

The PyQt baseline commands below are retained as historical measurement
provenance. Current calculator packaging must use the canonical Tkinter source.

The comparison answers the *Decision criteria* section of the
feasibility design doc.

## Target platform

Windows is the production deployment target. Run the measurement on a
Windows host with the same Python interpreter version used for both
builds, in a deployment-only virtual environment (`venv_deploy` or
equivalent — see `docs/PACKAGING.md`). macOS / Linux measurements are
informational only.

## Build commands

Run each build from the repo root in a clean deployment venv.

### Baseline — PyQt calculator (one-folder dist)

```cmd
python -m pip install --upgrade pyinstaller pyqt5
pyinstaller --noconfirm --clean --noconsole --name app_calculator_pyqt ^
    --add-data "data;data" ^
    app_calculator.py
```

### Baseline — PyQt calculator (one-file exe)

```cmd
pyinstaller --noconfirm --clean --noconsole --onefile ^
    --name app_calculator_pyqt_onefile ^
    --add-data "data;data" ^
    app_calculator.py
```

### Spike — Tkinter calculator (one-folder dist)

```cmd
python -m pip install --upgrade pyinstaller
pyinstaller --noconfirm --clean --noconsole --name app_calculator ^
    --add-data "data;data" ^
    app_calculator.py
```

`pyqt5` does **not** need to be installed in the Tkinter venv. If it
is installed, PyInstaller may still discover and bundle it through
some indirect import path; verify the resulting `dist/` directory
does not contain `PyQt5` / `Qt5*.dll` after the spike build.

### Spike — Tkinter calculator (one-file exe)

```cmd
pyinstaller --noconfirm --clean --noconsole --onefile ^
    --name app_calculator_onefile ^
    --add-data "data;data" ^
    app_calculator.py
```

Notes:

- `--noconsole` matches the deployment shape (no terminal window).
- `--add-data "data;data"` ships `data/region_configs/*.json` so
  profile config paths resolve at runtime.
- `--clean` discards previous PyInstaller caches; required for
  apples-to-apples comparison.
- Avoid `--upx-dir` for the first measurement; UPX changes both
  bundles equally and adds noise to the baseline. UPX is an
  optimization step, not a baseline.

## One-folder dist size measurement

Run from the repo root after the build completes.

### Windows (PowerShell)

```powershell
Get-ChildItem -Path dist\app_calculator_pyqt -Recurse |
    Measure-Object -Property Length -Sum |
    Select-Object @{Name="MB";Expression={[math]::Round($_.Sum / 1MB, 1)}}

Get-ChildItem -Path dist\app_calculator -Recurse |
    Measure-Object -Property Length -Sum |
    Select-Object @{Name="MB";Expression={[math]::Round($_.Sum / 1MB, 1)}}
```

### Windows (cmd / git bash via `du`)

```bash
du -sh dist/app_calculator_pyqt
du -sh dist/app_calculator
```

### macOS / Linux (informational only)

```bash
du -sh dist/app_calculator_pyqt dist/app_calculator
```

## One-file exe size measurement

```powershell
(Get-Item dist\app_calculator_pyqt_onefile.exe).Length / 1MB
(Get-Item dist\app_calculator_onefile.exe).Length / 1MB
```

```bash
ls -lh dist/app_calculator_pyqt_onefile.exe dist/app_calculator_onefile.exe
```

## Windows-specific verification checklist

After each build:

1. `dist\<name>\` exists and the entry `.exe` launches with double
   click from File Explorer (matches the deployment story for general
   users).
2. The bundle correctly loads `data/region_configs/hong_kong.json`
   (open the app, run a CSPF calculation, confirm
   `CSPF ≈ 4.939` for `35_full = (3600, 900)` /
   `35_half = (1700, 380)` / `declared = 3500`).
3. For the Tkinter bundle: confirm `dist/app_calculator/`
   contains `tcl86*.dll` / `tk86*.dll` and a `tcl/` script folder.
   Absence of those means Tk will fail at runtime on a clean host.
4. For the Tkinter bundle: confirm `dist/app_calculator/` does
   **not** contain `PyQt5`, `Qt5Core.dll`, `Qt5Gui.dll`,
   `Qt5Widgets.dll`, or a `PyQt5/Qt5/plugins/` tree.
5. For the PyQt bundle: capture (with `dir`/`du`) which top-level
   subfolders contribute most of the size, so the comparison report
   can name the dominant DLLs.

## Comparison criteria

The full decision matrix lives in the design doc's
*Decision criteria* section. Short form:

- **Continue Tkinter**: Tkinter one-folder dist ≥ 40 % smaller than
  PyQt baseline on the **same** Windows host.
- **Pause / re-evaluate**: shrink is < 20 % OR the Tkinter MVP
  needs to duplicate non-trivial input parsing/normalization logic
  from `ui/`.
- **Fall back**: Tkinter packaging does not shrink meaningfully, OR
  PyInstaller's bundled Tcl/Tk fails to load on a clean Windows
  host.

Fallback order: CLI / `argparse` over the dispatcher → local HTML
(Flask + browser) → stay on PyQt5 and resume Slice ζ.

## Reporting protocol

When this guide is exercised:

1. Record measured sizes for both baseline and spike, **both**
   one-folder dist and one-file exe.
2. Record Windows version, Python version, PyInstaller version,
   PyQt5 version.
3. Record whether `Qt5*.dll` / `PyQt5/` is present in the Tkinter
   bundle (must be absent) and whether `tcl*.dll` / `tk*.dll` is
   present (must be present).
4. Land the numbers in the report associated with the build run.
   Do **not** retroactively edit the feasibility design doc; instead
   write a follow-up decision report that references the measured
   numbers.

If a build run is skipped (no Windows host available, etc.):

- Record `not measured` for every size column.
- Do not estimate a number into the report.

## Out of scope here

- PyInstaller `.spec` authoring beyond the one-line command above.
- UPX / `--exclude-module` optimization. These are follow-up
  decisions after the baseline measurement.
- Code signing, MSI / NSIS installer wrapping, auto-update channels.
- Crash-logging plumbing differences between the PyQt and Tkinter
  shells.
- Train / Predict app packaging (separate workstream).
