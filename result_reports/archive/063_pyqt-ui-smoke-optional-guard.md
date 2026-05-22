# 063 PyQt UI Smoke Optional Guard

## Goal

Make the Calculator UI smoke test safe to collect in environments where PyQt5 is not installed.

## Scope

- `tests/test_app_calculator_ui_smoke.py`

## Non-goals

- No UI code changes.
- No PyQt installation script.
- No calculator core changes.

## Changed Files

- `tests/test_app_calculator_ui_smoke.py`
- `result_reports/active/063_pyqt-ui-smoke-optional-guard.md`

## Verification

- `python3 -B -m py_compile tests/test_app_calculator_ui_smoke.py`
  - passed
- `QT_QPA_PLATFORM=offscreen python3 -B -m pytest tests/test_app_calculator_ui_smoke.py -q`
  - `2 passed`

## Task Results

- Added `pytest.importorskip("PyQt5")` before importing PyQt widgets.
- PyQt-installed environments still run the existing offscreen UI smoke.
- PyQt-missing environments should skip this test module during collection instead of failing the full test suite with `ModuleNotFoundError`.

## Known Risks

- The current environment has PyQt5 installed, so PyQt-missing behavior was verified by code path inspection rather than by uninstalling PyQt.

## Commit / Push

- Source commit: `9dbf6cf` (`test: skip calculator UI smoke without PyQt`).
- Report commit: this commit (`report: record PyQt UI smoke optional guard`).
- Push: deferred until final objective push.
