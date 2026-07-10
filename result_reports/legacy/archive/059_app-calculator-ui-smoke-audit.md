# 059 App Calculator UI Smoke Audit

## Goal

Audit `app_calculator.py` / `ui/calc_window.py` runtime interaction enough to avoid moving into ML/inverse-search with an unverified calculator UI boundary.

## Scope

- `app_calculator.py` import/launch path
- `ui/calc_window.py` `CalculatorWindow` instantiation path
- PyQt offscreen smoke coverage

## Non-goals

- No calculator core changes.
- No UI redesign.
- No ML connection or result-envelope implementation.

## Changed Files

- `tests/test_app_calculator_ui_smoke.py`
- `result_reports/active/059_app-calculator-ui-smoke-audit.md`

## Verification

- PyQt check: `PyQt5: available`; no install was needed.
- `QT_QPA_PLATFORM=offscreen python3 -B -m pytest tests/test_app_calculator_ui_smoke.py -q`
  - `1 passed`
- `python3 -B -m py_compile app_calculator.py ui/calc_window.py`
  - passed
- `rg -n "QPushButton|clicked|setText|on_calculate|calculate_ahri\\(|calculate_en\\(" ui/calc_window.py`
  - found `on_calculate()`, `calculate_ahri()`, and `calculate_en()`
  - did not find a `QPushButton`, `.clicked` connection, or result-label `.setText()` path in `ui/calc_window.py`

## Task Results

- Added an offscreen PyQt smoke test that instantiates `CalculatorWindow`, verifies the three main tabs, and confirms the AHRI combo is populated at launch.
- The first smoke attempt aborted because the test did not hold a Python reference to the `QApplication` wrapper. The test now stores the application reference before constructing `CalculatorWindow`.
- Runtime launch smoke is now covered, but the interaction audit still shows no visible calculate button/result-display connection in `ui/calc_window.py`.

## Known Risks

- The smoke test proves the window can instantiate offscreen; it does not prove that a user can trigger `on_calculate()` from the current UI.
- Since no button/result display path was found, calculator UI usability remains a follow-up UI task rather than something fixed in this audit step.

## Commit / Push

- Source commit: `f17f8da` (`test: add calculator UI launch smoke`).
- Report commit: this commit (`report: record app calculator UI smoke audit`).
- Push: deferred until final objective push.
