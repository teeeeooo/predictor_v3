# 128 PyQt macOS Fatal-Abort Environment Audit

## Goal

Audit the four PyQt test files currently excluded from the local full-ish suite because they can trigger native aborts on the current macOS + Python 3.14.4 + PyQt5 environment, then recommend an environment-handling policy without modifying tests or PyQt code.

## Scope

- `tests/test_iso16358_result_table_copy_tsv.py`
- `tests/test_iso16358_table_excel_like_behavior.py`
- `tests/test_app_calculator_ui_smoke.py`
- `tests/test_spreadsheet_table_view.py`
- pytest/conftest configuration lookup
- `docs/WORK_PLAN.md`
- Prior context from reports 116, 118, and summary 123

## Non-Goals

- Modify tests.
- Add skip or xfail markers.
- Modify PyQt UI code.
- Modify Tkinter code.
- Delete PyQt tests.
- Add CI, pre-commit, devcontainer, or PyInstaller changes.
- Perform result report lifecycle maintenance.

## Task 1 Result

Target file inventory:

| File | Role | PyQt surface | Current skip/import policy | Preservation value |
| --- | --- | --- | --- | --- |
| `tests/test_iso16358_result_table_copy_tsv.py` | ISO16358 read-only result/trace table Ctrl+C TSV copy coverage for `TwoPointTableModel`, `RegionResultTableModel`, `TraceTableModel`, and `RegionDetailTab.table`. | `QApplication`, `QTableView` subclasses, `QClipboard`. | `pytest.importorskip("PyQt5")`; `QT_QPA_PLATFORM=offscreen`. | Keep. It protects PyQt table copy behavior and historical UI/UX contract alignment even while calculator-only deployment is on Tkinter hold. |
| `tests/test_iso16358_table_excel_like_behavior.py` | ISO16358 input table Excel-like behavior: TSV copy, clear, undo, navigation, invalid-cell display. | `QApplication`, `ProfileInputGridView`, `QBrush`, clipboard. | `pytest.importorskip("PyQt5")`; `QT_QPA_PLATFORM=offscreen`. | Keep. It protects PyQt table UX contract behavior. |
| `tests/test_app_calculator_ui_smoke.py` | PyQt calculator window smoke and profile/table wiring for ISO/EN/AHRI surfaces. | `QApplication`, `CalculatorWindow`, `SpreadsheetTableView`, widgets. | `pytest.importorskip("PyQt5")`; `QT_QPA_PLATFORM=offscreen`. | Keep. PyQt calculator UI is on deployment hold, not deleted; Predict/Train PyQt remains possible. |
| `tests/test_spreadsheet_table_view.py` | Shared `SpreadsheetTableView` copy/paste/clear/undo/navigation behavior. | `QApplication`, `SpreadsheetTableView`, `QTest` key events. | `pytest.importorskip("PyQt5")`; `QT_QPA_PLATFORM=offscreen`. | Keep. It protects a shared PyQt table component used by current PyQt assets. |

Configuration check:

- No repo `conftest.py` or `tests/conftest.py` was found by `rg --files`.
- No `pytest.ini`, `pyproject.toml`, `setup.cfg`, or `tox.ini` pytest configuration file was found by the targeted lookup.
- Current policy is local per-file `pytest.importorskip("PyQt5")` plus `QT_QPA_PLATFORM=offscreen`; there is no environment marker for macOS + Python 3.14 + PyQt5 fatal-abort risk.

Prior context:

- Report 116 recorded full pytest crashing on the same four PyQt files on macOS + Python 3.14 + PyQt5, then used a full-ish baseline excluding them.
- Report 118 carried the same known-failure separation forward while resetting Tkinter calculator structure.
- Summary 123 kept PyQt fatal-abort handling as a separate environment slice.
- `docs/WORK_PLAN.md` keeps PyQt calculator UI on hold for calculator-only deployment while Tkinter MVP is the current lightweight direction.

## Task 2 Result

Environment:

- `python3 --version` -> `Python 3.14.4`
- `uname -a && sw_vers` -> macOS 15.7.3, Darwin 24.6.0, arm64.
- PyQt version command:
  - `PyQt5 5.15.11 Qt 5.15.14`

Stage checks:

