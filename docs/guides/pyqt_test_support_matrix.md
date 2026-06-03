# PyQt Test Support Matrix

## Purpose

Document when the repository's PyQt widget tests should run, when they
are skipped, and which host combinations still need validation. This is
an environment policy for tests only; it does not restart or remove the
PyQt calculator UI workstream.

## Scope

This guide covers PyQt widget tests that create `QApplication`,
`QTableView` subclasses, clipboard paths, key events, or existing PyQt
calculator windows.

It does not cover Tkinter calculator tests, core calculator tests,
packaging measurements, or PyQt troubleshooting beyond the known native
abort environment recorded in reports 128 and 129.

## Current Baseline

Current macOS local baseline after the known-bad environment skip patch:

```bash
python3 -B -m pytest -q -rxXs
```

Expected current result:

```text
585 passed, 59 skipped, 19 xfailed
```

The full suite no longer requires manual `--ignore` entries for the
four PyQt widget test files on the known-bad macOS Python 3.14 host.

## PyQt Test Groups

| Test file | Purpose |
| --- | --- |
| `tests/test_iso16358_result_table_copy_tsv.py` | ISO16358 read-only result/trace table Ctrl+C TSV copy behavior. |
| `tests/test_iso16358_table_excel_like_behavior.py` | ISO16358 input table Excel-like copy, clear, undo, navigation, and invalid-cell display behavior. |
| `tests/test_app_calculator_ui_smoke.py` | Existing PyQt calculator window smoke, profile selection, and table wiring. |
| `tests/test_spreadsheet_table_view.py` | Shared `SpreadsheetTableView` copy/paste/clear/undo/navigation behavior. |

These tests are kept because PyQt table UX, Predict/Train UI assets,
and existing PyQt calculator assets still have regression value. The
Tkinter calculator-only direction and PyQt test support policy are
separate decisions.

## Known-Bad Environment

Known bad:

- macOS arm64
- Python 3.14.x
- PyQt5/Qt installed

Observed local tuple:

- macOS 15.7.3 arm64
- Python 3.14.4
- PyQt5 5.15.11
- Qt 5.15.14

Observed behavior:

- PyQt5 import succeeds.
- Offscreen `QApplication` creation succeeds.
- Plain `QTableView` creation can succeed.
- In pytest context, `QTableView` subclass construction can native
  abort with SIGABRT before Python can raise a normal exception.

The skip guard exists to prevent this native abort before risky widget
construction.

## Supported / Pending / Skipped Host Matrix

| Host | Policy | Notes |
| --- | --- | --- |
| macOS arm64 + Python 3.14.x + PyQt5 | skipped | Known-bad. PyQt widget tests are skipped by `tests.helpers.pyqt_env.macos_python314_pyqt5_known_bad_skip_mark()`. |
| macOS + Python 3.12/3.11 + PyQt5 | pending validation | Should be tested in a dedicated venv before being treated as supported. |
| Windows + Python 3.12/3.11 + PyQt5 | pending validation / preferred future validation host | Good candidate for future PyQt and packaging-host checks, but not yet verified by this guide. |
| Linux + Python 3.14 + PyQt5 | not classified as known-bad | The current guard does not skip Linux. Run the PyQt tests if a Qt-capable host is available. |
| No PyQt5 installed | skipped | Existing `pytest.importorskip("PyQt5")` behavior applies. |
| Tkinter-only paths | unaffected | Tkinter tests and app paths do not depend on PyQt5 and are not controlled by this policy. |

Python 3.15+ is not skipped by the current guard. Extend the guard only
after a separate audit confirms the same native abort risk.

## Local Test Commands

Run the guard tests:

```bash
python3 -B -m pytest tests/test_pyqt_environment_guard.py -q
```

Run the PyQt widget tests directly:

```bash
python3 -B -m pytest \
  tests/test_iso16358_result_table_copy_tsv.py \
  tests/test_iso16358_table_excel_like_behavior.py \
  tests/test_app_calculator_ui_smoke.py \
  tests/test_spreadsheet_table_view.py \
  -q -rs
```

On the known-bad macOS Python 3.14 environment, this should report
skips rather than aborting the Python process.

Run the full suite without manual PyQt ignores:

```bash
python3 -B -m pytest -q -rxXs
```

## How To Interpret Skipped PyQt Tests

A skip with a reason like:

```text
known-bad PyQt widget test environment: Darwin Python 3.14.4 PyQt5 5.15.11 Qt 5.15.14 can native-abort during pytest QTableView subclass construction
```

means the host matches the known-bad environment policy. It does not
mean the PyQt tests are deleted, retired, or considered unimportant.

If PyQt5 is not installed, skips come from the existing
`pytest.importorskip("PyQt5")` policy.

## When To Revalidate

Revalidate PyQt widget tests when:

- A Python 3.12 or 3.11 venv with PyQt5 is available.
- A Windows host with PyQt5 is available.
- PyQt5 / Qt versions change.
- Python 3.15+ becomes part of local or supported test usage.
- PyQt table widgets, clipboard behavior, or calculator window wiring
  are modified.

## Non-Goals

- Do not delete PyQt widget tests because the calculator-only direction
  currently uses Tkinter.
- Do not claim Python 3.12/3.11 or Windows support until those hosts are
  actually tested.
- Do not use this guide as a PyInstaller measurement record.
- Do not use this guide to modify skip conditions, xfail markers,
  expected values, fixtures, or PyQt UI code.
