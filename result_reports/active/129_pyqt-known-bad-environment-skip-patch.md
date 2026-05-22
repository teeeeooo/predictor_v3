# 129 PyQt Known-Bad Environment Skip Patch

## Goal

Prevent native aborts from PyQt widget tests on the known-bad macOS + Python 3.14 + PyQt5 environment while keeping the PyQt tests available on other supported hosts.

## Scope

- `tests/helpers/pyqt_env.py`
- `tests/test_pyqt_environment_guard.py`
- `tests/test_iso16358_result_table_copy_tsv.py`
- `tests/test_iso16358_table_excel_like_behavior.py`
- `tests/test_app_calculator_ui_smoke.py`
- `tests/test_spreadsheet_table_view.py`
- `docs/WORK_PLAN.md`

## Non-Goals

- Delete PyQt tests.
- Convert PyQt tests to xfail.
- Modify PyQt UI code.
- Modify Tkinter code.
- Change test bodies, assertions, expected values, fixtures, core calculator code, profile/dispatcher code, CI, pre-commit, devcontainer, or PyInstaller behavior.
- Perform result report lifecycle maintenance.

## Task 1 Result

Skip target files:

- `tests/test_iso16358_result_table_copy_tsv.py`
- `tests/test_iso16358_table_excel_like_behavior.py`
- `tests/test_app_calculator_ui_smoke.py`
- `tests/test_spreadsheet_table_view.py`

Risky widget construction points:

- `test_iso16358_result_table_copy_tsv.py`: `TwoPointTableView`, `ReadOnlyCopyTableView`, and `RegionDetailTab.table` paths.
- `test_iso16358_table_excel_like_behavior.py`: `ProfileInputGridView` construction in `_make_view_with_points`.
- `test_app_calculator_ui_smoke.py`: `CalculatorWindow` and embedded table widgets.
- `test_spreadsheet_table_view.py`: `SpreadsheetTableView` plus `QTest` key-event paths.

Existing import policy:

- Each file already used `pytest.importorskip("PyQt5")`.
- That behavior was preserved, so PyQt5-less environments still skip normally.
- The new known-bad guard runs after `pytest.importorskip("PyQt5")` and before test body widget construction.

Known-bad condition:

- `platform.system() == "Darwin"`.
- Python version is exactly the 3.14 series.
- PyQt5 is importable for version detection.
- Python 3.15+ is not skipped by this patch because it is not verified; the condition can be extended only after evidence.

## Task 2 Result

Added helper:

- `tests/helpers/pyqt_env.py`

Public interface:

- `PyQtEnvironment`
- `current_pyqt_environment() -> PyQtEnvironment`
- `is_macos_python314_pyqt5_known_bad(env: PyQtEnvironment | None = None) -> bool`
- `describe_pyqt_environment(env: PyQtEnvironment | None = None) -> str`
- `macos_python314_pyqt5_known_bad_skip_mark()`
- `skip_if_macos_python314_pyqt5_known_bad() -> None`

Implementation notes:

- The helper imports `PyQt5.QtCore` only to read `PYQT_VERSION_STR` and `QT_VERSION_STR`.
- It does not create `QApplication`, `QTableView`, clipboard objects, or any widget.
- It does not call platform-specific shell commands.
- If PyQt5 import fails, the helper reports PyQt unavailable and does not classify the environment as known-bad.

Skip reason example:

```text
known-bad PyQt widget test environment: Darwin Python 3.14.4 PyQt5 5.15.11 Qt 5.15.14 can native-abort during pytest QTableView subclass construction
```

## Task 3 Result

Applied `pytestmark = pytest.mark.skipif(...)` to all four PyQt widget test files.

Application point:

- After existing `pytest.importorskip("PyQt5")`.
- Before test body execution and before any `QApplication` / widget construction.

Why `pytestmark` instead of module-level `pytest.skip`:

- A first implementation using module-level `pytest.skip(..., allow_module_level=True)` prevented the native abort but returned pytest exit code 5 when only the four skipped modules were targeted.
- `pytestmark = skipif(...)` keeps tests collected and skipped, so targeted validation exits successfully.

Unchanged:

- Test bodies.
- Assertions.
- Expected values.
- Fixtures.
- PyQt UI behavior.
- xfail markers.
- PyQt test files remain present.

Other environments:

- Windows, Linux, and macOS Python 3.12/3.11 do not match the helper condition and can still run the PyQt widget tests if PyQt5 is installed.
- Python 3.15+ is not skipped until separately verified.

## Task 4 Result

Added helper tests:

- `tests/test_pyqt_environment_guard.py`

Monkeypatch/pure detection coverage:

- macOS + Python 3.14 + PyQt5 available -> known-bad true.
- macOS + Python 3.12 -> false.
- Windows + Python 3.14 -> false.
- Linux + Python 3.14 -> false.
- macOS + Python 3.15 -> false until verified.
- PyQt5 unavailable -> false and no crash.
- `describe_pyqt_environment` includes system, Python, PyQt5, and Qt versions when available.
- `macos_python314_pyqt5_known_bad_skip_mark` returns a `skipif` marker with the known-bad reason.
- `skip_if_macos_python314_pyqt5_known_bad` raises pytest skip on known-bad and no-ops on supported host.

The helper tests do not create `QApplication`, `QTableView`, clipboard objects, or widgets.

## Task 5 Result

`docs/WORK_PLAN.md` was updated narrowly:

- Marked the PyQt known-bad environment skip patch complete.
- Recorded that manual PyQt ignore is no longer needed on this known-bad host because the full suite now skips the four PyQt widget files safely.
- Kept remaining xfail count at 19.
- Kept Windows PyInstaller size measurement pending until a Windows host is available.

Next recommended actions:

1. Python 3.12/3.11 venv PyQt support validation.
2. PyQt test support matrix documentation.
3. Windows PyInstaller size measurement when a Windows host is available.
4. Tkinter ISO section pure helper cleanup, if needed.

Lifecycle maintenance was not performed because this task creates one active report and does not summarize/archive active reports.

## Task 6 Result

Verification commands:

- `python3 -B tools/check_code_structure.py` -> `code structure guard: OK (no findings)`.
- `python3 -B -m py_compile tests/helpers/pyqt_env.py tests/test_pyqt_environment_guard.py` -> pass.
- `python3 -B -m pytest tests/test_pyqt_environment_guard.py -q` -> `11 passed`.
- `python3 -B -m pytest tests/test_iso16358_result_table_copy_tsv.py tests/test_iso16358_table_excel_like_behavior.py tests/test_app_calculator_ui_smoke.py tests/test_spreadsheet_table_view.py -q -rs` -> `58 skipped`, exit code 0, no native abort.
- `python3 -B -m pytest -q -rxXs` -> `579 passed, 59 skipped, 19 xfailed`, no native abort.

Remaining xfail count:

- 19 xfailed.

Native abort status:

- No native abort occurred after the patch in targeted PyQt validation or full suite validation without manual PyQt ignores.

## Changed Files

- `tests/helpers/pyqt_env.py`
- `tests/test_pyqt_environment_guard.py`
- `tests/test_iso16358_result_table_copy_tsv.py`
- `tests/test_iso16358_table_excel_like_behavior.py`
- `tests/test_app_calculator_ui_smoke.py`
- `tests/test_spreadsheet_table_view.py`
- `docs/WORK_PLAN.md`
- `result_reports/active/129_pyqt-known-bad-environment-skip-patch.md`

## Residual Risk

- The exact Qt native cause remains unresolved; this patch only prevents known-bad host execution before risky widget construction.
- Python 3.12/3.11 and Windows PyQt behavior still need explicit validation.
- Python 3.15+ is intentionally not skipped until separately verified.