| Stage | Command / check | Result |
| --- | --- | --- |
| PyQt5 import | `import PyQt5.QtCore as QtCore` | Pass |
| offscreen `QApplication` creation | script importing `QApplication`, then `QApplication([])` | Pass |
| plain `QTableView` creation | script with `QTableView()` | Pass |
| `TwoPointTableView` direct script creation | script with `TwoPointTableView()` | Pass |
| `test_iso16358_result_table_copy_tsv.py` representative pytest test | `python3 -B -m pytest tests/test_iso16358_result_table_copy_tsv.py::test_two_point_table_copy_tsv_via_clipboard -q` | Native abort, exit code -1 |
| `test_iso16358_table_excel_like_behavior.py` representative single test | `python3 -B -m pytest tests/test_iso16358_table_excel_like_behavior.py::test_copy_selection_puts_tsv_on_clipboard -q` | Pass in this isolated single-test run |
| `test_spreadsheet_table_view.py` representative single test | `python3 -B -m pytest tests/test_spreadsheet_table_view.py::test_copy_selection_tsv_returns_selected_rectangle -q` | Pass |
| `test_app_calculator_ui_smoke.py` representative single test | `python3 -B -m pytest tests/test_app_calculator_ui_smoke.py::test_calculator_window_instantiates_offscreen -q` | Pass |
| `test_iso16358_table_excel_like_behavior.py` file run | `python3 -B -m pytest tests/test_iso16358_table_excel_like_behavior.py -q` | Native abort, exit code -1 |
| `test_spreadsheet_table_view.py` file run | `python3 -B -m pytest tests/test_spreadsheet_table_view.py -q` | `8 passed` |
| `test_app_calculator_ui_smoke.py` file run | `python3 -B -m pytest tests/test_app_calculator_ui_smoke.py -q` | `20 passed` |

Crash classification:

- The crash is not a Python exception; it is a native SIGABRT / `Fatal Python error: Aborted`.
- The stack for `test_iso16358_result_table_copy_tsv.py::test_two_point_table_copy_tsv_via_clipboard` points to line 60, `view = TwoPointTableView()`, with the C stack inside Qt `QTableView` construction.
- The stack for `tests/test_iso16358_table_excel_like_behavior.py` file execution points to `ui/calculators_2point.py:943`, `ProfileInputGridView.__init__ -> super().__init__()`, again inside `QTableView` construction.
- Clipboard access is not proven to be the first failing stage for these reproductions; the reproduced aborts happen before clipboard assertions.
- The issue is environment-sensitive and test-run-context-sensitive: direct script creation of `QTableView` and `TwoPointTableView` passed, while pytest execution of the affected widget tests aborted.
- Repeated crash probing was stopped after confirming two native aborts to avoid unnecessary native crash repetition.

## Task 3 Result

Policy candidates:

| Candidate | Pros | Cons | Judgment |
| --- | --- | --- | --- |
| macOS + Python 3.14 + PyQt5-only skip guard | Keeps PyQt tests active elsewhere; stops native aborts in known-bad local environment; small future patch. | Needs careful environment detection before PyQt widget creation; may hide a real regression if detection is too broad. | Recommended core policy. |
| PyQt tests opt-in marker | Makes local default suite stable and explicit; useful if PyQt support matrix remains broad. | Too broad for current evidence; would unnecessarily remove PyQt coverage from environments that can run it. | Useful as a supplemental marker, not the first patch alone. |
| PyQt clipboard/table tests only environment marker | Narrower than all PyQt; targets current crash class. | `test_app_calculator_ui_smoke.py` also instantiates many PyQt widgets and was historically part of the excluded set. | Good implementation shape if marker covers PyQt widget-host tests. |
| Keep local full-ish ignore only | Zero code change; already works. | Keeps the native crash footgun and requires every runner to remember four ignores. | Not sufficient as long-term policy. |
| Support PyQt tests only on Python 3.12/3.11 venv | Likely reduces Python 3.14 compatibility risk; clear support matrix. | Needs actual verification; cannot be asserted from this audit alone. | Good follow-up validation. |
| Run PyQt tests only on Windows/CI host | Aligns with future Windows packaging/smoke needs. | Current repo has no CI policy here; macOS developers still need clear local behavior. | Good later support matrix entry, not enough alone. |

Recommended policy:

- Do not delete or retire the PyQt tests.
- Add a small future environment-handling patch that skips/marks PyQt widget tests on the known-bad macOS + Python 3.14 + PyQt5 combination before risky widget construction.
- Keep the tests runnable on supported PyQt hosts, especially a Python 3.12/3.11 venv or Windows host once verified.
- Document the support matrix so local full-ish ignores are no longer the only way to avoid native aborts.

