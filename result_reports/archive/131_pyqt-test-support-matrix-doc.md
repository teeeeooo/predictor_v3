# 131 PyQt Test Support Matrix Doc

## Goal

Document the PyQt widget test support/skip policy so future local and supported-host runs know when PyQt tests should execute, when they should skip, and which environments still need validation.

## Scope

- `docs/guides/pyqt_test_support_matrix.md`
- `docs/WORK_PLAN.md`
- Existing context from reports 128, 129, and 130.

## Non-Goals

- Modify code, tests, skip markers, PyQt helpers, PyQt UI code, Tkinter code, xfail markers, expected values, fixtures, core calculator code, profile/dispatcher code, CI, devcontainer, or PyInstaller behavior.
- Claim Python 3.12/3.11 or Windows PyQt validation has completed.
- Perform result report lifecycle maintenance or move active/archive/summary reports.

## Task 1 Result

Confirmed PyQt helper/test files:

- `tests/helpers/pyqt_env.py`
- `tests/test_pyqt_environment_guard.py`
- `tests/test_iso16358_result_table_copy_tsv.py`
- `tests/test_iso16358_table_excel_like_behavior.py`
- `tests/test_app_calculator_ui_smoke.py`
- `tests/test_spreadsheet_table_view.py`

Known-bad condition from 129:

- `platform.system() == "Darwin"`.
- Python version series is 3.14.
- PyQt5 is importable for version detection.
- Python 3.15+ is not skipped until separately verified.
- PyQt5-unavailable hosts still use existing `pytest.importorskip("PyQt5")`.

Skip reason shape:

```text
known-bad PyQt widget test environment: Darwin Python 3.14.4 PyQt5 5.15.11 Qt 5.15.14 can native-abort during pytest QTableView subclass construction
```

Skip target files and roles:

| File | Role |
| --- | --- |
| `tests/test_iso16358_result_table_copy_tsv.py` | ISO16358 read-only result/trace table Ctrl+C TSV copy behavior. |
| `tests/test_iso16358_table_excel_like_behavior.py` | ISO16358 input table Excel-like copy, clear, undo, navigation, invalid-cell display. |
| `tests/test_app_calculator_ui_smoke.py` | Existing PyQt calculator window smoke, profile selection, and table wiring. |
| `tests/test_spreadsheet_table_view.py` | Shared `SpreadsheetTableView` copy/paste/clear/undo/navigation behavior. |

Current full suite baseline:

- `python3 -B -m pytest -q -rxXs` -> `585 passed, 59 skipped, 19 xfailed`.
- Manual PyQt `--ignore` entries are no longer required on the known-bad macOS Python 3.14 host.

## Task 2 Result

Created guide:

- `docs/guides/pyqt_test_support_matrix.md`

Included sections:

- Purpose
- Scope
- Current Baseline
- PyQt Test Groups
- Known-Bad Environment
- Supported / Pending / Skipped Host Matrix
- Local Test Commands
- How To Interpret Skipped PyQt Tests
- When To Revalidate
- Non-Goals

Support matrix documented:

| Host | Policy |
| --- | --- |
| macOS arm64 + Python 3.14.x + PyQt5 | Known-bad; PyQt widget tests skipped. |
| macOS + Python 3.12/3.11 + PyQt5 | Pending validation. |
| Windows + Python 3.12/3.11 + PyQt5 | Pending validation / preferred future validation host. |
| Linux + Python 3.14 + PyQt5 | Not classified as known-bad by the current guard. |
| No PyQt5 installed | `pytest.importorskip("PyQt5")` skip. |
| Tkinter-only paths | Unaffected. |

Pending validation items:

- Python 3.12/3.11 venv PyQt widget test run.
- Windows PyQt widget test run.
- Future PyQt5/Qt/Python version changes, including Python 3.15+ if used.

The guide explicitly states that PyQt test skips are not deletion/retirement and are separate from the Tkinter calculator-only direction.

## Task 3 Result

Updated `docs/WORK_PLAN.md` narrowly:

- Recorded the new PyQt test support matrix guide.
- Kept PyQt calculator deployment hold state unchanged.
- Kept Windows PyInstaller size measurement pending until a Windows host is available.
- Kept remaining xfail count at 19.

Next recommended actions:

1. Python 3.12/3.11 venv PyQt support validation.
2. Windows PyInstaller size measurement when a Windows host is available.
3. Tkinter next metric/standard extension design, if needed.
4. ML / inverse-search return prep.

## Task 4 Result

Verification:

- `python3 -B tools/check_code_structure.py` -> `code structure guard: OK (no findings)`.
- `python3 -B -m pytest tests/test_pyqt_environment_guard.py -q` -> `11 passed`.
- `python3 -B -m pytest -q -rxXs` -> `585 passed, 59 skipped, 19 xfailed`.

Lifecycle maintenance:

- Not performed. This task creates one active report and does not summarize/archive active reports.
- Active reports are now 124-131, eight active reports total.
- Next work before or after the following active report should consider result report lifecycle maintenance.

## Changed Files

- `docs/guides/pyqt_test_support_matrix.md`
- `docs/WORK_PLAN.md`
- `result_reports/active/131_pyqt-test-support-matrix-doc.md`

## Residual Risk

- Python 3.12/3.11 and Windows PyQt support remain pending validation.
- The exact Qt native abort root cause is still unresolved; the current policy prevents the known-bad local host from executing risky widget tests.