This keeps Tkinter calculator-only direction separate from PyQt test environment handling. PyQt calculator deployment remains on hold, but PyQt assets and table UX tests still have value and should not be deleted.

## Task 4 Result

Follow-up patch slices:

### 1. PyQt Fatal-Abort Environment Marker/Skip Patch

- **Purpose**: Prevent native abort on macOS + Python 3.14 + PyQt5 while preserving PyQt tests elsewhere.
- **Target files**: likely a small helper in tests infrastructure or per-file top-of-file guard for the four PyQt widget test files.
- **Include**: environment detection before widget construction; marker/skip reason that names macOS + Python 3.14 + PyQt5 native abort risk.
- **Exclude**: PyQt code changes, test deletion, xfail conversion, expected/fixture/core changes.
- **Prerequisite**: decide whether to centralize in a helper or per-file guard.
- **Verification**: affected tests should skip in the known-bad environment; full-ish suite should no longer need manual ignores for these files on this host.

### 2. PyQt Test Support Matrix Documentation

- **Purpose**: State which hosts should run PyQt widget tests and which hosts skip them.
- **Target files**: a guide or WORK_PLAN-adjacent docs section, depending on the next task scope.
- **Include**: macOS Python 3.14 known-bad status, Python 3.12/3.11 validation pending, Windows host validation pending.
- **Exclude**: CI implementation.
- **Prerequisite**: patch policy decision from slice 1.
- **Verification**: docs-only review plus code structure guard.

### 3. macOS Python 3.14 PyQt Known Issue Guide

- **Purpose**: Give local developers a concise explanation and reproduction command for the native abort.
- **Target files**: docs/guides if a separate guide is warranted.
- **Include**: environment tuple, failing commands, full-ish baseline command.
- **Exclude**: broad PyQt troubleshooting rewrite.
- **Prerequisite**: optional; can be combined with support matrix docs if kept short.
- **Verification**: docs-only review.

### 4. Python 3.12 venv PyQt Smoke Reverification

- **Purpose**: Confirm whether PyQt widget tests should be supported on Python 3.12/3.11 locally.
- **Target files**: none unless a follow-up report is required.
- **Include**: create/use a Python 3.12 venv, install current dependencies, run the four PyQt files and full suite.
- **Exclude**: dependency upgrades, PyQt code changes, CI changes.
- **Prerequisite**: Python 3.12 or 3.11 interpreter available.
- **Verification**: four PyQt files, full-ish suite, and code structure guard.

Recommended next action:

1. Implement the PyQt fatal-abort environment marker/skip patch for known-bad macOS + Python 3.14 + PyQt5, with the smallest possible guard and no PyQt behavior changes.

## Task 5 Result

`docs/WORK_PLAN.md` was updated narrowly:

- Added PyQt macOS fatal-abort environment audit status.
- Recorded the current environment tuple and reproduced crash class.
- Kept PyQt tests as preserved assets, not deletion candidates.
- Recorded next action as a future environment marker/skip patch plus support matrix / Python 3.12 or Windows validation.
- Kept Windows PyInstaller size measurement pending until a Windows host is available.
- Kept remaining xfail count unchanged at 19.

Lifecycle maintenance was not performed because this task creates a single active audit report and does not summarize/archive active reports.

Verification:

- `python3 -B tools/check_code_structure.py` -> `code structure guard: OK (no findings)`.
- `python3 --version` -> `Python 3.14.4`.
- PyQt version check -> `PyQt5 5.15.11 Qt 5.15.14`.
- Full-ish baseline:
  - `python3 -B -m pytest -q -rxX --ignore=tests/test_iso16358_result_table_copy_tsv.py --ignore=tests/test_iso16358_table_excel_like_behavior.py --ignore=tests/test_app_calculator_ui_smoke.py --ignore=tests/test_spreadsheet_table_view.py`
  - Result: `568 passed, 1 skipped, 19 xfailed`.

## Changed Files

- `docs/WORK_PLAN.md`
- `result_reports/active/128_pyqt-macos-fatal-abort-environment-audit.md`

## Residual Risk

- The exact Qt native cause is not proven. Evidence points to `QTableView` subclass construction under pytest on this macOS/Python/PyQt tuple, but direct script construction can pass.
- `test_spreadsheet_table_view.py` and `test_app_calculator_ui_smoke.py` passed in this audit's individual file runs, but they remain in the historical fatal-abort exclusion set and should be handled by the same environment policy until a supported-host matrix is verified.
- No Windows or Python 3.12/3.11 validation was performed in this task.
